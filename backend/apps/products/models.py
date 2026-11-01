from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Purity(models.Model):
    """e.g. 22KT, 18KT, 916, 750"""
    name = models.CharField(max_length=20, unique=True)
    fineness = models.DecimalField(max_digits=5, decimal_places=3,
                                   help_text='Fineness value e.g. 0.916 for 22KT')

    class Meta:
        verbose_name_plural = 'Purities'

    def __str__(self):
        return self.name


class Product(models.Model):
    """Core jewellery item / SKU"""
    name = models.CharField(max_length=200)
    sku = models.CharField(max_length=50, unique=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    purity = models.ForeignKey(Purity, on_delete=models.PROTECT, related_name='products')

    # Weights in grams — NUMERIC, never float
    gross_weight = models.DecimalField(max_digits=10, decimal_places=3,
                                       validators=[MinValueValidator(Decimal('0.001'))])
    stone_weight = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal('0.000'))
    other_weight = models.DecimalField(max_digits=10, decimal_places=3, default=Decimal('0.000'))

    @property
    def net_weight(self):
        return self.gross_weight - self.stone_weight - self.other_weight

    @property
    def qr_token(self):
        """Permanent unique QR token of the physical inventory piece."""
        cached = getattr(self, '_qr_token', None)
        if cached is not None:
            return cached
        if hasattr(self, 'items'):
            first = next((i for i in self.items.all() if i.status == 'AVAILABLE'), None) or self.items.first()
            if first:
                return first.qr_token
        return None

    # Making charges
    making_charge_type = models.CharField(
        max_length=10,
        choices=[('per_gram', 'Per Gram'), ('percent', '% on Gold Value'), ('fixed', 'Fixed Amount')],
        default='per_gram'
    )
    making_charge_value = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    # Product details
    description = models.TextField(blank=True)
    hsn_code = models.CharField(max_length=20, blank=True, default='7113')
    huid = models.CharField(max_length=20, blank=True, help_text='Hallmark Unique ID')
    photo = models.ImageField(upload_to='product_photos/', null=True, blank=True)

    is_active = models.BooleanField(default=True)
    branch = models.ForeignKey(
        'accounts.Branch', null=True, blank=True, on_delete=models.SET_NULL, related_name='products'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.sku})"

    class Meta:
        ordering = ['-created_at']
