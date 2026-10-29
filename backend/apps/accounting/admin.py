from django.contrib import admin
from .models import GoldRate, Customer, DayBook

admin.site.register(GoldRate)
admin.site.register(Customer)

@admin.register(DayBook)
class DayBookAdmin(admin.ModelAdmin):
    list_display = ['date', 'branch', 'opening_balance', 'cash_in', 'cash_out', 'closing_balance', 'is_closed']
    list_filter = ['is_closed', 'branch']
