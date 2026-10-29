from django.contrib import admin
from .models import StockMovement, StockSummary

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'movement_type', 'quantity', 'reference_type', 'created_at']
    list_filter = ['movement_type']
    readonly_fields = ['created_at']

@admin.register(StockSummary)
class StockSummaryAdmin(admin.ModelAdmin):
    list_display = ['product', 'quantity_on_hand', 'updated_at']
    readonly_fields = ['updated_at']
