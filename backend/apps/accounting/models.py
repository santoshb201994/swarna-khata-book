from django.db import models
from decimal import Decimal


class GoldRate(models.Model):
    """Live gold rate entry — locked at time of sale"""
    purity = models.ForeignKey('products.Purity', on_delete=models.PROTECT, related_name='gold_rates')
    rate_per_gram = models.DecimalField(max_digits=10, decimal_places=2)
    effective_date = models.DateField()
    is_current = models.BooleanField(default=True)
    entered_by = models.ForeignKey(
        'accounts.User', null=True, on_delete=models.SET_NULL, related_name='gold_rates'
    )
    branch = models.ForeignKey(
        'accounts.Branch', null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-effective_date', '-created_at']
        indexes = [models.Index(fields=['purity', 'is_current'])]

    def __str__(self):
        return f"{self.purity.name}: ₹{self.rate_per_gram}/g on {self.effective_date}"

    def save(self, *args, **kwargs):
        if self.is_current:
            # Only one current rate per purity per branch
            GoldRate.objects.filter(
                purity=self.purity, branch=self.branch, is_current=True
            ).exclude(pk=self.pk).update(is_current=False)
        super().save(*args, **kwargs)


class Customer(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    pan_number = models.CharField(max_length=10, blank=True)
    aadhar_last4 = models.CharField(max_length=4, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.phone})"


class DayBook(models.Model):
    """Daily cash summary — one entry per business day per branch"""
    date = models.DateField()
    branch = models.ForeignKey(
        'accounts.Branch', null=True, blank=True, on_delete=models.SET_NULL
    )
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    cash_in = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    cash_out = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    closing_balance = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    is_closed = models.BooleanField(default=False)
    closed_by = models.ForeignKey(
        'accounts.User', null=True, blank=True, on_delete=models.SET_NULL
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['date', 'branch']]
        ordering = ['-date']

    def __str__(self):
        return f"Day Book {self.date} - {self.branch}"


class ShopRateSetting(models.Model):
    """Stores shop/tenant level preferences for bullion rate scraping source"""
    branch = models.OneToOneField(
        'accounts.Branch', null=True, blank=True, on_delete=models.CASCADE, related_name='rate_setting'
    )
    preferred_source = models.CharField(
        max_length=50, default='ksjf',
        help_text="Default rate scraping source identifier (e.g. 'ksjf', 'ibja')"
    )
    last_synced_at = models.DateTimeField(null=True, blank=True)
    last_synced_source = models.CharField(max_length=50, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Rate Setting: {self.preferred_source} ({self.branch})"

