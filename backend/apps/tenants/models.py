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


class PasswordResetToken(models.Model):
    """
    Secure, single-use, expiring password-reset token registry.
    Stored exclusively in the public schema to support multi-tenant user resolution.
    Raw tokens are never stored; only cryptographic SHA-256 hashes are persisted.
    """
    user_id = models.IntegerField(db_index=True)
    user_email = models.EmailField(db_index=True)
    tenant_schema = models.CharField(max_length=63, default='public', db_index=True)
    token_hash = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)
    used_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['token_hash', 'expires_at']),
            models.Index(fields=['user_email', 'tenant_schema']),
        ]

    def is_valid(self) -> bool:
        from django.utils import timezone
        return self.used_at is None and self.expires_at > timezone.now()

    def __str__(self):
        return f"ResetToken({self.user_email} @ {self.tenant_schema}, valid={self.is_valid()})"
