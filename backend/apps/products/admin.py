from django.contrib import admin
from .models import Category, Purity, Product

admin.site.register(Category)
admin.site.register(Purity)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'sku', 'category', 'purity', 'gross_weight', 'net_weight', 'is_active']
    list_filter = ['category', 'purity', 'is_active']
    search_fields = ['name', 'sku', 'huid']
    readonly_fields = ['net_weight']
