from typing import List, Optional
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError

from apps.accounts.models import User, Branch
from ninja_api.auth import create_token, decode_token, jwt_auth, require_role, ROLE_LEVELS, ROLE_HIERARCHY
from ninja_api.schemas import (
    TokenRequest, TokenRefreshRequest, TokenResponse, UserInfo,
    UserCreateIn, UserDetailOut, BranchIn, BranchOut,
    PasswordResetIn, PasswordChangeIn, StaffStatusUpdateIn
)

router = Router(tags=["Authentication & Account Management"])


# ==============================================================================
# AUTHENTICATION
# ==============================================================================

@router.post("/auth/token/", response={200: TokenResponse, 401: dict}, auth=None)
def obtain_token(request, payload: TokenRequest):
    """
    Authenticate user with credentials and issue JWT access & refresh tokens.
    Operates within the active tenant schema with cross-tenant resolution for tenant users.
    """
    user = authenticate(request, username=payload.username, password=payload.password)
    resolved_schema = None

    if not user:
        # Check across active tenant schemas if username/password matches
        from apps.tenants.models import Client
        from django_tenants.utils import schema_context
        from django.db import connection

        for tenant in Client.objects.filter(is_active=True).exclude(schema_name='public'):
            with schema_context(tenant.schema_name):
                matched_user = authenticate(request, username=payload.username, password=payload.password)
                if matched_user and matched_user.is_active:
                    user = matched_user
                    resolved_schema = tenant.schema_name
                    connection.set_tenant(tenant)
                    request.tenant = tenant
                    break

    if not user:
        # Check if platform superadmin exists in public schema
        from django_tenants.utils import schema_context
        with schema_context('public'):
            public_user = authenticate(request, username=payload.username, password=payload.password)
            if public_user and public_user.is_active and (public_user.is_superuser or public_user.role == 'superadmin'):
                user = public_user
                resolved_schema = 'public'

    if not user or not user.is_active:
        return 401, {"error": "Invalid username or password, or account inactive."}

    from django.db import connection
    current_schema = resolved_schema or getattr(connection, 'schema_name', 'public')
    user.tenant_schema = current_schema

    access_token = create_token(user, token_type='access')
    refresh_token = create_token(user, token_type='refresh')
    effective_role = 'superadmin' if (user.is_superuser or user.role == 'superadmin') else user.role

    return 200, {
        "access": access_token,
        "refresh": refresh_token,
        "tenant_schema": current_schema,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": effective_role,
            "branch_id": user.branch_id,
            "tenant_schema": current_schema,
        }
    }


@router.post("/auth/token/refresh/", response={200: dict, 401: dict}, auth=None)
def refresh_token(request, payload: TokenRefreshRequest):
    """
    Exchange a valid JWT refresh token for a fresh access token.
    Securely activates the token's authoritative tenant schema.
    """
    claims = decode_token(payload.refresh, expected_type='refresh')
    if not claims:
        return 401, {"error": "Invalid or expired refresh token."}

    token_schema = claims.get('tenant_schema')
    is_super = bool(claims.get('is_superuser') or claims.get('role') == 'superadmin')
    from django_tenants.utils import schema_context, get_tenant_model
    from django.db import connection

    if is_super:
        with schema_context('public'):
            user = User.objects.filter(id=claims['user_id'], is_active=True).first()
    elif token_schema and token_schema != 'public':
        tenant = get_tenant_model().objects.filter(schema_name=token_schema).first()
        if not tenant:
            return 401, {"error": "Tenant database schema does not exist."}
        connection.set_tenant(tenant)
        user = User.objects.filter(id=claims['user_id'], is_active=True).first()
    else:
        user = User.objects.filter(id=claims['user_id'], is_active=True).first()

    if not user:
        return 401, {"error": "User no longer exists or is deactivated."}

    new_access = create_token(user, token_type='access')
    return 200, {
        "access": new_access,
        "refresh": payload.refresh,
        "tenant_schema": token_schema or getattr(connection, 'schema_name', 'public'),
    }


@router.get("/auth/me", response=UserDetailOut, auth=jwt_auth)
def get_current_user(request):
    """
    Get profile information of the currently authenticated user.
    """
    user = request.auth
    effective_role = 'superadmin' if (user.is_superuser or user.role == 'superadmin') else user.role
    from django.db import connection
    current_schema = getattr(user, 'tenant_schema', None) or getattr(connection, 'schema_name', 'public')
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": effective_role,
        "phone": user.phone,
        "branch_id": user.branch_id,
        "branch_name": user.branch.name if user.branch else None,
        "tenant_schema": current_schema,
        "is_active": user.is_active,
    }


# ==============================================================================
# USER MANAGEMENT (RBAC: Owner/Manager)
# ==============================================================================

@router.get("/users/", response=List[UserDetailOut], auth=jwt_auth)
def list_users(request):
    """List staff users in the current tenant shop."""
    require_role(request.auth, ['owner', 'manager'])
    users = User.objects.select_related('branch').all()
    results = []
    for u in users:
        results.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "role": u.role,
            "phone": u.phone,
            "branch_id": u.branch_id,
            "branch_name": u.branch.name if u.branch else None,
            "is_active": u.is_active,
        })
    return results


@router.post("/users/", response={201: UserDetailOut, 400: dict}, auth=jwt_auth)
def create_user(request, payload: UserCreateIn):
    """Create a new staff / cashier / accountant user in this tenant."""
    require_role(request.auth, ['owner', 'manager'])

    # Enforce role hierarchy: cannot create a user with a role equal to or higher than caller
    caller_role = request.auth.role
    caller_level = 100 if request.auth.is_superuser else ROLE_LEVELS.get(caller_role, 0)
    target_level = ROLE_LEVELS.get(payload.role, 0)

    if target_level >= caller_level and not request.auth.is_superuser:
        return 400, {"error": f"Hierarchy violation: Your role '{caller_role}' cannot create accounts with role '{payload.role}'."}

    if User.objects.filter(username=payload.username).exists():
        return 400, {"error": f"Username '{payload.username}' is already taken."}

    user = User(
        username=payload.username,
        email=payload.email,
        first_name=payload.first_name,
        last_name=payload.last_name,
        role=payload.role,
        phone=payload.phone,
        branch_id=payload.branch_id,
    )
    user.set_password(payload.password)
    user.save()

    return 201, {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "role": user.role,
        "phone": user.phone,
        "branch_id": user.branch_id,
        "branch_name": user.branch.name if user.branch else None,
        "is_active": user.is_active,
    }


@router.post("/users/{user_id}/toggle-status/", response={200: UserDetailOut, 400: dict}, auth=jwt_auth)
def toggle_user_status(request, user_id: int, payload: StaffStatusUpdateIn):
    """
    Activate or deactivate a staff/salesman user.
    Owners cannot deactivate their own account or users of equal/higher hierarchy.
    """
    require_role(request.auth, ['owner', 'superadmin'])
    target_user = get_object_or_404(User, id=user_id)
    if target_user.id == request.auth.id:
        return 400, {"error": "You cannot deactivate your own account."}

    caller_level = 100 if request.auth.is_superuser else ROLE_LEVELS.get(request.auth.role, 0)
    target_level = 100 if target_user.is_superuser else ROLE_LEVELS.get(target_user.role, 0)
    if target_level >= caller_level and not request.auth.is_superuser:
        return 400, {"error": f"Hierarchy violation: Cannot modify account status of user with role '{target_user.role}'."}

    target_user.is_active = payload.is_active
    target_user.save(update_fields=['is_active'])

    return 200, {
        "id": target_user.id,
        "username": target_user.username,
        "email": target_user.email,
        "first_name": target_user.first_name,
        "last_name": target_user.last_name,
        "role": target_user.role,
        "phone": target_user.phone,
        "branch_id": target_user.branch_id,
        "branch_name": target_user.branch.name if target_user.branch else None,
        "is_active": target_user.is_active,
    }


@router.post("/users/{user_id}/reset-password/", response={200: dict, 400: dict}, auth=jwt_auth)
def reset_staff_password(request, user_id: int, payload: PasswordResetIn):
    """
    Reset a staff member's password by Store Owner / Manager.
    Enforces the Jewellery Shield Password Policy via Pydantic validator.
    Strictly forbids resetting passwords of equal or higher hierarchy roles.
    """
    require_role(request.auth, ['owner', 'manager', 'superadmin'])
    target_user = get_object_or_404(User, id=user_id)

    caller_level = 100 if request.auth.is_superuser else ROLE_LEVELS.get(request.auth.role, 0)
    target_level = 100 if target_user.is_superuser else ROLE_LEVELS.get(target_user.role, 0)
    if target_level >= caller_level and not request.auth.is_superuser:
        return 400, {"error": f"Hierarchy violation: Cannot reset password for user with equal or higher role '{target_user.role}'."}

    target_user.set_password(payload.new_password)
    target_user.save(update_fields=['password'])
    return 200, {"success": True, "message": f"Password for {target_user.username} has been reset."}


@router.post("/auth/change-password/", response={200: dict, 400: dict}, auth=jwt_auth)
def change_own_password(request, payload: PasswordChangeIn):
    """
    Change currently authenticated user's password.
    Requires current password verification and validates new password policy.
    """
    user = request.auth
    if not user.check_password(payload.current_password):
        return 400, {"error": "Incorrect current password."}

    user.set_password(payload.new_password)
    user.save(update_fields=['password'])
    return 200, {"success": True, "message": "Password changed successfully."}


# ==============================================================================
# BRANCHES
# ==============================================================================

@router.get("/branches/", response=List[BranchOut], auth=jwt_auth)
def list_branches(request):
    """List all retail branches / showrooms for this tenant."""
    return Branch.objects.filter(is_active=True)


@router.post("/branches/", response={201: BranchOut, 400: dict}, auth=jwt_auth)
def create_branch(request, payload: BranchIn):
    """Register a new branch showroom (Owner / Manager only)."""
    require_role(request.auth, ['owner', 'manager'])
    branch = Branch.objects.create(
        name=payload.name,
        address=payload.address,
        phone=payload.phone,
        gstin=payload.gstin,
        is_active=payload.is_active,
    )
    return 201, branch


@router.get("/branches/{branch_id}/", response=BranchOut, auth=jwt_auth)
def get_branch(request, branch_id: int):
    """Get single branch details."""
    return get_object_or_404(Branch, id=branch_id)


@router.put("/branches/{branch_id}/", response=BranchOut, auth=jwt_auth)
def update_branch(request, branch_id: int, payload: BranchIn):
    """Update branch details."""
    require_role(request.auth, ['owner', 'manager'])
    branch = get_object_or_404(Branch, id=branch_id)
    branch.name = payload.name
    branch.address = payload.address
    branch.phone = payload.phone
    branch.gstin = payload.gstin
    branch.is_active = payload.is_active
    branch.save()
    return branch
