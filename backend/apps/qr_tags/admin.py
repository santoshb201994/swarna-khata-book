from django.contrib import admin
from .models import QRTag

@admin.register(QRTag)
class QRTagAdmin(admin.ModelAdmin):
    list_display = ['product', 'printed_count', 'created_at']
    search_fields = ['product__sku', 'product__name']
    readonly_fields = ['qr_data', 'qr_image', 'printed_count', 'created_at', 'updated_at']
