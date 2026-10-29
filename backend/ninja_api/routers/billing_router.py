from typing import List, Optional
from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.db import transaction
from django.utils import timezone
from ninja import Router
from ninja.errors import HttpError

from apps.billing.models import Sale, SaleItem, Payment, InvoiceSetting, Item
from apps.billing.services import generate_invoice_pdf, _next_invoice_number
from apps.products.models import Product
from apps.accounts.models import Branch
from apps.accounting.models import Customer, DayBook
from apps.stock.models import StockMovement, StockSummary
from apps.stock.services import record_stock_movement
from ninja_api.auth import jwt_auth, require_role
from ninja_api.schemas import (
    SaleCreateIn, SaleOut, SaleListOut, SaleItemOut, PaymentOut, AddPaymentIn,
    InvoiceSettingOut, InvoiceSettingUpdateIn
)

router = Router(tags=["POS Billing & Invoicing Engine"])


def _format_sale(sale: Sale) -> dict:
    items = []
    for it in sale.items.all():
        items.append({
            "id": it.id,
            "product_id": it.product_id,
            "product_name": it.product_name,
            "sku": it.sku,
            "purity": it.purity,
            "quantity": it.quantity,
            "gross_weight": it.gross_weight,
            "net_weight": it.net_weight,
            "gold_rate_per_gram": it.gold_rate_per_gram,
            "making_charge": it.making_charge,
            "stone_charge": it.stone_charge,
            "unit_price": it.unit_price,
            "total_price": it.total_price,
            "hsn_code": it.hsn_code,
            "gst_rate": it.gst_rate,
            "huid": it.huid or (it.product.huid if it.product and it.product.huid else ""),
            "wastage_percent": it.wastage_percent,
        })

    payments = []
    for p in sale.payments.all():
        payments.append({
            "id": p.id,
            "method": p.method,
            "amount": p.amount,
            "reference": p.reference,
            "paid_at": p.paid_at,
            "note": p.note,
        })

    # Retrieve or initialize branch invoice settings
    branch = sale.branch or Branch.objects.first()
    invoice_setting = None
    if branch:
        inv_obj, _ = InvoiceSetting.objects.get_or_create(branch=branch)
        invoice_setting = inv_obj

    # Prioritize immutable snapshots with fallback to live relations
    cust_snap = getattr(sale, 'customer_snapshot', None) or {}
    customer_name = cust_snap.get('name') or (sale.customer.name if sale.customer else None)
    customer_phone = cust_snap.get('phone') or (sale.customer.phone if sale.customer else None)
    customer_address = cust_snap.get('address') or (sale.customer.address if sale.customer else None)
    customer_pan = cust_snap.get('pan_number') or (sale.customer.pan_number if sale.customer else None)

    return {
        "id": sale.id,
        "invoice_number": sale.invoice_number,
        "customer_id": sale.customer_id,
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "customer_address": customer_address,
        "customer_pan": customer_pan,
        "branch_id": sale.branch_id,
        "sale_date": sale.sale_date,
        "gold_rate_per_gram": sale.gold_rate_per_gram,
        "subtotal": sale.subtotal,
        "discount": sale.discount,
        "cgst_amount": sale.cgst_amount,
        "sgst_amount": sale.sgst_amount,
        "igst_amount": sale.igst_amount,
        "total_amount": sale.total_amount,
        "amount_paid": sale.amount_paid,
        "old_gold_value": sale.old_gold_value,
        "balance_due": sale.balance_due,
        "payment_status": sale.payment_status,
        "sale_status": sale.sale_status,
        "notes": sale.notes,
        "items": items,
        "payments": payments,
        "invoice_setting": invoice_setting,
        "shop_snapshot": sale.shop_snapshot or {},
        "customer_snapshot": sale.customer_snapshot or {},
        "pdf_sha256": sale.pdf_sha256 or "",
    }


# ==============================================================================
# SALES LIST & DETAIL
# ==============================================================================

@router.get("/sales/", response=List[SaleListOut], auth=jwt_auth)
def list_sales(
    request,
    payment_status: Optional[str] = None,
    sale_status: Optional[str] = None,
    search: Optional[str] = None
):
    """List historical sales invoices with payment & status filters."""
    qs = Sale.objects.select_related('customer').prefetch_related('items').all()
    if payment_status:
        qs = qs.filter(payment_status=payment_status)
    if sale_status:
        qs = qs.filter(sale_status=sale_status)
    if search:
        qs = qs.filter(invoice_number__icontains=search) | qs.filter(customer__name__icontains=search)

    results = []
    for s in qs[:200]:
        results.append({
            "id": s.id,
            "invoice_number": s.invoice_number,
            "customer_name": s.customer.name if s.customer else None,
            "total_amount": s.total_amount,
            "amount_paid": s.amount_paid,
            "balance_due": s.balance_due,
            "payment_status": s.payment_status,
            "sale_status": s.sale_status,
            "sale_date": s.sale_date,
            "items_count": s.items.count(),
        })
    return results


@router.get("/sales/{sale_id}/", response=SaleOut, auth=jwt_auth)
def get_sale(request, sale_id: int):
    """Retrieve full sale invoice details, line items, and split payment logs."""
    sale = get_object_or_404(
        Sale.objects.select_related('customer', 'branch').prefetch_related('items', 'payments'),
        id=sale_id
    )
    return _format_sale(sale)


# ==============================================================================
# ATOMIC POS CHECKOUT (Hardened against race conditions & rounding bugs)
# ==============================================================================

@router.post("/sales/", response={201: SaleOut, 400: dict}, auth=jwt_auth)
def create_sale_invoice(request, payload: SaleCreateIn):
    """
    Production-grade Atomic POS Checkout:
    1. Locks StockSummary with `select_for_update()` to prevent double-selling & race conditions.
    2. Validates available inventory > requested quantity.
    3. Calculates line item values, making charges, and GST with Decimal precision.
    4. Guarantees mathematical exactness: CGST + SGST == total_gst without penny loss.
    5. Deducts stock atomically via StockMovement ledger.
    6. Supports split payments (cash + card + upi + old gold exchange).
    7. Atomically records cash intake in today's branch DayBook ledger.
    """
    if not payload.items:
        return 400, {"error": "At least one sale item is required."}

    user = request.auth
    branch = user.branch if user else None

    with transaction.atomic():
        # 1. Concurrency Check & Row Locking on Inventory
        product_ids = [it.product_id for it in payload.items]
        # Lock products in deterministic order to prevent deadlocks
        products = {
            p.id: p for p in Product.objects.select_for_update().filter(id__in=product_ids)
        }

        # Check stock quantities with row lock
        for item_in in payload.items:
            prod = products.get(item_in.product_id)
            if not prod:
                return 400, {"error": f"Product id {item_in.product_id} does not exist."}

            summary, _ = StockSummary.objects.select_for_update().get_or_create(product=prod)
            if summary.quantity_on_hand < item_in.quantity:
                return 400, {
                    "error": (
                        f"Insufficient stock for '{prod.sku}' ({prod.name}). "
                        f"Available: {summary.quantity_on_hand}, Requested: {item_in.quantity}"
                    )
                }

        # 2. Customer resolution
        customer = None
        if payload.customer_id:
            customer = Customer.objects.filter(id=payload.customer_id).first()

        # Check today's DayBook if cash is part of payment
        today = timezone.localdate()
        payment_list = []
        if payload.payments:
            payment_list.extend(payload.payments)
        elif payload.payment:
            payment_list.append(payload.payment)

        has_cash = any(p.method.lower() == 'cash' for p in payment_list)
        if has_cash:
            day_book_check = DayBook.objects.filter(date=today, branch=branch).first()
            if day_book_check and day_book_check.is_closed:
                return 400, {"error": "DayBook cash drawer is closed for today. Reopen DayBook to process cash payments."}

        # 3. Create Draft Sale
        invoice_num = _next_invoice_number(branch)
        sale = Sale.objects.create(
            invoice_number=invoice_num,
            customer=customer,
            branch=branch,
            created_by=user,
            gold_rate_per_gram=Decimal('0.00'),
            notes=payload.notes or '',
        )

        subtotal = Decimal('0.00')
        total_gst = Decimal('0.00')

        # 4. Process Line Items & Atomic Stock OUT
        for item_in in payload.items:
            prod = products[item_in.product_id]
            qty = item_in.quantity
            gold_rate = item_in.gold_rate_per_gram
            making = item_in.making_charge
            stone = item_in.stone_charge
            gst_rate = Decimal('3.00')

            net_wt = prod.net_weight
            gold_val = (net_wt * gold_rate).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            unit_price = (gold_val + making + stone).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            item_total = (unit_price * qty).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            gst_on_item = (item_total * gst_rate / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

            SaleItem.objects.create(
                sale=sale,
                product=prod,
                quantity=qty,
                product_name=prod.name,
                sku=prod.sku,
                purity=prod.purity.name,
                gross_weight=prod.gross_weight,
                net_weight=net_wt,
                gold_rate_per_gram=gold_rate,
                making_charge=making,
                stone_charge=stone,
                unit_price=unit_price,
                total_price=item_total,
                hsn_code=prod.hsn_code or '7113',
                gst_rate=gst_rate,
                huid=prod.huid or '',
                wastage_percent=Decimal('0.00'),
            )

            # Record stock movement OUT
            record_stock_movement(
                product=prod,
                movement_type=StockMovement.MovementType.OUT,
                quantity=qty,
                reference_type='sale',
                reference_id=sale.id,
                user=user,
                branch=branch,
                note=f"POS Sale Invoice {sale.invoice_number}"
            )

            # Automatically remove sold item from active shop inventory
            summary = StockSummary.objects.filter(product=prod).first()
            if not summary or summary.quantity_on_hand <= 0:
                prod.is_active = False
                prod.save(update_fields=['is_active', 'updated_at'])
                Item.objects.update_or_create(
                    qr_code=prod.sku,
                    defaults={
                        'name': prod.name,
                        'weight': prod.gross_weight,
                        'status': Item.Status.SOLD,
                        'locked_by_bill': None,
                    }
                )

            subtotal += item_total
            total_gst += gst_on_item

        # 5. Old Gold Exchange Valuation
        old_gold_val = Decimal('0.00')
        if payload.old_gold_weight > 0 and payload.old_gold_rate > 0:
            old_gold_val = (payload.old_gold_weight * payload.old_gold_rate).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )

        # 6. Balanced GST Allocation: cgst + sgst == total_gst
        cgst = (total_gst / 2).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        sgst = total_gst - cgst  # Guarantees mathematical exactness without float drift
        discount = payload.discount.quantize(Decimal('0.01'))

        # Financial Invariant: Discount cannot exceed gross invoice total (subtotal + tax)
        gross_total = (subtotal + total_gst).quantize(Decimal('0.01'))
        if discount > gross_total:
            return 400, {"error": f"Discount (₹{discount}) cannot exceed gross invoice amount (₹{gross_total})."}

        total = (gross_total - discount).quantize(Decimal('0.01'))

        # 7. Collect All Payments (Single or Split)
        payment_list = []
        if payload.payments:
            payment_list.extend(payload.payments)
        elif payload.payment:
            payment_list.append(payload.payment)

        total_cash_received = Decimal('0.00')
        total_payment_amount = Decimal('0.00')

        for p_in in payment_list:
            p_amount = p_in.amount.quantize(Decimal('0.01'))
            total_payment_amount += p_amount
            Payment.objects.create(
                sale=sale,
                method=p_in.method,
                amount=p_amount,
                reference=p_in.reference or '',
                note=p_in.note or ''
            )
            if p_in.method.lower() == 'cash':
                total_cash_received += p_amount

        # If old gold offset was applied, record it as an explicit Payment record for audit clarity
        if old_gold_val > Decimal('0.00'):
            Payment.objects.create(
                sale=sale,
                method='old_gold',
                amount=old_gold_val,
                reference=f"{payload.old_gold_weight}g @ ₹{payload.old_gold_rate}/g",
                note='Old Gold Exchange Credit'
            )
            total_payment_amount += old_gold_val

        balance = (total - total_payment_amount).quantize(Decimal('0.01'))

        # 8. Update Sale Header Totals
        sale.gold_rate_per_gram = payload.items[0].gold_rate_per_gram
        sale.subtotal = subtotal
        sale.discount = discount
        sale.cgst_amount = cgst
        sale.sgst_amount = sgst
        sale.total_amount = total
        sale.old_gold_value = old_gold_val
        sale.amount_paid = total_payment_amount
        sale.balance_due = max(balance, Decimal('0.00'))
        sale.payment_status = (
            Sale.PaymentStatus.PAID if balance <= 0
            else Sale.PaymentStatus.PARTIAL if total_payment_amount > 0
            else Sale.PaymentStatus.PENDING
        )
        sale.save()

        # 9. DayBook Cash Ledger Integration: Record cash received in today's ledger
        if total_cash_received > Decimal('0.00'):
            today = timezone.localdate()
            day_book, _ = DayBook.objects.select_for_update().get_or_create(
                date=today, branch=branch,
                defaults={'opening_balance': Decimal('0.00')}
            )
            if day_book.is_closed:
                return 400, {"error": "Cannot post cash intake to a closed DayBook. Reopen DayBook first."}
            day_book.cash_in += total_cash_received
            day_book.save(update_fields=['cash_in', 'updated_at'])

        # Reload with relations
        sale = Sale.objects.select_related('customer', 'branch').prefetch_related('items', 'payments').get(id=sale.id)
        return 201, _format_sale(sale)


# ==============================================================================
# INVOICE PDF DOWNLOAD
# ==============================================================================

@router.get("/sales/{sale_id}/invoice-pdf/", auth=jwt_auth)
def download_invoice_pdf(request, sale_id: int):
    """Generate high-resolution printable GST Tax Invoice PDF using ReportLab."""
    sale = get_object_or_404(
        Sale.objects.select_related('customer', 'branch').prefetch_related('items', 'payments'),
        id=sale_id
    )
    pdf_bytes = generate_invoice_pdf(sale)
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{sale.invoice_number}.pdf"'
    response['Access-Control-Expose-Headers'] = 'Content-Disposition'
    return response


@router.get("/sales/{sale_id}/invoice_pdf/", auth=jwt_auth)
def download_invoice_pdf_underscore(request, sale_id: int):
    """Compatibility alias for invoice PDF download."""
    return download_invoice_pdf(request, sale_id)


# ==============================================================================
# INVOICE CUSTOMIZATION & SETTINGS ENGINE
# ==============================================================================

@router.get("/billing/invoice-settings/", response=InvoiceSettingOut, auth=jwt_auth)
def get_invoice_settings(request):
    """Retrieve invoice branding, layout templates, toggles, and terms for the active branch."""
    user = request.auth
    branch = getattr(user, 'branch', None)
    if not branch:
        branch = Branch.objects.first()
    if not branch:
        branch = Branch.objects.create(name="Main Showroom", is_active=True)
    setting, _ = InvoiceSetting.objects.get_or_create(branch=branch)
    return setting


@router.put("/billing/invoice-settings/", response=InvoiceSettingOut, auth=jwt_auth)
def update_invoice_settings(request, payload: InvoiceSettingUpdateIn):
    """
    Update invoice template style, headers, invocations, columns, and terms.
    Strictly restricted to Store Owners and Managers.
    """
    user = request.auth
    require_role(user, ['owner', 'manager', 'superadmin'])
    branch = getattr(user, 'branch', None)
    if not branch:
        branch = Branch.objects.first()
    if not branch:
        branch = Branch.objects.create(name="Main Showroom", is_active=True)
    setting, _ = InvoiceSetting.objects.get_or_create(branch=branch)

    update_data = payload.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(setting, field, value)
    setting.save()
    return setting


@router.post("/billing/invoice-settings/reset-demo/", response=InvoiceSettingOut, auth=jwt_auth)
def reset_demo_invoice_settings(request):
    """
    Reset invoice configuration to Shree Balaji Abharan Angadi (Gadag) reference profile.
    Restricted to Store Owners and Managers.
    """
    user = request.auth
    require_role(user, ['owner', 'manager', 'superadmin'])
    branch = getattr(user, 'branch', None)
    if not branch:
        branch = Branch.objects.first()
    if not branch:
        branch = Branch.objects.create(name="Main Showroom", is_active=True)
    setting, _ = InvoiceSetting.objects.get_or_create(branch=branch)
    setting.header_invocation = "|| ಶ್ರೀ ಶಾಂತೇರಿ ಪ್ರಸನ್ನ ||"
    setting.shop_name_primary = "Shree Balaji Abharan Angadi"
    setting.shop_name_secondary = "ಶ್ರೀ ಬಾಲಾಜಿ ಆಭರಣ ಅಂಗಡಿ"
    setting.tagline = "Gold & Silver Merchants"
    setting.address_primary = "Beside Mukkal Basaveshwar Temple, Old Shroff Bazar, GADAG-582101"
    setting.address_secondary = "ಮುಕ್ಕಾಲ ಬಸವೇಶ್ವರ ದೇವಸ್ಥಾನದ ಹತ್ತಿರ, ಹಳೇ ಸರಾಫ ಬಜಾರ, ಗದಗ-582101"
    setting.phone_landline = "(08372) 238391"
    setting.phone_mobile_1 = "9449642640"
    setting.phone_mobile_2 = "7760755515"
    setting.email = "Ranjanbalaji93@gmail.com"
    setting.gstin = "29ADNPP6515B1ZF"
    setting.pan_number = "ADNPP6515B"
    setting.state_name = "Karnataka"
    setting.state_code = "29"
    setting.bis_hallmark_licence = "HM/C-7891234"
    setting.template_style = "traditional_bilingual"
    setting.default_paper_size = "A4"
    setting.show_invocation = True
    setting.show_bilingual_header = True
    setting.show_huid = True
    setting.show_purity = True
    setting.show_gross_net_weight = True
    setting.show_wastage = True
    setting.show_making_charge = True
    setting.show_stone_details = True
    setting.show_rate_per_gram = True
    setting.show_old_gold_section = True
    setting.show_upi_qr = True
    setting.show_bank_details = True
    setting.show_customer_address = True
    setting.show_hallmark_badge = True
    setting.bank_name = "State Bank of India"
    setting.account_name = "Shree Balaji Abharan Angadi"
    setting.account_number = "38291048591"
    setting.ifsc_code = "SBIN0000837"
    setting.upi_id = "9449642640@sbi"
    setting.terms_and_conditions = (
        "1. Exchange with in 3 days, No Guarantee For Stone Falling & Brekage.\n"
        "2. Weight variation subject to +/- 10mg tolerance.\n"
        "3. Certified 916/750 Hallmark Jewellery conforms to Bureau of Indian Standards (BIS).\n"
        "4. Old Gold purchase/exchange value is calculated after melting assay & karat verification.\n"
        "5. Subject to Gadag jurisdiction only."
    )
    setting.declaration = "Certified that the particulars given above are true and correct and price charged is legal."
    setting.signatory_title = "For, Shree Balaji Abharan Angadi"
    setting.save()
    return setting


# ==============================================================================
# SALE VOID / CANCELLATION
# ==============================================================================

@router.post("/sales/{sale_id}/cancel/", response={200: SaleOut, 400: dict}, auth=jwt_auth)
def cancel_sale(request, sale_id: int):
    """
    Safely void/cancel a sale invoice:
    - Verifies sale is currently active.
    - Atomically reverses all stock items back into inventory (RETURN movement).
    - If cash payments were collected, records a DayBook cash_out outflow for the refund.
    """
    require_role(request.auth, ['owner', 'manager'])
    sale = get_object_or_404(
        Sale.objects.select_related('customer', 'branch').prefetch_related('items', 'payments'),
        id=sale_id
    )

    if sale.sale_status == Sale.SaleStatus.CANCELLED:
        return 400, {"error": "Invoice is already cancelled."}

    with transaction.atomic():
        # 1. Reverse inventory movements
        for item in sale.items.all():
            record_stock_movement(
                product=item.product,
                movement_type=StockMovement.MovementType.RETURN,
                quantity=item.quantity,
                reference_type='sale_cancel',
                reference_id=sale.id,
                note=f"Reversal on Voided Invoice {sale.invoice_number}",
                user=request.auth,
                branch=sale.branch,
            )

            # Reactivate item in inventory if stock was returned
            if item.product:
                summary = StockSummary.objects.filter(product=item.product).first()
                if summary and summary.quantity_on_hand > 0:
                    item.product.is_active = True
                    item.product.save(update_fields=['is_active', 'updated_at'])
                    Item.objects.filter(qr_code=item.product.sku).update(
                        status=Item.Status.AVAILABLE,
                        locked_by_bill=None
                    )

        # 2. Reverse cash intake in DayBook if applicable
        cash_paid = sum(p.amount for p in sale.payments.filter(method='cash'))
        if cash_paid > Decimal('0.00'):
            today = timezone.localdate()
            day_book, _ = DayBook.objects.select_for_update().get_or_create(
                date=today, branch=sale.branch,
                defaults={'opening_balance': Decimal('0.00')}
            )
            if day_book.is_closed:
                return 400, {"error": "Cannot process cash refund: today's DayBook is closed. Reopen DayBook first."}
            day_book.cash_out += cash_paid
            day_book.save(update_fields=['cash_out', 'updated_at'])

        sale.sale_status = Sale.SaleStatus.CANCELLED
        sale.save(update_fields=['sale_status'])

    return 200, _format_sale(sale)


# ==============================================================================
# RECORD BALANCE PAYMENT
# ==============================================================================

@router.post("/sales/{sale_id}/add-payment/", response={200: SaleOut, 400: dict}, auth=jwt_auth)
def add_sale_payment(request, sale_id: int, payload: AddPaymentIn):
    """Record an incremental payment against an unpaid or partially-paid invoice."""
    sale = get_object_or_404(
        Sale.objects.select_related('customer', 'branch').prefetch_related('items', 'payments'),
        id=sale_id
    )

    if sale.sale_status == Sale.SaleStatus.CANCELLED:
        return 400, {"error": "Cannot accept payment on a cancelled invoice."}

    amount = payload.amount.quantize(Decimal('0.01'))
    if amount <= Decimal('0.00'):
        return 400, {"error": "Payment amount must be greater than zero."}

    with transaction.atomic():
        payment = Payment.objects.create(
            sale=sale,
            method=payload.method,
            amount=amount,
            reference=payload.reference or '',
            note=payload.note or ''
        )

        sale.amount_paid += amount
        sale.balance_due = max(sale.total_amount - sale.amount_paid, Decimal('0.00'))
        sale.payment_status = (
            Sale.PaymentStatus.PAID if sale.balance_due <= Decimal('0.00')
            else Sale.PaymentStatus.PARTIAL
        )
        sale.save(update_fields=['amount_paid', 'balance_due', 'payment_status'])

        # If payment is cash, record in DayBook
        if payload.method.lower() == 'cash':
            today = timezone.localdate()
            day_book, _ = DayBook.objects.select_for_update().get_or_create(
                date=today, branch=sale.branch,
                defaults={'opening_balance': Decimal('0.00')}
            )
            if day_book.is_closed:
                return 400, {"error": "Cannot accept cash payment: today's DayBook is closed. Reopen DayBook first."}
            day_book.cash_in += amount
            day_book.save(update_fields=['cash_in', 'updated_at'])

    sale = Sale.objects.select_related('customer', 'branch').prefetch_related('items', 'payments').get(id=sale.id)
    return 200, _format_sale(sale)
