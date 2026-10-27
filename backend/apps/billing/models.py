from django.db import models
from django.core.exceptions import ValidationError
from decimal import Decimal


class Sale(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PARTIAL = 'partial', 'Partially Paid'
        PAID = 'paid', 'Fully Paid'

    class SaleStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        CANCELLED = 'cancelled', 'Cancelled'

    invoice_number = models.CharField(max_length=30, unique=True)
    customer = models.ForeignKey(
        'accounting.Customer', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='sales'
    )
    branch = models.ForeignKey(
        'accounts.Branch', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='sales'
    )
    created_by = models.ForeignKey(
        'accounts.User', null=True, on_delete=models.SET_NULL, related_name='sales'
    )
    sale_date = models.DateTimeField(auto_now_add=True)

    # Gold rate locked at time of sale — NEVER float
    gold_rate_per_gram = models.DecimalField(max_digits=10, decimal_places=2)

    # Totals — computed and stored for audit integrity
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    cgst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    sgst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    igst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    old_gold_value = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    balance_due = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    payment_status = models.CharField(max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    sale_status = models.CharField(max_length=15, choices=SaleStatus.choices, default=SaleStatus.ACTIVE)
    notes = models.TextField(blank=True)

    # Snapshot Immutability (PostgreSQL JSONB storage for statutory tax audit & GST compliance)
    shop_snapshot = models.JSONField(
        default=dict,
        blank=True,
        help_text="Immutable snapshot of shop name, address, GSTIN, PAN, bank details, and invoice settings at time of sale"
    )
    customer_snapshot = models.JSONField(
        default=dict,
        blank=True,
        help_text="Immutable snapshot of customer name, phone, address, PAN, and Aadhaar at time of sale"
    )
    pdf_sha256 = models.CharField(
        max_length=64,
        blank=True,
        help_text="Cryptographic SHA-256 digest of the invoice PDF generated at time of checkout"
    )

    class Meta:
        ordering = ['-sale_date']
        indexes = [models.Index(fields=['invoice_number']), models.Index(fields=['sale_date'])]

    def clean(self):
        super().clean()
        if self.pk:
            orig = Sale.objects.filter(pk=self.pk).first()
            if orig:
                if orig.shop_snapshot and self.shop_snapshot != orig.shop_snapshot:
                    raise ValidationError("shop_snapshot is immutable and cannot be altered after sale creation.")
                if orig.customer_snapshot and self.customer_snapshot != orig.customer_snapshot:
                    raise ValidationError("customer_snapshot is immutable and cannot be altered after sale creation.")

    def __str__(self):
        return f"Invoice {self.invoice_number}"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(
        'products.Product', on_delete=models.PROTECT, related_name='sale_items'
    )
    quantity = models.PositiveIntegerField(default=1)

    # Snapshot at time of sale — never changes after
    product_name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50)
    purity = models.CharField(max_length=20)
    gross_weight = models.DecimalField(max_digits=10, decimal_places=3)
    net_weight = models.DecimalField(max_digits=10, decimal_places=3)
    gold_rate_per_gram = models.DecimalField(max_digits=10, decimal_places=2)
    making_charge = models.DecimalField(max_digits=10, decimal_places=2)
    stone_charge = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    hsn_code = models.CharField(max_length=20, default='7113')
    gst_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('3.00'))
    huid = models.CharField(max_length=20, blank=True, default='', help_text='Hallmark Unique ID')
    wastage_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"{self.sku} x{self.quantity} in {self.sale.invoice_number}"


class Payment(models.Model):
    class PaymentMethod(models.TextChoices):
        CASH = 'cash', 'Cash'
        UPI = 'upi', 'UPI'
        CARD = 'card', 'Card'
        CHEQUE = 'cheque', 'Cheque'
        OLD_GOLD = 'old_gold', 'Old Gold Exchange'

    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='payments')
    method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    reference = models.CharField(max_length=100, blank=True, help_text='UPI/cheque ref number')
    paid_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.method} ₹{self.amount} for {self.sale.invoice_number}"


class POSPairingSession(models.Model):
    """Secure temporary pairing session between Laptop POS and Mobile QR Scanner"""
    session_id = models.CharField(max_length=64, unique=True, db_index=True)
    pairing_code = models.CharField(max_length=64, unique=True, db_index=True)
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='pos_pairing_sessions')
    branch = models.ForeignKey('accounts.Branch', null=True, blank=True, on_delete=models.SET_NULL)
    is_redeemed = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    redeemed_at = models.DateTimeField(null=True, blank=True)
    mobile_device_info = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['session_id', 'is_active']),
            models.Index(fields=['pairing_code', 'is_redeemed']),
        ]

    def __str__(self):
        return f"POS Session {self.session_id[:8]} ({'Active' if self.is_active else 'Revoked'})"


class ScannedItemAudit(models.Model):
    """Event deduplication and audit trail for mobile QR scans"""
    event_id = models.CharField(max_length=64, unique=True, db_index=True)
    session = models.ForeignKey(POSPairingSession, on_delete=models.CASCADE, related_name='scanned_events')
    product = models.ForeignKey('products.Product', null=True, blank=True, on_delete=models.SET_NULL)
    qr_payload = models.TextField()
    is_successful = models.BooleanField(default=True)
    error_message = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['event_id']),
            models.Index(fields=['session', 'created_at']),
        ]

    def __str__(self):
        return f"ScanEvent {self.event_id[:8]} - {'OK' if self.is_successful else 'FAIL'}"


import uuid

class Bill(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        PAID = 'PAID', 'Paid'
        CANCELLED = 'CANCELLED', 'Cancelled'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Bill {self.id} ({self.status})"


class Item(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = 'AVAILABLE', 'Available'
        IN_CART = 'IN_CART', 'In Cart'
        SOLD = 'SOLD', 'Sold'

    qr_code = models.CharField(max_length=128, unique=True, db_index=True)
    name = models.CharField(max_length=200, blank=True)
    weight = models.DecimalField(max_digits=10, decimal_places=3, help_text="Weight in grams")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE, db_index=True)
    locked_by_bill = models.ForeignKey(
        Bill,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='items'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['status', 'qr_code']),
            models.Index(fields=['locked_by_bill', 'status']),
        ]

    def __str__(self):
        return f"{self.qr_code} - {self.weight}g ({self.status})"


class IdempotencyRecord(models.Model):
    key = models.CharField(max_length=128, db_index=True)
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='idempotency_records')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['bill', 'key']]
        indexes = [
            models.Index(fields=['bill', 'key']),
        ]

    def __str__(self):
        return f"Idempotency {self.key} for Bill {self.bill_id}"


class InvoiceSetting(models.Model):
    """
    Store & Branch Level Invoice Customization Profile.
    Holds bilingual identities, invocations, statutory tax details, bank info,
    dynamic UPI QR config, and custom terms & conditions.
    """
    class TemplateStyle(models.TextChoices):
        TRADITIONAL = 'traditional_bilingual', 'Traditional Bilingual (Heritage)'
        MODERN = 'modern_luxury', 'Modern Luxury (Tanishq/BlueStone Style)'
        ROYAL = 'royal_gold', 'Royal Heritage (Kalyan/Joyalukkas Style)'
        THERMAL = 'compact_thermal', 'Compact Thermal (80mm POS Roll)'

    class PaperSize(models.TextChoices):
        A4 = 'A4', 'A4 Full Page'
        A5 = 'A5', 'A5 Half Page'
        ROLL_80MM = '80mm', '80mm POS Thermal Slip'

    branch = models.OneToOneField(
        'accounts.Branch', on_delete=models.CASCADE, related_name='invoice_setting'
    )

    # Invocations & Branding
    header_invocation = models.CharField(
        max_length=200, default='|| ಶ್ರೀ ಶಾಂತೇರಿ ಪ್ರಸನ್ನ ||', blank=True,
        help_text="Religious or customary top invocation e.g. || ಶ್ರೀ ಶಾಂತೇರಿ ಪ್ರಸನ್ನ ||"
    )
    shop_name_primary = models.CharField(
        max_length=200, default='Shree Balaji Abharan Angadi',
        help_text="Primary display name (English)"
    )
    shop_name_secondary = models.CharField(
        max_length=200, default='ಶ್ರೀ ಬಾಲಾಜಿ ಆಭರಣ ಅಂಗಡಿ', blank=True,
        help_text="Secondary/regional script name (e.g. Kannada)"
    )
    tagline = models.CharField(max_length=200, blank=True, default='Gold & Silver Merchants')

    address_primary = models.TextField(
        default='Beside Mukkal Basaveshwar Temple, Old Shroff Bazar, GADAG-582101'
    )
    address_secondary = models.TextField(
        default='ಮುಕ್ಕಾಲ ಬಸವೇಶ್ವರ ದೇವಸ್ಥಾನದ ಹತ್ತಿರ, ಹಳೇ ಸರಾಫ ಬಜಾರ, ಗದಗ-582101', blank=True
    )

    phone_landline = models.CharField(max_length=50, default='(08372) 238391', blank=True)
    phone_mobile_1 = models.CharField(max_length=50, default='9449642640', blank=True)
    phone_mobile_2 = models.CharField(max_length=50, default='7760755515', blank=True)
    email = models.EmailField(default='Ranjanbalaji93@gmail.com', blank=True)
    website = models.CharField(max_length=100, blank=True)

    # Statutory & GST Compliance
    gstin = models.CharField(max_length=20, default='29ADNPP6515B1ZF')
    pan_number = models.CharField(max_length=20, default='ADNPP6515B', blank=True)
    state_name = models.CharField(max_length=50, default='Karnataka')
    state_code = models.CharField(max_length=10, default='29')
    bis_hallmark_licence = models.CharField(max_length=100, default='HM/C-7891234', blank=True)
    logo_url = models.TextField(blank=True)

    # Presentation Template & Paper Format
    template_style = models.CharField(
        max_length=30, choices=TemplateStyle.choices, default=TemplateStyle.TRADITIONAL
    )
    default_paper_size = models.CharField(
        max_length=10, choices=PaperSize.choices, default=PaperSize.A4
    )

    # Column & Section Visibility Toggles
    show_invocation = models.BooleanField(default=True)
    show_bilingual_header = models.BooleanField(default=True)
    show_huid = models.BooleanField(default=True)
    show_purity = models.BooleanField(default=True)
    show_gross_net_weight = models.BooleanField(default=True)
    show_wastage = models.BooleanField(default=True)
    show_making_charge = models.BooleanField(default=True)
    show_stone_details = models.BooleanField(default=True)
    show_rate_per_gram = models.BooleanField(default=True)
    show_old_gold_section = models.BooleanField(default=True)
    show_upi_qr = models.BooleanField(default=True)
    show_bank_details = models.BooleanField(default=True)
    show_customer_address = models.BooleanField(default=True)
    show_hallmark_badge = models.BooleanField(default=True)

    # Bank Details & Dynamic UPI QR
    bank_name = models.CharField(max_length=100, default='State Bank of India', blank=True)
    account_name = models.CharField(max_length=150, default='Shree Balaji Abharan Angadi', blank=True)
    account_number = models.CharField(max_length=50, default='38291048591', blank=True)
    ifsc_code = models.CharField(max_length=20, default='SBIN0000837', blank=True)
    upi_id = models.CharField(max_length=100, default='9449642640@sbi', blank=True)

    # Terms & Conditions & Signatures
    terms_and_conditions = models.TextField(
        default=(
            "1. Exchange with in 3 days, No Guarantee For Stone Falling & Brekage.\n"
            "2. Weight variation subject to +/- 10mg tolerance.\n"
            "3. Certified 916/750 Hallmark Jewellery conforms to Bureau of Indian Standards (BIS).\n"
            "4. Old Gold purchase/exchange value is calculated after melting assay & karat verification.\n"
            "5. Subject to Gadag jurisdiction only."
        )
    )
    declaration = models.CharField(
        max_length=255,
        default="Certified that the particulars given above are true and correct and price charged is legal."
    )
    signatory_title = models.CharField(
        max_length=100, default='For, Shree Balaji Abharan Angadi'
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"InvoiceSettings: {self.shop_name_primary} ({self.branch})"


