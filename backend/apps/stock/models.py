from django.db import models
from decimal import Decimal


class StockMovement(models.Model):
    class MovementType(models.TextChoices):
        IN = 'IN', 'Stock In'
        OUT = 'OUT', 'Stock Out'
        RETURN = 'RETURN', 'Return'
        EXCHANGE = 'EXCHANGE', 'Exchange'
        ADJUSTMENT = 'ADJUSTMENT', 'Adjustment'

    product = models.ForeignKey(
        'products.Product', on_delete=models.PROTECT, related_name='stock_movements'
    )
    movement_type = models.CharField(max_length=20, choices=MovementType.choices)
    quantity = models.IntegerField(default=1)
    reference_type = models.CharField(max_length=50, blank=True, help_text='e.g. sale, purchase, adjustment')
    reference_id = models.BigIntegerField(null=True, blank=True)
    note = models.TextField(blank=True)
    created_by = models.ForeignKey(
        'accounts.User', null=True, on_delete=models.SET_NULL, related_name='stock_movements'
    )
    branch = models.ForeignKey(
        'accounts.Branch', null=True, blank=True, on_delete=models.SET_NULL, related_name='stock_movements'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'movement_type']),
            models.Index(fields=['reference_type', 'reference_id']),
        ]

    def __str__(self):
        return f"{self.movement_type} - {self.product.sku} ({self.created_at.date()})"


class StockSummary(models.Model):
    """Materialized current stock count per product"""
    product = models.OneToOneField(
        'products.Product', on_delete=models.CASCADE, related_name='stock_summary'
    )
    quantity_on_hand = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Stock Summaries'

    def __str__(self):
        return f"{self.product.sku}: {self.quantity_on_hand}"
