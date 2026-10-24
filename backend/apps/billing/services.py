import io
import qrcode
from decimal import Decimal, ROUND_HALF_UP
from django.db import transaction
from django.utils import timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from .models import Sale, SaleItem, Payment
from apps.stock.services import record_stock_movement
from apps.stock.models import StockMovement


def _next_invoice_number(branch):
    prefix = 'SK'
    if branch:
        prefix = branch.name[:2].upper()
    year_month = timezone.localdate().strftime('%y%m')
    last = Sale.objects.filter(invoice_number__startswith=f'{prefix}{year_month}').order_by('-id').first()
    if last:
        try:
            seq = int(last.invoice_number[-4:]) + 1
        except ValueError:
            seq = 1
    else:
        seq = 1
    return f"{prefix}{year_month}{seq:04d}"


def create_sale(user, items_data, payment_data, customer=None, discount=0, notes='', old_gold_weight=0, old_gold_rate=0):
    """
    Atomic sale creation:
    - Creates Sale + SaleItems
    - Records stock OUT movements
    - Calculates GST (3% jewellery)
    - Creates Payment record(s)
    - Returns Sale instance
    """
    with transaction.atomic():
        from apps.accounting.models import GoldRate
        branch = user.branch

        # Get current gold rate (fallback to provided rate in items)
        sale = Sale.objects.create(
            invoice_number=_next_invoice_number(branch),
            customer=customer,
            branch=branch,
            created_by=user,
            gold_rate_per_gram=Decimal('0'),  # will update after items
            notes=notes,
        )

        subtotal = Decimal('0')
        total_gst = Decimal('0')
        total_making = Decimal('0')

        for item_data in items_data:
            product = item_data['product']
            qty = item_data.get('quantity', 1)
            gold_rate = Decimal(str(item_data['gold_rate_per_gram']))
            making = Decimal(str(item_data.get('making_charge', '0')))
            stone = Decimal(str(item_data.get('stone_charge', '0')))
            gst_rate = Decimal('3.00')

            net_wt = product.net_weight
            gold_value = (net_wt * gold_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            unit_price = (gold_value + making + stone).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            item_total = unit_price * qty
            gst_on_item = (item_total * gst_rate / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=qty,
                product_name=product.name,
                sku=product.sku,
                purity=product.purity.name,
                gross_weight=product.gross_weight,
                net_weight=net_wt,
                gold_rate_per_gram=gold_rate,
                making_charge=making,
                stone_charge=stone,
                unit_price=unit_price,
                total_price=item_total,
                hsn_code=product.hsn_code or '7113',
                gst_rate=gst_rate,
            )

            # Stock OUT
            record_stock_movement(
                product=product,
                movement_type=StockMovement.MovementType.OUT,
                quantity=qty,
                reference_type='sale',
                reference_id=sale.id,
                user=user,
                branch=branch,
            )

            subtotal += item_total
            total_gst += gst_on_item

        # Old gold exchange value
        old_gold_val = (Decimal(str(old_gold_weight)) * Decimal(str(old_gold_rate))).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        ) if old_gold_weight and old_gold_rate else Decimal('0')

        cgst = (total_gst / 2).quantize(Decimal('0.01'))
        sgst = (total_gst / 2).quantize(Decimal('0.01'))
        disc = Decimal(str(discount)).quantize(Decimal('0.01'))
        total = (subtotal + total_gst - disc).quantize(Decimal('0.01'))
        amount_paid = Decimal(str(payment_data.get('amount', '0')))
        balance = (total - amount_paid - old_gold_val).quantize(Decimal('0.01'))

        # Update sale
        sale.gold_rate_per_gram = Decimal(str(items_data[0]['gold_rate_per_gram'])) if items_data else Decimal('0')
        sale.subtotal = subtotal
        sale.discount = disc
        sale.cgst_amount = cgst
        sale.sgst_amount = sgst
        sale.total_amount = total
        sale.old_gold_value = old_gold_val
        sale.amount_paid = amount_paid + old_gold_val
        sale.balance_due = max(balance, Decimal('0'))
        sale.payment_status = (
            Sale.PaymentStatus.PAID if balance <= 0
            else Sale.PaymentStatus.PARTIAL if amount_paid > 0
            else Sale.PaymentStatus.PENDING
        )
        sale.save()

        # Create payment record
        Payment.objects.create(
            sale=sale,
            method=payment_data.get('method', 'cash'),
            amount=amount_paid,
            reference=payment_data.get('reference', ''),
        )

        return sale


def generate_invoice_pdf(sale):
    """Generate PDF invoice. Returns bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm,
                             topMargin=20*mm, bottomMargin=20*mm)
    styles = getSampleStyleSheet()
    story = []

    # Header
    branch = sale.branch
    shop_name = branch.name if branch else 'Swarna Khata'
    story.append(Paragraph(f'<b>{shop_name}</b>', styles['Title']))
    if branch:
        story.append(Paragraph(branch.address, styles['Normal']))
        story.append(Paragraph(f'GSTIN: {branch.gstin}', styles['Normal']))
    story.append(Spacer(1, 6*mm))
    story.append(Paragraph(f'<b>TAX INVOICE</b>', styles['Heading2']))
    story.append(Paragraph(f'Invoice No: {sale.invoice_number}', styles['Normal']))
    story.append(Paragraph(f'Date: {sale.sale_date.strftime("%d-%m-%Y %H:%M")}', styles['Normal']))
    if sale.customer:
        story.append(Paragraph(f'Customer: {sale.customer.name} | Ph: {sale.customer.phone}', styles['Normal']))
    story.append(Spacer(1, 6*mm))

    # Items table
    headers = ['#', 'Item', 'Purity', 'Net Wt (g)', 'Rate/g', 'Making', 'Qty', 'Amount']
    rows = [headers]
    for i, item in enumerate(sale.items.all(), 1):
        rows.append([
            str(i), item.product_name, item.purity,
            str(item.net_weight), f'₹{item.gold_rate_per_gram}',
            f'₹{item.making_charge}', str(item.quantity),
            f'₹{item.total_price}'
        ])

    table = Table(rows, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2D3748')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F7FAFC')]),
    ]))
    story.append(table)
    story.append(Spacer(1, 6*mm))

    # Totals
    totals = [
        ['Subtotal', f'₹{sale.subtotal}'],
        ['Discount', f'-₹{sale.discount}'],
        ['CGST (1.5%)', f'₹{sale.cgst_amount}'],
        ['SGST (1.5%)', f'₹{sale.sgst_amount}'],
        ['Old Gold Exchange', f'-₹{sale.old_gold_value}'],
        ['TOTAL', f'₹{sale.total_amount}'],
        ['Amount Paid', f'₹{sale.amount_paid}'],
        ['Balance Due', f'₹{sale.balance_due}'],
    ]
    tot_table = Table(totals, colWidths=[100, 100])
    tot_table.setStyle(TableStyle([
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, -3), (-1, -3), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('LINEABOVE', (0, -3), (-1, -3), 1, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
    ]))
    story.append(tot_table)
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph('Thank you for your purchase!', styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


async def generate_invoice_pdf_async(sale):
    """
    Asynchronously generates an invoice PDF by delegating CPU-bound
    ReportLab document building to a thread pool executor.
    Prevents event-loop starvation under high invoice traffic.
    """
    import asyncio
    return await asyncio.to_thread(generate_invoice_pdf, sale)
