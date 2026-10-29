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
    import re
    prefix = 'SK'
    if branch and branch.name:
        clean_prefix = re.sub(r'[^A-Z0-9]', '', branch.name.upper())[:2]
        if clean_prefix:
            prefix = clean_prefix
    year_month = timezone.localdate().strftime('%y%m')
    pattern = f"{prefix}{year_month}"

    # Serialize concurrent invoice generation using pessimistic lock on latest sale
    last = Sale.objects.select_for_update().filter(invoice_number__startswith=pattern).order_by('-id').first()
    if last:
        try:
            seq = int(last.invoice_number[-4:]) + 1
        except ValueError:
            seq = 1
    else:
        seq = 1

    candidate = f"{pattern}{seq:04d}"
    while Sale.objects.filter(invoice_number=candidate).exists():
        seq += 1
        candidate = f"{pattern}{seq:04d}"
    return candidate


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

        # Capture immutable snapshot of shop profile & invoice settings at time of sale
        inv_setting = None
        if branch and hasattr(branch, 'invoice_setting'):
            inv_setting = branch.invoice_setting
        elif branch:
            from apps.billing.models import InvoiceSetting
            inv_setting = InvoiceSetting.objects.filter(branch=branch).first()

        shop_snapshot = {
            "shop_name_primary": inv_setting.shop_name_primary if inv_setting else (branch.name if branch else 'Swarna Khata'),
            "shop_name_secondary": inv_setting.shop_name_secondary if inv_setting else '',
            "header_invocation": inv_setting.header_invocation if inv_setting else '',
            "tagline": inv_setting.tagline if inv_setting else '',
            "address_primary": inv_setting.address_primary if inv_setting else (branch.address if branch else ''),
            "address_secondary": inv_setting.address_secondary if inv_setting else '',
            "phone_landline": inv_setting.phone_landline if inv_setting else '',
            "phone_mobile_1": inv_setting.phone_mobile_1 if inv_setting else (branch.phone if branch else ''),
            "phone_mobile_2": inv_setting.phone_mobile_2 if inv_setting else '',
            "email": inv_setting.email if inv_setting else '',
            "gstin": inv_setting.gstin if inv_setting else (branch.gstin if branch else ''),
            "pan_number": inv_setting.pan_number if inv_setting else '',
            "state_name": inv_setting.state_name if inv_setting else 'Karnataka',
            "state_code": inv_setting.state_code if inv_setting else '29',
            "bis_hallmark_licence": inv_setting.bis_hallmark_licence if inv_setting else '',
            "bank_name": inv_setting.bank_name if inv_setting else '',
            "account_name": inv_setting.account_name if inv_setting else '',
            "account_number": inv_setting.account_number if inv_setting else '',
            "ifsc_code": inv_setting.ifsc_code if inv_setting else '',
            "upi_id": inv_setting.upi_id if inv_setting else '',
            "terms_and_conditions": inv_setting.terms_and_conditions if inv_setting else '',
            "signatory_title": inv_setting.signatory_title if inv_setting else 'Authorized Signatory',
            "template_style": getattr(inv_setting, 'template_style', 'traditional_bilingual'),
            "default_paper_size": getattr(inv_setting, 'default_paper_size', 'A4'),
            "show_invocation": getattr(inv_setting, 'show_invocation', True),
            "show_bilingual_header": getattr(inv_setting, 'show_bilingual_header', True),
            "show_bank_details": getattr(inv_setting, 'show_bank_details', True),
            "show_huid": getattr(inv_setting, 'show_huid', True),
            "show_customer_address": getattr(inv_setting, 'show_customer_address', True),
            "show_hallmark_badge": getattr(inv_setting, 'show_hallmark_badge', True),
        }

        customer_snapshot = {}
        if customer:
            customer_snapshot = {
                "id": customer.id,
                "name": customer.name,
                "phone": customer.phone,
                "email": customer.email,
                "address": customer.address,
                "pan_number": customer.pan_number,
                "aadhar_last4": customer.aadhar_last4,
            }

        # Get current gold rate (fallback to provided rate in items)
        sale = Sale.objects.create(
            invoice_number=_next_invoice_number(branch),
            customer=customer,
            branch=branch,
            created_by=user,
            gold_rate_per_gram=Decimal('0'),  # will update after items
            notes=notes,
            shop_snapshot=shop_snapshot,
            customer_snapshot=customer_snapshot,
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

            # Automatically remove sold item from active shop inventory
            from apps.stock.models import StockSummary
            from apps.billing.models import Item
            summary = StockSummary.objects.filter(product=product).first()
            if not summary or summary.quantity_on_hand <= 0:
                product.is_active = False
                product.save(update_fields=['is_active', 'updated_at'])
                Item.objects.update_or_create(
                    qr_code=product.sku,
                    defaults={
                        'name': product.name,
                        'weight': product.gross_weight,
                        'status': Item.Status.SOLD,
                        'locked_by_bill': None,
                    }
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

        # Generate initial PDF fingerprint and store SHA-256 digest
        import hashlib
        pdf_bytes = generate_invoice_pdf(sale)
        sale.pdf_sha256 = hashlib.sha256(pdf_bytes).hexdigest()
        sale.save(update_fields=['pdf_sha256'])

        return sale


def generate_invoice_pdf(sale):
    """Generate high-resolution printable GST Tax Invoice PDF. Returns bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=15*mm, leftMargin=15*mm,
                             topMargin=15*mm, bottomMargin=15*mm, invariant=True)
    styles = getSampleStyleSheet()
    story = []

    # Retrieve immutable shop snapshot with graceful fallback to live relations
    snap = getattr(sale, 'shop_snapshot', None) or {}
    branch = sale.branch
    inv_setting = None
    if not snap:
        if branch and hasattr(branch, 'invoice_setting'):
            inv_setting = branch.invoice_setting
        elif branch:
            from apps.billing.models import InvoiceSetting
            inv_setting = InvoiceSetting.objects.filter(branch=branch).first()

    shop_name = snap.get('shop_name_primary') or (inv_setting.shop_name_primary if inv_setting else (branch.name if branch else 'Swarna Khata'))
    address = snap.get('address_primary') or (inv_setting.address_primary if inv_setting else (branch.address if branch else ''))
    gstin = snap.get('gstin') or (inv_setting.gstin if inv_setting else (branch.gstin if branch else ''))

    phones = []
    landline = snap.get('phone_landline') or (inv_setting.phone_landline if inv_setting else '')
    mobile_1 = snap.get('phone_mobile_1') or (inv_setting.phone_mobile_1 if inv_setting else '')
    mobile_2 = snap.get('phone_mobile_2') or (inv_setting.phone_mobile_2 if inv_setting else '')
    if landline:
        phones.append(f"Shop: {landline}")
    if mobile_1:
        phones.append(f"Cell: {mobile_1}")
    if mobile_2:
        phones.append(mobile_2)
    if not phones and branch and branch.phone:
        phones.append(f"Ph: {branch.phone}")
    phone_str = " | ".join(phones)

    # Header section
    story.append(Paragraph(f'<b><font size="14">{shop_name}</font></b>', styles['Title']))
    if address:
        story.append(Paragraph(f'<font size="8" color="#4A5568">{address}</font>', styles['Normal']))
    contact_parts = []
    if gstin:
        contact_parts.append(f"GSTIN: <b>{gstin}</b>")
    if phone_str:
        contact_parts.append(phone_str)
    email = snap.get('email') or (inv_setting.email if inv_setting else '')
    if email:
        contact_parts.append(f"Email: {email}")
    if contact_parts:
        story.append(Paragraph(f'<font size="8" color="#4A5568">{" | ".join(contact_parts)}</font>', styles['Normal']))

    story.append(Spacer(1, 4*mm))
    story.append(Paragraph('<b><font size="11">TAX INVOICE / SALE BILL</font></b>', styles['Heading3']))

    # Metadata & Customer details
    inv_date = (sale.sale_date or timezone.now()).strftime("%d/%m/%Y %I:%M %p")
    meta_info = f"<b>Invoice No:</b> {sale.invoice_number} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Date:</b> {inv_date}"
    state_name = snap.get('state_name') or (inv_setting.state_name if inv_setting else '')
    state_code = snap.get('state_code') or (inv_setting.state_code if inv_setting else '')
    if state_name:
        meta_info += f" &nbsp;&nbsp;|&nbsp;&nbsp; <b>State:</b> {state_name} ({state_code})"
    story.append(Paragraph(f'<font size="9">{meta_info}</font>', styles['Normal']))

    # Customer details (immutable snapshot with fallback to live customer)
    cust_snap = getattr(sale, 'customer_snapshot', None) or {}
    cust_name = cust_snap.get('name') or (sale.customer.name if sale.customer else None)
    cust_phone = cust_snap.get('phone') or (sale.customer.phone if sale.customer else None)
    cust_address = cust_snap.get('address') or (sale.customer.address if sale.customer else None)
    cust_pan = cust_snap.get('pan_number') or (sale.customer.pan_number if sale.customer else None)

    if cust_name:
        cust_line = f"<b>Customer:</b> {cust_name}"
        if cust_phone:
            cust_line += f" &nbsp;|&nbsp; <b>Phone:</b> {cust_phone}"
        if cust_pan:
            cust_line += f" &nbsp;|&nbsp; <b>PAN:</b> {cust_pan}"
        if cust_address:
            cust_line += f" &nbsp;|&nbsp; <b>Address:</b> {cust_address}"
        story.append(Paragraph(f'<font size="8">{cust_line}</font>', styles['Normal']))

    story.append(Spacer(1, 4*mm))

    # Items table
    headers = ['#', 'Description', 'Purity', 'Gross Wt', 'Net Wt', 'Rate/g', 'Making', 'HSN', 'Amount']
    rows = [headers]
    for i, item in enumerate(sale.items.all(), 1):
        desc = item.product_name
        if hasattr(item, 'huid') and item.huid:
            desc += f"\nHUID: {item.huid}"
        rows.append([
            str(i),
            desc,
            item.purity,
            f"{item.gross_weight}g",
            f"{item.net_weight}g",
            f"Rs. {item.gold_rate_per_gram}",
            f"Rs. {item.making_charge}",
            item.hsn_code or '7113',
            f"Rs. {item.total_price}"
        ])

    if len(rows) == 1:
        rows.append(['1', 'Jewellery Item', '22KT', '-', '-', '-', '-', '7113', f'Rs. {sale.total_amount}'])

    table = Table(rows, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')]),
    ]))
    story.append(table)
    story.append(Spacer(1, 4*mm))

    # Totals table
    totals = [
        ['Taxable Total Value:', f'Rs. {sale.subtotal}'],
        ['Discount:', f'-Rs. {sale.discount}'],
        ['CGST @ 1.5%:', f'Rs. {sale.cgst_amount}'],
        ['SGST @ 1.5%:', f'Rs. {sale.sgst_amount}'],
    ]
    if sale.old_gold_value > 0:
        totals.append(['Old Gold Exchange Deduction:', f'-Rs. {sale.old_gold_value}'])
    totals.extend([
        ['GRAND TOTAL:', f'Rs. {sale.total_amount}'],
        ['Amount Paid:', f'Rs. {sale.amount_paid}'],
        ['Balance Due:', f'Rs. {sale.balance_due}'],
    ])

    tot_table = Table(totals, colWidths=[120, 80])
    tot_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, -3), (-1, -3), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('LINEABOVE', (0, -3), (-1, -3), 1, colors.HexColor('#0F172A')),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
    ]))
    story.append(tot_table)
    story.append(Spacer(1, 5*mm))

    # Terms & Signatures
    terms_text = snap.get('terms_and_conditions') or (inv_setting.terms_and_conditions if inv_setting else "Exchange within 3 days. No guarantee for stone falling.")
    cleaned_terms = "<br/>".join([line.strip() for line in terms_text.splitlines() if line.strip()])
    story.append(Paragraph(f'<b><font size="7">Terms & Conditions:</font></b><br/><font size="6" color="#64748B">{cleaned_terms}</font>', styles['Normal']))

    story.append(Spacer(1, 6*mm))
    signatory = snap.get('signatory_title') or (inv_setting.signatory_title if inv_setting else f"For, {shop_name}")
    sign_table = Table([
        ['Customer Signature', f'{signatory}\n\nAuthorized Signatory']
    ], colWidths=[150, 150])
    sign_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))
    story.append(sign_table)

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
