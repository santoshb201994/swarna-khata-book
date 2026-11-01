import logging
import re
import uuid
from decimal import Decimal
from typing import Dict, Any, Optional
from django.db import connection, transaction
from django_tenants.utils import schema_context, get_tenant_model, get_tenant_domain_model
from apps.tenants.models import Client, Domain
from apps.accounts.models import User, Branch
from apps.products.models import Category, Purity, Product
from apps.accounting.models import ShopRateSetting
from ninja_api.auth import create_token

logger = logging.getLogger(__name__)


def generate_schema_name(shop_name: str) -> str:
    """
    Sanitize and generate a safe, unique PostgreSQL schema name.
    Schema names must start with a letter and contain only lowercase letters, digits, and underscores.
    """
    base_slug = re.sub(r'[^a-z0-9_]', '', shop_name.strip().lower().replace(' ', '_'))
    if not base_slug:
        base_slug = "store"

    candidate = f"t_{base_slug}"[:40]
    if not Client.objects.filter(schema_name=candidate).exists():
        return candidate

    short_suffix = uuid.uuid4().hex[:6]
    return f"t_{base_slug[:33]}_{short_suffix}"


class TenantProvisioningService:
    """
    Idempotent, Retry-Safe Multi-Tenant Provisioning Engine.

    State Progression:
    INITIALIZING -> PROVISIONING -> SEEDING -> (Validation) -> ACTIVE
    On Failure: -> FAILED (with error tracking & retry capabilities)
    """

    @classmethod
    def provision_store(
        cls,
        shop_name: str,
        owner_username: str,
        owner_password: str,
        owner_email: Optional[str] = "",
        owner_phone: Optional[str] = "",
        address: Optional[str] = "",
        gstin: Optional[str] = "",
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Idempotently provisions a complete tenant with dedicated PostgreSQL schema.
        Only activates the store after migrations, seeding, and verification succeed.
        """
        # 1. Idempotency Check
        if idempotency_key:
            existing = Client.objects.filter(idempotency_key=idempotency_key).first()
            if existing:
                if existing.provisioning_status == Client.ProvisioningStatus.ACTIVE:
                    logger.info("Idempotent hit for active store '%s' (key: %s)", existing.name, idempotency_key)
                    # Retrieve owner user
                    with schema_context(existing.schema_name):
                        owner = User.objects.filter(role=User.Role.OWNER).first()
                        access_tok = create_token(owner, token_type='access') if owner else ""
                        refresh_tok = create_token(owner, token_type='refresh') if owner else ""
                    return {
                        "schema_name": existing.schema_name,
                        "shop_name": existing.name,
                        "domain": getattr(existing.domains.first(), 'domain', ''),
                        "owner_username": owner.username if owner else owner_username,
                        "access": access_tok,
                        "refresh": refresh_tok,
                        "provisioning_status": existing.provisioning_status,
                        "is_idempotent_replay": True,
                        "message": f"Store '{existing.name}' is already active and verified."
                    }
                elif existing.provisioning_status == Client.ProvisioningStatus.FAILED:
                    logger.info("Retrying previously failed provisioning for '%s' (key: %s)", existing.name, idempotency_key)
                    return cls.retry_provisioning(existing.id, owner_password)

        schema_name = generate_schema_name(shop_name)
        domain_host = f"{schema_name}.swarnakhata.internal"

        # 2. Step 1: Initialize record in public schema
        with schema_context('public'):
            tenant = Client(
                schema_name=schema_name,
                name=shop_name.strip(),
                description=f"Jewellery retail showroom for {shop_name.strip()}",
                is_active=False, # Remains inactive until verified
                provisioning_status=Client.ProvisioningStatus.PROVISIONING,
                idempotency_key=idempotency_key
            )
            # auto_create_schema=True ensures django-tenants handles CREATE SCHEMA & migrate_schemas
            tenant.auto_create_schema = True
            tenant.save()

            Domain.objects.create(
                domain=domain_host,
                tenant=tenant,
                is_primary=True
            )

        # 3. Step 2 & 3: Provision and Seed within tenant schema
        try:
            with schema_context(schema_name):
                # A. Showroom Branch
                main_branch = Branch.objects.create(
                    name="Main Showroom",
                    address=address or "",
                    phone=owner_phone or "",
                    gstin=gstin or "",
                    is_active=True
                )

                # B. Owner User
                owner = User(
                    username=owner_username.strip(),
                    email=owner_email or "",
                    phone=owner_phone or "",
                    role=User.Role.OWNER,
                    branch=main_branch,
                    is_staff=True,
                    is_active=True
                )
                owner.set_password(owner_password)
                owner.save()

                # C. Categories
                for cat_name in ["Gold Jewellery", "Silver Ornaments", "Diamond Jewellery", "Platinum"]:
                    Category.objects.get_or_create(name=cat_name)

                # D. Standard Purities
                default_purities = [
                    ("24KT Pure Gold", Decimal('0.999')),
                    ("22KT Hallmarked 916", Decimal('0.916')),
                    ("18KT Diamond Studded", Decimal('0.750')),
                    ("925 Sterling Silver", Decimal('0.925')),
                ]
                for p_name, fineness in default_purities:
                    Purity.objects.get_or_create(name=p_name, defaults={'fineness': fineness})

                # E. Live Gold Rate Setting
                ShopRateSetting.objects.get_or_create(
                    branch=main_branch,
                    defaults={'preferred_source': 'ksjf'}
                )

                # F. Verification Check: Confirm table and owner integrity
                cls._validate_provisioning_integrity(schema_name, owner.id)

                # G. Issue authoritative JWT tokens
                owner.tenant_schema = schema_name
                access_tok = create_token(owner, token_type='access')
                refresh_tok = create_token(owner, token_type='refresh')

            # 4. Step 4: Promote to ACTIVE status
            with schema_context('public'):
                tenant.provisioning_status = Client.ProvisioningStatus.ACTIVE
                tenant.is_active = True
                tenant.provisioning_error = ""
                tenant.save(update_fields=['provisioning_status', 'is_active', 'provisioning_error'])

            logger.info("Store '%s' (%s) successfully provisioned and activated.", tenant.name, schema_name)
            return {
                "schema_name": schema_name,
                "shop_name": tenant.name,
                "domain": domain_host,
                "owner_username": owner.username,
                "access": access_tok,
                "refresh": refresh_tok,
                "provisioning_status": Client.ProvisioningStatus.ACTIVE,
                "is_idempotent_replay": False,
                "message": f"Store '{tenant.name}' registered successfully with isolated database schema."
            }

        except Exception as exc:
            logger.error("Provisioning failed for tenant '%s': %s", schema_name, exc, exc_info=True)
            with schema_context('public'):
                tenant.provisioning_status = Client.ProvisioningStatus.FAILED
                tenant.provisioning_error = str(exc)
                tenant.retry_count += 1
                tenant.is_active = False
                tenant.save(update_fields=['provisioning_status', 'provisioning_error', 'retry_count', 'is_active'])
            raise RuntimeError(f"Tenant provisioning failed: {str(exc)}")

    @classmethod
    def retry_provisioning(cls, tenant_id: int, owner_password: str) -> Dict[str, Any]:
        """
        Retries a failed tenant provisioning pipeline.
        """
        with schema_context('public'):
            tenant = Client.objects.filter(id=tenant_id).first()
            if not tenant:
                raise ValueError("Tenant not found.")
            tenant.retry_count += 1
            tenant.save(update_fields=['retry_count'])

        # Execute provisioning steps inside schema
        schema_name = tenant.schema_name
        with schema_context(schema_name):
            # Check or create branch
            branch, _ = Branch.objects.get_or_create(name="Main Showroom", defaults={'is_active': True})
            owner = User.objects.filter(role=User.Role.OWNER).first()
            if not owner:
                owner = User.objects.create(
                    username=f"owner_{schema_name[-6:]}",
                    role=User.Role.OWNER,
                    branch=branch,
                    is_staff=True,
                    is_active=True
                )
                owner.set_password(owner_password)
                owner.save()

            for cat_name in ["Gold Jewellery", "Silver Ornaments", "Diamond Jewellery", "Platinum"]:
                Category.objects.get_or_create(name=cat_name)

            default_purities = [
                ("24KT Pure Gold", Decimal('0.999')),
                ("22KT Hallmarked 916", Decimal('0.916')),
                ("18KT Diamond Studded", Decimal('0.750')),
                ("925 Sterling Silver", Decimal('0.925')),
            ]
            for p_name, fineness in default_purities:
                Purity.objects.get_or_create(name=p_name, defaults={'fineness': fineness})

            cls._validate_provisioning_integrity(schema_name, owner.id)
            owner.tenant_schema = schema_name
            access_tok = create_token(owner, token_type='access')
            refresh_tok = create_token(owner, token_type='refresh')

        with schema_context('public'):
            tenant.provisioning_status = Client.ProvisioningStatus.ACTIVE
            tenant.is_active = True
            tenant.provisioning_error = ""
            tenant.save(update_fields=['provisioning_status', 'is_active', 'provisioning_error'])

        domain_host = getattr(tenant.domains.first(), 'domain', f"{schema_name}.swarnakhata.internal")
        return {
            "schema_name": schema_name,
            "shop_name": tenant.name,
            "domain": domain_host,
            "owner_username": owner.username,
            "access": access_tok,
            "refresh": refresh_tok,
            "provisioning_status": Client.ProvisioningStatus.ACTIVE,
            "is_idempotent_replay": False,
            "message": f"Store '{tenant.name}' provisioned and activated on retry."
        }

    @classmethod
    def _validate_provisioning_integrity(cls, schema_name: str, owner_id: int):
        """
        Validates that required tables, owner, and relations are functional.
        """
        with schema_context(schema_name):
            owner = User.objects.filter(id=owner_id, is_active=True).first()
            if not owner:
                raise ValueError("Integrity check failed: Owner user not present.")
            # Verify core models can be queried without relation errors
            Category.objects.count()
            Purity.objects.count()
            Branch.objects.count()
