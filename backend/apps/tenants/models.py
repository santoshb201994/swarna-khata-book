from django.db import models
from django_tenants.models import TenantMixin, DomainMixin


class Client(TenantMixin):
    """
    Tenant model representing a jewellery enterprise / jewellery retail shop tenant.
    Each client gets its own isolated PostgreSQL schema.
    """
    class ProvisioningStatus(models.TextChoices):
        INITIALIZING = 'initializing', 'Initializing'
        PROVISIONING = 'provisioning', 'Provisioning Schema'
        SEEDING = 'seeding', 'Seeding Initial Data'
        ACTIVE = 'active', 'Active & Verified'
        FAILED = 'failed', 'Provisioning Failed'

    name = models.CharField(max_length=150, help_text="Business / Store display name")
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_on = models.DateField(auto_now_add=True)

    provisioning_status = models.CharField(
        max_length=20,
        choices=ProvisioningStatus.choices,
        default=ProvisioningStatus.ACTIVE,
        db_index=True
    )
    provisioning_error = models.TextField(blank=True, default='')
    retry_count = models.PositiveSmallIntegerField(default=0)
    idempotency_key = models.CharField(max_length=64, blank=True, null=True, unique=True, db_index=True)
    last_migrated_at = models.DateTimeField(null=True, blank=True)
    last_migration_status = models.CharField(max_length=20, blank=True, default='success')

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
