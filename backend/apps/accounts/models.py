from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPERADMIN = 'superadmin', 'Super Admin'
        OWNER = 'owner', 'Owner'
        MANAGER = 'manager', 'Manager'
        STAFF = 'staff', 'Staff'
        ACCOUNTANT = 'accountant', 'Accountant'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.STAFF)
    phone = models.CharField(max_length=15, blank=True)
    branch = models.ForeignKey(
        'Branch', null=True, blank=True, on_delete=models.SET_NULL, related_name='users'
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Branch(models.Model):
    name = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    gstin = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Branches'

    def __str__(self):
        return self.name
