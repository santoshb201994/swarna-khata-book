from django.db import models
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

    class Meta:
        ordering = ['-sale_date']
        indexes = [models.Index(fields=['invoice_number']), models.Index(fields=['sale_date'])]

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

