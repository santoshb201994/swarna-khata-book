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
    current_schema = getattr(connection, 'schema_name', None)

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
    if current_schema and current_schema != 'public':
        payload['tenant_schema'] = current_schema

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
    Extracts Bearer token from HTTP Authorization header and resolves the user in the current tenant schema.
    """
    def authenticate(self, request, token):
        payload = decode_token(token, expected_type='access')
        if not payload:
            return None
        user_id = payload.get('user_id')
        if not user_id:
            return None

        # Ensure database connection matches the user's tenant schema if connection is currently public
        token_schema = payload.get('tenant_schema')
        from django.db import connection
        from django_tenants.utils import get_tenant_model
        curr_schema = getattr(connection, 'schema_name', None)
        if (not curr_schema or curr_schema == 'public') and token_schema and token_schema != 'public':
            tenant = get_tenant_model().objects.filter(schema_name=token_schema).first()
            if tenant:
                connection.set_tenant(tenant)
                request.tenant = tenant

        # If token belongs to platform superadmin, fetch from public schema
        if payload.get('is_superuser') or payload.get('role') == 'superadmin':
            from django_tenants.utils import schema_context
            with schema_context('public'):
                user = User.objects.select_related('branch').filter(id=user_id, is_active=True).first()
            if user:
                user.role = 'superadmin'
        else:
            user = User.objects.select_related('branch').filter(id=user_id, is_active=True).first()

        if not user:
            return None

        # Attach user to request for convenience
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


def require_role(user: User, allowed_roles: list[str]):
    """Enforces Role-Based Access Control (RBAC)"""
    if not user or not user.is_authenticated:
        raise PermissionError("Authentication required.")
    if user.is_superuser or user.role in allowed_roles:
        return True
    raise PermissionError(f"Access denied. Requires one of roles: {', '.join(allowed_roles)}")
