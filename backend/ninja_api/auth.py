import jwt
from datetime import datetime, timezone, timedelta
from django.conf import settings
from ninja.security import HttpBearer
from apps.accounts.models import User


def create_token(user: User, token_type: str = 'access') -> str:
    now = datetime.now(timezone.utc)
    lifetime = (
        settings.JWT_ACCESS_TOKEN_LIFETIME
        if token_type == 'access'
        else settings.JWT_REFRESH_TOKEN_LIFETIME
    )
    exp = now + lifetime
    from django.db import connection
    current_schema = getattr(user, 'tenant_schema', None) or getattr(connection, 'schema_name', None)

    role = 'superadmin' if (user.is_superuser or user.role == 'superadmin') else user.role
    payload = {
        'user_id': user.id,
        'username': user.username,
        'role': role,
        'is_superuser': bool(user.is_superuser),
        'branch_id': user.branch_id,
        'token_type': token_type,
        'iat': int(now.timestamp()),
        'exp': int(exp.timestamp()),
    }
    if current_schema:
        payload['tenant_schema'] = current_schema
    else:
        payload['tenant_schema'] = 'public'

    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str, expected_type: str = 'access') -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"require": ["exp", "iat", "user_id"]}
        )
        if payload.get('token_type') != expected_type:
            return None
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


class JWTAuth(HttpBearer):
    """
    Production-grade Bearer Token Authentication for Django Ninja.
    Extracts Bearer token from HTTP Authorization header or query parameter ('token'),
    and resolves the user in the current tenant schema.
    """
    def __call__(self, request):
        auth_value = request.headers.get("Authorization")
        token = None
        if auth_value:
            parts = auth_value.split(" ")
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]
        if not token:
            token = request.GET.get("token")
        if not token:
            return None
        return self.authenticate(request, token)

    def authenticate(self, request, token):
        payload = decode_token(token, expected_type='access')
        if not payload:
            return None
        user_id = payload.get('user_id')
        if not user_id:
            return None

        is_super = bool(payload.get('is_superuser') or payload.get('role') == 'superadmin')
        token_schema = payload.get('tenant_schema')
        from django.db import connection
        from django_tenants.utils import get_tenant_model, schema_context
        curr_schema = getattr(connection, 'schema_name', None)

        # Multi-Tenant Isolation Enforcement:
        # Route to the tenant schema encoded in the signed token, or public for platform superadmin
        if token_schema and token_schema != 'public':
            if curr_schema != token_schema:
                tenant = get_tenant_model().objects.filter(schema_name=token_schema).first()
                if not tenant:
                    return None
                connection.set_tenant(tenant)
                request.tenant = tenant
            user = User.objects.select_related('branch').filter(id=user_id, is_active=True).first()
        else:
            with schema_context('public'):
                user = User.objects.select_related('branch').filter(id=user_id, is_active=True).first()
            if user:
                user.role = 'superadmin'

        if not user:
            return None

        user.tenant_schema = token_schema or getattr(connection, 'schema_name', 'public')
        request.user = user
        return user


# Singleton instance
jwt_auth = JWTAuth()


# ==============================================================================
# BILL SESSION JWT & TENANT DYNAMIC ROUTING
# ==============================================================================

def generate_bill_token(tenant_schema: str, bill_id, lifetime_hours: int = 4) -> str:
    """
    Generates a cryptographically signed JWT scoped to a specific Bill and Tenant Schema.
    Used for pairing laptop POS with mobile phone QR scanners.
    """
    now = datetime.now(timezone.utc)
    exp = now + timedelta(hours=lifetime_hours)
    payload = {
        'tenant_schema': str(tenant_schema),
        'bill_id': str(bill_id),
        'scope': 'bill_session',
        'iat': int(now.timestamp()),
        'exp': int(exp.timestamp()),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


class BillJWTAuth(HttpBearer):
    """
    Authoritative Bearer Token authentication for POS Bill polling & mobile QR scanner.
    1. Decodes and verifies scoped bill JWT token.
    2. Dynamically activates the PostgreSQL tenant schema.
    3. Validates path bill_id matching token's bill_id.
    """
    def authenticate(self, request, token):
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
                options={"require": ["exp", "iat", "tenant_schema", "bill_id"]}
            )
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return None

        if payload.get('scope') != 'bill_session':
            return None

        tenant_schema = payload.get('tenant_schema')
        bill_id = payload.get('bill_id')

        # 1. Dynamic Tenant Schema Routing
        if tenant_schema:
            from django_tenants.utils import get_tenant_model
            from django.db import connection
            tenant_model = get_tenant_model()
            tenant = tenant_model.objects.filter(schema_name=tenant_schema).first()
            if not tenant:
                return None
            request.tenant = tenant
            connection.set_tenant(tenant)

        # 2. Path parameter validation (if bill_id is in URL kwargs)
        path_bill_id = None
        if hasattr(request, 'resolver_match') and request.resolver_match:
            path_bill_id = request.resolver_match.kwargs.get('bill_id')

        if path_bill_id and str(path_bill_id) != str(bill_id):
            return None

        request.bill_id = bill_id
        request.tenant_schema = tenant_schema
        return payload


bill_jwt_auth = BillJWTAuth()


# ==============================================================================
# HIERARCHICAL ROLE-BASED ACCESS CONTROL (RBAC)
# ==============================================================================

ROLE_LEVELS: dict[str, int] = {
    'superadmin': 100,
    'owner': 80,
    'manager': 60,
    'accountant': 40,
    'staff': 20,
}

# Role inheritance: a superior role inherits all capabilities of subordinate roles
ROLE_HIERARCHY: dict[str, set[str]] = {
    'superadmin': {'superadmin', 'owner', 'manager', 'accountant', 'staff'},
    'owner': {'owner', 'manager', 'accountant', 'staff'},
    'manager': {'manager', 'staff'},
    'accountant': {'accountant', 'staff'},
    'staff': {'staff'},
}


def require_role(user: User, allowed_roles: list[str]):
    """
    Enforces Hierarchical Role-Based Access Control (RBAC).
    A user has access if their active role or any role inherited through the
    hierarchy is present in allowed_roles.
    Superusers and platform superadmins possess root access across all roles.
    """
    if not user or not user.is_authenticated:
        raise PermissionError("Authentication required.")

    if user.is_superuser or user.role == 'superadmin':
        return True

    effective_roles = ROLE_HIERARCHY.get(user.role, {user.role})
    if any(role in effective_roles for role in allowed_roles):
        return True

    raise PermissionError(f"Access denied. Requires one of roles: {', '.join(allowed_roles)}")


def require_branch_access(user: User, branch_id) -> bool:
    """
    Enforces Multi-Branch Store Isolation:
    - Superadmins and Store Owners have universal access to all branches within the store tenant.
    - Managers, Accountants, and Staff are strictly restricted to their assigned branch.
    - If user has no branch assigned or target branch_id differs from their assigned branch,
      raises PermissionError (HTTP 403).
    """
    if not user or not user.is_authenticated:
        raise PermissionError("Authentication required.")

    if user.is_superuser or user.role in ['superadmin', 'owner']:
        return True

    if not branch_id:
        return True

    if not user.branch_id:
        raise PermissionError("User is not assigned to any branch.")

    if str(user.branch_id) != str(branch_id):
        raise PermissionError(
            f"Branch access violation: User is assigned to Branch {user.branch_id}, "
            f"cannot operate on Branch {branch_id}."
        )

    return True

