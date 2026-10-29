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
