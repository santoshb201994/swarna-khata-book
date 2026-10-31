from decimal import Decimal
from django.db import models


class QRTag(models.Model):
    product = models.OneToOneField(
        'products.Product', on_delete=models.CASCADE, related_name='qr_tag'
    )
    qr_data = models.TextField(help_text='JSON payload encoded in QR')
    qr_image = models.ImageField(upload_to='qr_codes/', null=True, blank=True)
    printed_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"QR: {self.product.sku}"

    class Meta:
        verbose_name = 'QR Tag'


class Tray(models.Model):
    code = models.CharField(max_length=50, unique=True, help_text='Unique code for the tray/group (e.g. TRAY-101)')
    name = models.CharField(max_length=150, help_text='Display name for the tray')
    description = models.TextField(blank=True, default='')
    branch = models.ForeignKey(
        'accounts.Branch', null=True, blank=True, on_delete=models.SET_NULL, related_name='trays'
    )
    items = models.ManyToManyField(
        'products.Product', related_name='trays', blank=True
    )
    qr_data = models.TextField(blank=True, default='', help_text='JSON payload encoded in group QR')
    qr_image = models.ImageField(upload_to='tray_qr_codes/', null=True, blank=True)
    printed_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tray / Group QR Tag'
        verbose_name_plural = 'Trays / Group QR Tags'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.code})"

    @property
    def total_items(self):
        return self.items.count()

    @property
    def total_gross_weight(self):
        return sum((item.gross_weight for item in self.items.all()), Decimal('0.000'))

    @property
    def total_net_weight(self):
        return sum((item.net_weight for item in self.items.all()), Decimal('0.000'))

    @property
    def total_stone_weight(self):
        return sum((item.stone_weight for item in self.items.all()), Decimal('0.000'))
