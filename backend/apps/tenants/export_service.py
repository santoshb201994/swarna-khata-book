import os
import csv
import io
import json
import zipfile
import tempfile
from datetime import datetime, date
from decimal import Decimal
from django.utils import timezone
from django_tenants.utils import schema_context

from apps.tenants.models import Client
from apps.accounts.models import User, Branch
from apps.products.models import Product, Category, Purity
from apps.stock.models import StockMovement
from apps.billing.models import Sale, SaleItem, Payment, InvoiceSetting
from apps.accounting.models import Customer, DayBook, GoldRate


class CleanupFile:
    """File wrapper that securely deletes the underlying temp file upon stream completion."""
    def __init__(self, path: str):
        self.path = path
        self.file = open(path, 'rb')

    def read(self, *args):
        return self.file.read(*args)

    def close(self):
        try:
            self.file.close()
        finally:
            if os.path.exists(self.path):
                try:
                    os.remove(self.path)
                except OSError:
                    pass


def _write_csv_to_zip(zip_archive: zipfile.ZipFile, zip_path: str, headers: list[str], rows_generator):
    """
    Streams CSV rows directly into the ZIP archive using utf-8-sig
    (BOM encoded) for full Microsoft Excel bilingual compatibility.
    """
    buffer = io.StringIO()
    writer = csv.writer(buffer, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(headers)

    count = 0
    for row in rows_generator:
        writer.writerow(row)
        count += 1

    zip_archive.writestr(zip_path, buffer.getvalue().encode('utf-8-sig'))
    return count


def export_tenant_data_to_zip(schema_name: str, zip_archive: zipfile.ZipFile, start_date: date = None, end_date: date = None, folder_prefix: str = "") -> dict:
    """
    Exports all operational, financial, and inventory data of a single tenant schema
    into an isolated folder within the provided ZIP archive.
    """
    with schema_context(schema_name):
        tenant_obj = Client.objects.filter(schema_name=schema_name).first()
        store_name = tenant_obj.name if tenant_obj else schema_name
        manifest_counts = {}

        # 1. Sales & Invoices
        sales_qs = Sale.objects.all().order_by('-sale_date')
        if start_date:
            sales_qs = sales_qs.filter(sale_date__date__gte=start_date)
        if end_date:
            sales_qs = sales_qs.filter(sale_date__date__lte=end_date)

        def generate_sales_rows():
            for s in sales_qs.select_related('customer', 'branch').iterator(chunk_size=1000):
                cust_name = s.customer_snapshot.get('name') or (s.customer.name if s.customer else '')
                cust_phone = s.customer_snapshot.get('phone') or (s.customer.phone if s.customer else '')
                cust_pan = s.customer_snapshot.get('pan_number') or (s.customer.pan_number if s.customer else '')
                yield [
                    s.invoice_number,
                    s.sale_date.strftime("%Y-%m-%d %H:%M:%S") if s.sale_date else '',
                    cust_name,
                    cust_phone,
                    cust_pan,
                    str(s.gold_rate_per_gram),
                    str(s.subtotal),
                    str(s.discount),
                    str(s.cgst_amount),
                    str(s.sgst_amount),
                    str(s.total_amount),
                    str(s.amount_paid),
                    str(s.old_gold_value),
                    str(s.balance_due),
                    s.payment_status,
                    s.sale_status,
                    s.pdf_sha256 or '',
                    s.notes or '',
                ]

        manifest_counts['sales_invoices'] = _write_csv_to_zip(
            zip_archive,
            f"{folder_prefix}sales_invoices.csv",
            [
                'Invoice Number', 'Sale Date', 'Customer Name', 'Customer Phone', 'Customer PAN',
                'Gold Rate (Rs/g)', 'Subtotal (Rs)', 'Discount (Rs)', 'CGST (Rs)', 'SGST (Rs)',
                'Grand Total (Rs)', 'Amount Paid (Rs)', 'Old Gold Value (Rs)', 'Balance Due (Rs)',
                'Payment Status', 'Sale Status', 'PDF SHA256 Hash', 'Notes'
            ],
            generate_sales_rows()
        )

        # 2. Sale Items Breakdown
        items_qs = SaleItem.objects.filter(sale__in=sales_qs).select_related('sale').order_by('-id')

        def generate_sale_items_rows():
            for it in items_qs.iterator(chunk_size=1000):
                yield [
                    it.sale.invoice_number,
                    it.product_name,
                    it.sku,
                    it.purity,
                    it.quantity,
                    str(it.gross_weight),
                    str(it.net_weight),
                    str(it.gold_rate_per_gram),
                    str(it.making_charge),
                    str(it.stone_charge),
                    str(it.total_price),
                    it.hsn_code or '7113',
                    it.huid or '',
                    str(it.gst_rate),
                ]

        manifest_counts['sale_items'] = _write_csv_to_zip(
            zip_archive,
            f"{folder_prefix}sale_items.csv",
            [
                'Invoice Number', 'Product Name', 'SKU', 'Purity', 'Quantity',
                'Gross Weight (g)', 'Net Weight (g)', 'Gold Rate (Rs/g)', 'Making Charge (Rs)',
                'Stone Charge (Rs)', 'Item Total (Rs)', 'HSN Code', 'HUID', 'GST Rate (%)'
            ],
            generate_sale_items_rows()
        )

        # 3. Payments Ledger
        payments_qs = Payment.objects.filter(sale__in=sales_qs).select_related('sale').order_by('-paid_at')

        def generate_payment_rows():
            for p in payments_qs.iterator(chunk_size=1000):
                yield [
                    p.sale.invoice_number,
                    p.method,
                    str(p.amount),
                    p.reference or '',
                    p.paid_at.strftime("%Y-%m-%d %H:%M:%S") if p.paid_at else '',
                    p.note or '',
                ]

        manifest_counts['payments'] = _write_csv_to_zip(
            zip_archive,
            f"{folder_prefix}payments.csv",
            ['Invoice Number', 'Payment Method', 'Amount (Rs)', 'Transaction Reference', 'Paid At', 'Notes'],
            generate_payment_rows()
        )

        # 4. Inventory Catalog & Products
        products_qs = Product.objects.all().select_related('category', 'purity').order_by('sku')

        def generate_products_rows():
            for prod in products_qs.iterator(chunk_size=1000):
                yield [
                    prod.sku,
                    prod.name,
                    prod.category.name if prod.category else '',
                    prod.purity.name if prod.purity else '',
                    str(prod.gross_weight),
                    str(prod.stone_weight),
                    str(prod.other_weight),
                    str(prod.net_weight),
                    prod.making_charge_type,
                    str(prod.making_charge_value),
                    prod.huid or '',
                    prod.hsn_code or '7113',
                    getattr(prod, 'item_status', 'AVAILABLE'),
                    prod.created_at.strftime("%Y-%m-%d %H:%M:%S") if getattr(prod, 'created_at', None) else '',
                    prod.is_active,
                ]

        manifest_counts['products'] = _write_csv_to_zip(
            zip_archive,
            f"{folder_prefix}inventory_products.csv",
            [
                'SKU', 'Product Name', 'Category', 'Purity', 'Gross Weight (g)', 'Stone Weight (g)',
                'Other Weight (g)', 'Net Weight (g)', 'Making Charge Type', 'Making Charge Value',
                'HUID', 'HSN Code', 'Item Status', 'Created At', 'Active'
            ],
            generate_products_rows()
        )

        # 5. Stock Movements & Audit Trail
        stock_qs = StockMovement.objects.all().select_related('product', 'created_by').order_by('-created_at')
        if start_date:
            stock_qs = stock_qs.filter(created_at__date__gte=start_date)
        if end_date:
            stock_qs = stock_qs.filter(created_at__date__lte=end_date)

        def generate_stock_rows():
            for sm in stock_qs.iterator(chunk_size=1000):
                yield [
                    sm.product.sku if sm.product else '',
                    sm.product.name if sm.product else '',
                    sm.movement_type,
                    sm.quantity,
                    sm.reference_type or '',
                    sm.reference_id or '',
                    sm.created_by.username if sm.created_by else '',
                    sm.created_at.strftime("%Y-%m-%d %H:%M:%S") if sm.created_at else '',
                ]

        manifest_counts['stock_movements'] = _write_csv_to_zip(
            zip_archive,
            f"{folder_prefix}stock_movements.csv",
            ['Product SKU', 'Product Name', 'Movement Type', 'Quantity', 'Reference Type', 'Reference ID', 'Logged By', 'Timestamp'],
            generate_stock_rows()
        )

        # 6. Customer Khata Directory
        customers_qs = Customer.objects.all().order_by('name')

        def generate_customer_rows():
            for c in customers_qs.iterator(chunk_size=1000):
                yield [
                    c.id,
                    c.name,
                    c.phone,
                    c.email or '',
                    c.address or '',
                    c.pan_number or '',
                    c.aadhar_last4 or '',
                    c.created_at.strftime("%Y-%m-%d %H:%M:%S") if c.created_at else '',
                ]

        manifest_counts['customers'] = _write_csv_to_zip(
            zip_archive,
            f"{folder_prefix}customers.csv",
            ['Customer ID', 'Full Name', 'Phone', 'Email', 'Address', 'PAN Card Number', 'Aadhaar Last 4', 'Registered Date'],
            generate_customer_rows()
        )

        # 7. Day Book & Daily Cash Register
        daybook_qs = DayBook.objects.all().order_by('-date')
        if start_date:
            daybook_qs = daybook_qs.filter(date__gte=start_date)
        if end_date:
            daybook_qs = daybook_qs.filter(date__lte=end_date)

        def generate_daybook_rows():
            for db in daybook_qs.iterator(chunk_size=1000):
                yield [
                    db.date.strftime("%Y-%m-%d") if db.date else '',
                    str(db.opening_balance),
                    str(db.cash_in),
                    str(db.cash_out),
                    str(db.closing_balance),
                    db.is_closed,
                    db.closed_by.username if db.closed_by else '',
                    db.notes or '',
                ]

        manifest_counts['daybook'] = _write_csv_to_zip(
            zip_archive,
            f"{folder_prefix}daybook_cash.csv",
            ['Date', 'Opening Balance (Rs)', 'Cash In (Rs)', 'Cash Out (Rs)', 'Closing Balance (Rs)', 'Is Closed', 'Closed By', 'Notes'],
            generate_daybook_rows()
        )

        # 8. Gold & Silver Metal Rates History
        rates_qs = GoldRate.objects.all().select_related('purity').order_by('-effective_date')
        if start_date:
            rates_qs = rates_qs.filter(effective_date__gte=start_date)
        if end_date:
            rates_qs = rates_qs.filter(effective_date__lte=end_date)

        def generate_rates_rows():
            for gr in rates_qs.iterator(chunk_size=1000):
                yield [
                    gr.effective_date.strftime("%Y-%m-%d") if gr.effective_date else '',
                    gr.purity.name if gr.purity else '',
                    str(gr.rate_per_gram),
                    gr.is_current,
                ]

        manifest_counts['gold_rates'] = _write_csv_to_zip(
            zip_archive,
            f"{folder_prefix}gold_rates_history.csv",
            ['Effective Date', 'Purity / Metal', 'Rate Per Gram (Rs)', 'Is Current Active Rate'],
            generate_rates_rows()
        )

        # 9. Showroom Staff (Security: Passwords & Hashes STRIPPED)
        users_qs = User.objects.all().order_by('username')

        def generate_user_rows():
            for u in users_qs.iterator(chunk_size=1000):
                yield [
                    u.id,
                    u.username,
                    u.first_name or '',
                    u.last_name or '',
                    u.role,
                    u.email or '',
                    u.phone or '',
                    u.is_active,
                    u.date_joined.strftime("%Y-%m-%d %H:%M:%S") if u.date_joined else '',
                ]

        manifest_counts['staff_users'] = _write_csv_to_zip(
            zip_archive,
            f"{folder_prefix}showroom_staff.csv",
            ['User ID', 'Username', 'First Name', 'Last Name', 'Assigned Role', 'Email', 'Phone', 'Active Status', 'Date Joined'],
            generate_user_rows()
        )

        # 10. Store Manifest Metadata
        manifest = {
            "schema_name": schema_name,
            "store_name": store_name,
            "export_generated_at": timezone.now().strftime("%Y-%m-%d %H:%M:%S %Z"),
            "time_frame": {
                "start_date": str(start_date) if start_date else "all_time",
                "end_date": str(end_date) if end_date else "current",
            },
            "record_counts": manifest_counts,
            "compliance_notice": (
                "Exported by Swarna Khata ERP with PostgreSQL snapshot immutability. "
                "Retain for statutory GST Section 36 audit compliance."
            )
        }
        zip_archive.writestr(
            f"{folder_prefix}export_manifest.json",
            json.dumps(manifest, indent=2).encode('utf-8')
        )

        return manifest


def generate_shop_export_archive(schema_name: str, start_date: date = None, end_date: date = None) -> str:
    """
    Creates a temporary compressed ZIP archive containing all operational data for a single shop.
    Returns the absolute path to the temp file.
    """
    temp_zip = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
    temp_path = temp_zip.name
    temp_zip.close()

    with zipfile.ZipFile(temp_path, 'w', compression=zipfile.ZIP_DEFLATED) as zip_arch:
        export_tenant_data_to_zip(schema_name, zip_arch, start_date, end_date, folder_prefix="")

    return temp_path


def generate_all_shops_export_archive(start_date: date = None, end_date: date = None) -> str:
    """
    Creates a multi-tenant archive containing exports for every active shop in separate subfolders.
    Restricted to Developer / Superadmin.
    Returns the absolute path to the temp file.
    """
    temp_zip = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
    temp_path = temp_zip.name
    temp_zip.close()

    active_tenants = Client.objects.filter(is_active=True).exclude(schema_name='public')
    all_manifests = []

    with zipfile.ZipFile(temp_path, 'w', compression=zipfile.ZIP_DEFLATED) as zip_arch:
        for tenant in active_tenants:
            manifest = export_tenant_data_to_zip(
                tenant.schema_name,
                zip_arch,
                start_date,
                end_date,
                folder_prefix=f"{tenant.schema_name}/"
            )
            all_manifests.append(manifest)

        # Global developer overview manifest
        global_summary = {
            "platform": "Swarna Khata Jewellery ERP Multi-Tenant SaaS",
            "export_type": "global_multi_store_full_export",
            "generated_at": timezone.now().strftime("%Y-%m-%d %H:%M:%S %Z"),
            "filter_range": {
                "start_date": str(start_date) if start_date else "all_time",
                "end_date": str(end_date) if end_date else "current",
            },
            "total_shops_exported": len(all_manifests),
            "shops": all_manifests,
        }
        zip_arch.writestr("global_export_summary.json", json.dumps(global_summary, indent=2).encode('utf-8'))

    return temp_path
