from django.contrib import admin
from .models import Sale, SaleItem, Payment


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    readonly_fields = ['product_name', 'sku', 'purity', 'gross_weight', 'net_weight',
                       'gold_rate_per_gram', 'making_charge', 'unit_price', 'total_price']
    extra = 0


class PaymentInline(admin.TabularInline):
    model = Payment
    readonly_fields = ['method', 'amount', 'reference', 'paid_at']
    extra = 0


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'customer', 'total_amount', 'payment_status', 'sale_status', 'sale_date']
    list_filter = ['payment_status', 'sale_status', 'branch']
    search_fields = ['invoice_number', 'customer__name']
    readonly_fields = ['invoice_number', 'sale_date', 'subtotal', 'cgst_amount', 'sgst_amount',
                       'total_amount', 'amount_paid', 'balance_due']
    inlines = [SaleItemInline, PaymentInline]
