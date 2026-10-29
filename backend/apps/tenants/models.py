from django.db import models
from django_tenants.models import TenantMixin, DomainMixin


class Client(TenantMixin):
    """
    Tenant model representing a jewellery enterprise / jewellery retail shop tenant.
    Each client gets its own isolated PostgreSQL schema.
    """
    name = models.CharField(max_length=150, help_text="Business / Store display name")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_on = models.DateField(auto_now_add=True)

    # Automatically create the PostgreSQL schema and apply migrations on save
    auto_create_schema = True
    auto_drop_schema = False

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.schema_name})"


class Domain(DomainMixin):
    """
    Domain routing model mapping hostnames/subdomains to tenants.
    """
    pass
