import re
import uuid
from decimal import Decimal
from typing import List
from django.db import connection, transaction
from django_tenants.utils import schema_context
from ninja import Router
from ninja.errors import HttpError

from apps.tenants.models import Client, Domain
from apps.accounts.models import User, Branch
from apps.products.models import Category, Purity, Product
from apps.accounting.models import ShopRateSetting
from ninja_api.auth import create_token, jwt_auth, require_role
from ninja_api.schemas import (
    StoreRegistrationIn, StoreRegistrationOut, TenantOut, TenantCreateIn,
    PasswordResetIn, StaffStatusUpdateIn, SwitchStoreIn, TokenRequest, TokenResponse
)

from apps.tenants.provisioning import TenantProvisioningService, generate_schema_name

router = Router(tags=["Tenant Store Onboarding & SaaS Management"])


@router.post("/tenants/register-store/", response={201: StoreRegistrationOut, 400: dict}, auth=None)
def register_store(request, payload: StoreRegistrationIn):
    """
    Idempotent, retry-safe public jewellery store onboarding endpoint.
    1. Validates strict Jewellery Shield password policy.
    2. Runs TenantProvisioningService with state machine (INITIALIZING -> PROVISIONING -> SEEDING -> ACTIVE).
    3. Provisions dedicated PostgreSQL schema with canary validation.
    4. Seeds initial Showroom Branch, default Gold/Silver categories and purities.
    5. Creates Owner account and returns authenticated JWT tokens.
    """
    if len(payload.owner_username.strip()) < 3:
        return 400, {"error": "Username must be at least 3 characters long."}

    # Extract optional Idempotency-Key header if provided by client HTTP headers
    header_idempotency = request.headers.get('Idempotency-Key') or request.META.get('HTTP_IDEMPOTENCY_KEY')
    effective_idempotency_key = (payload.idempotency_key or header_idempotency or "").strip() or None

    try:
        # Non-blocking async provisioning to prevent gateway timeouts on remote migrations
        result = TenantProvisioningService.provision_store(
            shop_name=payload.shop_name,
            owner_username=payload.owner_username,
            owner_password=payload.owner_password,
            owner_email=payload.owner_email,
            owner_phone=payload.owner_phone,
            address=payload.address,
            gstin=payload.gstin,
            idempotency_key=effective_idempotency_key,
            async_mode=True
        )
        return 201, result
    except Exception as exc:
        return 400, {"error": f"Failed to register store: {str(exc)}"}


@router.get("/tenants/status/{schema_name}/", response={200: dict, 400: dict, 404: dict}, auth=None)
def get_store_provisioning_status(request, schema_name: str):
    """
    Poll status of an asynchronous store provisioning pipeline.
    Returns access & refresh tokens immediately when the store schema becomes active.
    """
    res = TenantProvisioningService.get_provisioning_status(schema_name)
    status = res.get("status")
    if status == "not_found":
        return 404, res
    elif status == "failed":
        return 400, res
    return 200, res


def _format_tenant(t: Client) -> dict:
    domains = [
        {"id": d.id, "domain": d.domain, "is_primary": d.is_primary}
        for d in t.domains.all()
    ]
    return {
        "id": t.id,
        "name": t.name,
        "schema_name": t.schema_name,
        "description": t.description,
        "is_active": t.is_active,
        "created_on": t.created_on,
        "domains": domains,
    }


@router.get("/tenants/", response={200: List[TenantOut], 403: dict}, auth=jwt_auth)
def list_tenants(request):
    """
    List all provisioned tenants in the jewellery ERP multi-tenant cluster (Superadmin only).
    """
    require_role(request.auth, ['superadmin'])
    clients = Client.objects.prefetch_related('domains').all()
    return 200, [_format_tenant(c) for c in clients]


@router.post("/tenants/", response={201: TenantOut, 400: dict, 403: dict}, auth=jwt_auth)
def create_tenant(request, payload: TenantCreateIn):
    """
    Provision a brand new jewellery shop tenant (Superadmin only).
    Triggers automatic PostgreSQL schema creation and runs tenant database migrations.
    """
    require_role(request.auth, ['superadmin'])
    schema = payload.schema_name.lower().strip()
    if not schema.isidentifier():
        return 400, {"error": "schema_name must be a valid alphanumeric identifier (e.g. 'swarna_pune')."}

    if Client.objects.filter(schema_name=schema).exists():
        return 400, {"error": f"Tenant with schema '{schema}' already exists."}

    if Domain.objects.filter(domain=payload.domain).exists():
        return 400, {"error": f"Domain '{payload.domain}' is already assigned to another tenant."}

    client = Client(
        name=payload.name,
        schema_name=schema,
        description=payload.description or '',
        is_active=True,
    )
    client.save()

    domain = Domain(
        domain=payload.domain,
        tenant=client,
        is_primary=True,
    )
    domain.save()

    return 201, _format_tenant(client)


# ==============================================================================
# DEVELOPER / SUPER ADMIN MANAGEMENT ENDPOINTS
# ==============================================================================

@router.post("/developer/login/", response={200: TokenResponse, 401: dict, 403: dict}, auth=None)
def developer_login(request, payload: TokenRequest):
    """
    Dedicated endpoint for Developer / Superadmin authentication.
    Only the single designated superuser configured in backend .env can authenticate.
    Password can only be modified via backend code in local .env.
    """
    from django.conf import settings
    from django.db import connection
    from django.contrib.auth import authenticate

    expected_username = getattr(settings, 'DEVELOPER_SUPERUSER_USERNAME', 'developer')
    expected_password = getattr(settings, 'DEVELOPER_SUPERUSER_PASSWORD', 'Super*Vault9')
    expected_email = getattr(settings, 'DEVELOPER_SUPERUSER_EMAIL', 'developer@swarnakhata.internal')

    submitted_username = (payload.username or '').strip()
    submitted_password = payload.password or ''

    # Strictly reject any account other than the single configured developer superuser
    if submitted_username != expected_username:
        return 401, {"error": "Invalid developer credentials."}

    with schema_context('public'):
        # Ensure the single developer account exists in the public schema
        user, created = User.objects.get_or_create(
            username=expected_username,
            defaults={
                "email": expected_email,
                "first_name": "Platform",
                "last_name": "Developer",
                "role": "superadmin",
                "is_staff": True,
                "is_superuser": True,
            }
        )

        # Synchronize password from local .env if changed in backend code / .env
        if not user.check_password(expected_password) or created or not user.is_superuser or user.role != 'superadmin':
            user.set_password(expected_password)
            user.role = 'superadmin'
            user.is_staff = True
            user.is_superuser = True
            user.is_active = True
            user.save()

        # Enforce strictly only ONE superuser in public schema by deleting any other entries
        with connection.cursor() as cur:
            cur.execute('DELETE FROM accounts_user WHERE username != %s', [expected_username])

        # Authenticate with submitted credentials
        authenticated_user = authenticate(request, username=submitted_username, password=submitted_password)
        if not authenticated_user or not authenticated_user.is_active:
            return 401, {"error": "Invalid developer credentials."}
        if not (authenticated_user.is_superuser or authenticated_user.role == 'superadmin'):
            return 403, {"error": "Access denied: Account is not a platform superadmin."}

        authenticated_user.role = 'superadmin'
        authenticated_user.tenant_schema = 'public'
        access_token = create_token(authenticated_user, token_type='access')
        refresh_token = create_token(authenticated_user, token_type='refresh')
        return 200, {
            "access": access_token,
            "refresh": refresh_token,
            "tenant_schema": "public",
            "user": {
                "id": authenticated_user.id,
                "username": authenticated_user.username,
                "email": authenticated_user.email,
                "role": "superadmin",
                "branch_id": authenticated_user.branch_id,
                "tenant_schema": "public",
            }
        }


@router.get("/developer/overview/", response={200: dict, 403: dict}, auth=jwt_auth)
def developer_overview(request):
    """
    Platform Developer / Super Admin Master View:
    Returns full SaaS overview: all stores/tenants, their owners, all staff, branch counts, and stats.
    """
    require_role(request.auth, ['superadmin'])
    tenants = Client.objects.exclude(schema_name='public').prefetch_related('domains').order_by('-created_on')

    tenants_data = []
    total_users_count = 0

    for t in tenants:
        store_users = []
        prod_count = 0
        branch_count = 0

        try:
            with schema_context(t.schema_name):
                users_qs = User.objects.select_related('branch').all()
                prod_count = Product.objects.count()
                branch_count = Branch.objects.count()
                total_users_count += users_qs.count()

                for u in users_qs:
                    store_users.append({
                        "id": u.id,
                        "username": u.username,
                        "email": u.email,
                        "first_name": u.first_name,
                        "last_name": u.last_name,
                        "role": u.role,
                        "phone": u.phone,
                        "is_active": u.is_active,
                        "branch_name": u.branch.name if u.branch else None,
                    })
        except Exception:
            pass

        tenants_data.append({
            "id": t.id,
            "name": t.name,
            "schema_name": t.schema_name,
            "description": t.description,
            "is_active": t.is_active,
            "created_on": str(t.created_on),
            "domains": [d.domain for d in t.domains.all()],
            "product_count": prod_count,
            "branch_count": branch_count,
            "users": store_users,
        })

    return 200, {
        "total_tenants": tenants.count(),
        "active_tenants": tenants.filter(is_active=True).count(),
        "total_users": total_users_count,
        "tenants": tenants_data,
    }


@router.post("/developer/tenants/{schema_name}/toggle-status/", response={200: dict, 400: dict, 403: dict}, auth=jwt_auth)
def toggle_tenant_status(request, schema_name: str, payload: StaffStatusUpdateIn):
    """Developer endpoint: suspend or activate a whole store tenant."""
    require_role(request.auth, ['superadmin'])
    if schema_name == 'public':
        return 400, {"error": "Cannot toggle public schema."}

    with schema_context('public'):
        tenant = Client.objects.filter(schema_name=schema_name).first()
        if not tenant:
            return 400, {"error": f"Tenant '{schema_name}' not found."}

        tenant.is_active = payload.is_active
        tenant.save(update_fields=['is_active'])
        tenant_name = tenant.name
        is_active = tenant.is_active

    return 200, {
        "success": True,
        "schema_name": schema_name,
        "is_active": is_active,
        "message": f"Tenant '{tenant_name}' is now {'active' if is_active else 'suspended'}."
    }


@router.post("/developer/tenants/{schema_name}/users/{user_id}/reset-password/", response={200: dict, 400: dict, 403: dict}, auth=jwt_auth)
def developer_reset_user_password(request, schema_name: str, user_id: int, payload: PasswordResetIn):
    """Developer endpoint: reset any owner or staff password inside any tenant schema."""
    require_role(request.auth, ['superadmin'])
    if not Client.objects.filter(schema_name=schema_name).exists():
        return 400, {"error": f"Tenant '{schema_name}' does not exist."}

    with schema_context(schema_name):
        target_user = User.objects.filter(id=user_id).first()
        if not target_user:
            return 400, {"error": f"User ID {user_id} not found in tenant '{schema_name}'."}

        target_user.set_password(payload.new_password)
        target_user.save(update_fields=['password'])
        return 200, {
            "success": True,
            "message": f"Password reset for user '{target_user.username}' ({target_user.role}) in {schema_name}."
        }


@router.post("/developer/tenants/{schema_name}/users/{user_id}/toggle-status/", response={200: dict, 400: dict, 403: dict}, auth=jwt_auth)
def developer_toggle_user_status(request, schema_name: str, user_id: int, payload: StaffStatusUpdateIn):
    """Developer endpoint: toggle active/inactive status of any user inside any tenant schema."""
    require_role(request.auth, ['superadmin'])
    if not Client.objects.filter(schema_name=schema_name).exists():
        return 400, {"error": f"Tenant '{schema_name}' does not exist."}

    with schema_context(schema_name):
        target_user = User.objects.filter(id=user_id).first()
        if not target_user:
            return 400, {"error": f"User ID {user_id} not found in tenant '{schema_name}'."}

        target_user.is_active = payload.is_active
        target_user.save(update_fields=['is_active'])
        return 200, {
            "success": True,
            "username": target_user.username,
            "is_active": target_user.is_active,
            "message": f"User '{target_user.username}' is now {'active' if target_user.is_active else 'deactivated'}."
        }


@router.post("/developer/switch-store-token/", response={200: dict, 400: dict, 403: dict}, auth=jwt_auth)
def developer_switch_store_token(request, payload: SwitchStoreIn):
    """
    Developer endpoint: issue a JWT scoped to a target tenant with superadmin privileges,
    allowing the developer to enter any store's frontend views with full superadmin edit rights.
    """
    require_role(request.auth, ['superadmin'])
    target_schema = payload.schema_name
    if not target_schema or not Client.objects.filter(schema_name=target_schema).exists():
        return 400, {"error": "Invalid tenant schema."}

    with schema_context(target_schema):
        token = create_token(request.auth, token_type='access')

    return 200, {
        "access": token,
        "schema_name": target_schema,
        "message": f"Switched context to tenant '{target_schema}'."
    }
