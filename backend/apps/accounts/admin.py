from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Branch

admin.site.register(Branch)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'email', 'role', 'branch', 'is_active']
    list_filter = ['role', 'branch', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'phone', 'branch')}),
    )
