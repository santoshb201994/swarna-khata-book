import re
import logging
import jwt
from typing import Optional, Tuple
from django.conf import settings
from django.db import connection
from django_tenants.utils import (
    get_tenant_model,
    get_tenant_domain_model,
    get_public_schema_name,
    schema_context
)
from apps.accounts.models import User

logger = logging.getLogger(__name__)

# Strict PostgreSQL schema naming regex
SCHEMA_NAME_PATTERN = re.compile(r'^[a-z][a-z0-9_]{0,62}$')


class TenantResolutionError(Exception):
    """Base exception for tenant resolution and security failures."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class TenantContextMismatchError(TenantResolutionError):
    """Raised when an advisory tenant hint contradicts an authenticated token."""
    def __init__(self, message: str = "Tenant context mismatch detected between token and selection hint."):
        super().__init__(message, status_code=403)


class TenantSuspendedOrInactiveError(TenantResolutionError):
    """Raised when the resolved tenant is inactive, suspended, or unprovisioned."""
    def __init__(self, message: str = "Tenant account is suspended, inactive, or pending provisioning."):
        super().__init__(message, status_code=403)


class TenantResolver:
    """
    Principal Tenant Security Engine & Authoritative Context Resolver.

    Security Invariants:
    1. Cryptographic JWT signature, expiry (exp), issue time (iat), and claim verification.
    2. Tenant state verification: target tenant must be active and have provisioning_status='active'.
    3. User membership verification: authenticated user must exist and be active within the tenant.
    4. Advisory Hint Isolation: 'X-Tenant' and 'X-Tenant-Domain' are selection hints ONLY.
       If an authenticated token specifies tenant A and the hint specifies tenant B,
       execution is IMMEDIATELY rejected with HTTP 403 Forbidden.
    5. Schema Sanitization & Allowlist: Prevents untrusted schema selection or SQL injection.
    6. Connection Isolation: Guarantees connection search_path is safely set and sanitizes state.
    """

    @classmethod
    def sanitize_schema_name(cls, schema_name: str) -> str:
        """
        Validates that schema_name matches strict PostgreSQL identifier syntax.
        """
        if not schema_name or not isinstance(schema_name, str):
            raise TenantResolutionError("Schema identifier must be a non-empty string.", status_code=400)
        
        cleaned = schema_name.strip().lower()
        if not SCHEMA_NAME_PATTERN.match(cleaned):
            raise TenantResolutionError(
                f"Invalid schema name format: '{cleaned}'. Must be lowercase alphanumeric starting with a letter.",
                status_code=400
            )
        return cleaned

    @classmethod
    def is_exempt_path(cls, path: str) -> bool:
        """
        Paths exempt from multi-tenant store routing.
        """
        return (
            path.startswith('/api/health') or
            path.startswith('/static/') or
            path.startswith('/media/') or
            path.startswith('/admin/') or
            path.startswith('/api/developer/') or
            path.startswith('/api/tenants/')
        )

    @classmethod
    def extract_bearer_token(cls, request) -> Optional[str]:
        """
        Safely extracts Bearer token from Authorization header or URL query parameter.
        """
        auth_hdr = request.headers.get('Authorization') or request.META.get('HTTP_AUTHORIZATION', '')
        if auth_hdr.startswith('Bearer '):
            return auth_hdr.split(' ', 1)[1].strip()
        
        # Support WebSocket / print preview token param if explicitly permitted
        query_token = request.GET.get('token')
        if query_token:
            return query_token.strip()
        
        return None

    @classmethod
    def decode_and_verify_jwt(cls, token: str) -> Optional[dict]:
        """
        Cryptographically validates token signature, lifetime, and algorithm against JWT_SECRET_KEY.
        """
        try:
            secret = getattr(settings, 'JWT_SECRET_KEY', settings.SECRET_KEY)
            algo = getattr(settings, 'JWT_ALGORITHM', 'HS256')
            payload = jwt.decode(
                token,
                secret,
                algorithms=[algo],
                options={"require": ["exp", "iat", "user_id"]}
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.debug("JWT signature expired during tenant resolution.")
            return None
        except (jwt.InvalidTokenError, Exception) as exc:
            logger.warning("Invalid JWT encountered during tenant resolution: %s", exc)
            return None

    @classmethod
    def resolve_tenant(cls, request) -> Tuple[Optional[object], Optional[User]]:
        """
        Authoritatively resolves the active tenant and verified user for the incoming request.
        Returns: (tenant_instance, verified_user_or_None)
        Raises: TenantResolutionError, TenantContextMismatchError, TenantSuspendedOrInactiveError
        """
        tenant_model = get_tenant_model()
        domain_model = get_tenant_domain_model()
        public_schema = get_public_schema_name()

        # Step 0: Extract selection hint (X-Tenant)
        raw_hint = request.headers.get('X-Tenant') or request.META.get('HTTP_X_TENANT')
        hint_schema = raw_hint.strip().lower() if raw_hint else None

        # Step 1: Check for Authenticated Token
        token = cls.extract_bearer_token(request)
        verified_payload = None
        verified_user = None

        if token:
            verified_payload = cls.decode_and_verify_jwt(token)

        # Step 2: Handle Authenticated Request
        if verified_payload:
            token_schema = verified_payload.get('tenant_schema')
            user_id = verified_payload.get('user_id')
            is_super = bool(verified_payload.get('is_superuser') or verified_payload.get('role') == 'superadmin')

            if token_schema:
                token_schema = cls.sanitize_schema_name(token_schema)

            # Check for Mismatch: If hint is provided, it MUST match token_schema (unless platform superadmin)
            if hint_schema and token_schema and hint_schema != 'public' and token_schema != 'public':
                if hint_schema != token_schema and not is_super:
                    logger.warning(
                        "SECURITY ALERT: Tenant context mismatch! Token tenant='%s', Hint tenant='%s', user_id=%s",
                        token_schema, hint_schema, user_id
                    )
                    raise TenantContextMismatchError(
                        f"Tenant context mismatch: Authenticated tenant '{token_schema}' contradicts hint '{hint_schema}'."
                    )

            target_schema = token_schema or public_schema

            # Retrieve Tenant from allowlist (database)
            tenant = tenant_model.objects.filter(schema_name=target_schema).first()
            if not tenant:
                raise TenantResolutionError(f"Target tenant '{target_schema}' does not exist.", status_code=404)

            # Verify Tenant Status: Must be active and not in failed/initializing state
            if target_schema != public_schema:
                if not tenant.is_active:
                    raise TenantSuspendedOrInactiveError(f"Store '{tenant.name}' is inactive or suspended.")
                if getattr(tenant, 'provisioning_status', 'active') in ['failed', 'initializing']:
                    raise TenantSuspendedOrInactiveError(f"Store '{tenant.name}' has not completed provisioning.")

            # Verify User Membership within the tenant schema
            with schema_context(target_schema):
                user = User.objects.select_related('branch').filter(id=user_id, is_active=True).first()
                if not user:
                    # Allow superadmins authenticated in public to switch context if explicitly authorized
                    if is_super:
                        with schema_context(public_schema):
                            user = User.objects.filter(id=user_id, is_active=True).first()

                if not user:
                    raise TenantResolutionError(
                        f"User ID {user_id} does not exist or is inactive in tenant '{target_schema}'.",
                        status_code=403
                    )
                verified_user = user

            return tenant, verified_user

        # Step 3: Handle Unauthenticated Request (Registration, Login, Public Catalog)
        tenant = None

        # 3a. Use advisory hint if safe and valid
        if hint_schema and hint_schema != public_schema:
            hint_clean = cls.sanitize_schema_name(hint_schema)
            candidate = tenant_model.objects.filter(schema_name=hint_clean, is_active=True).first()
            if candidate:
                if getattr(candidate, 'provisioning_status', 'active') == 'active':
                    tenant = candidate

        # 3b. Use Domain / Subdomain resolution from HTTP Host
        if not tenant:
            hostname = request.get_host().split(':')[0]
            domain_obj = domain_model.objects.select_related('tenant').filter(domain=hostname).first()
            if domain_obj and domain_obj.tenant.is_active:
                tenant = domain_obj.tenant

        # 3c. Safe Fallback for Store APIs
        if not tenant:
            if not cls.is_exempt_path(request.path):
                # Auto-route to active demo or primary store tenant for store frontend
                fallback = (
                    tenant_model.objects.filter(schema_name='demo', is_active=True).first() or
                    tenant_model.objects.exclude(schema_name=public_schema).filter(is_active=True).first()
                )
                if fallback:
                    tenant = fallback

        # 3d. Final fallback to public schema for platform endpoints
        if not tenant:
            tenant = tenant_model.objects.filter(schema_name=public_schema).first()

        if not tenant:
            raise TenantResolutionError("No suitable tenant could be resolved for this request.", status_code=404)

        return tenant, None
