import logging
from django.conf import settings
from django.db import connection
from django.http import JsonResponse, HttpResponseNotFound
from django_tenants.middleware.main import TenantMainMiddleware
from django_tenants.utils import get_public_schema_name

from apps.tenants.resolver import (
    TenantResolver,
    TenantResolutionError,
    TenantContextMismatchError,
    TenantSuspendedOrInactiveError,
)

logger = logging.getLogger(__name__)


class ProductionTenantMiddleware(TenantMainMiddleware):
    """
    Production-grade Hardened Tenant Middleware.

    Key Security & Connection Guarantees:
    1. Delegates authoritative resolution to TenantResolver.
    2. Rejects cross-tenant mismatches (token vs X-Tenant hint) with 403 Forbidden.
    3. Blocks inactive, suspended, or unprovisioned tenants.
    4. Enforces Neon Connection Pool Safety: resets search_path to 'public' on response exit
       and on exceptions to prevent connection pollution and cross-tenant context leaks.
    """

    def process_request(self, request):
        # 0. Health check endpoint probe bypasses tenant resolution
        if request.path.startswith('/api/health'):
            return None

        # 1. Reset connection state to public baseline
        try:
            connection.set_schema_to_public()
        except Exception as e:
            logger.debug("Initial connection reset to public: %s", e)

        # 2. Authoritative Resolution
        try:
            tenant, verified_user = TenantResolver.resolve_tenant(request)
        except TenantContextMismatchError as exc:
            logger.warning("TenantContextMismatch: %s (path: %s)", exc.message, request.path)
            return JsonResponse({"error": exc.message, "code": "TENANT_CONTEXT_MISMATCH"}, status=403)
        except TenantSuspendedOrInactiveError as exc:
            logger.warning("TenantInactive: %s (path: %s)", exc.message, request.path)
            return JsonResponse({"error": exc.message, "code": "TENANT_INACTIVE"}, status=403)
        except TenantResolutionError as exc:
            logger.warning("TenantResolutionError: %s (path: %s)", exc.message, request.path)
            return JsonResponse({"error": exc.message, "code": "TENANT_RESOLUTION_ERROR"}, status=exc.status_code)
        except Exception as exc:
            logger.error("Unexpected error in TenantResolver: %s", exc, exc_info=True)
            return JsonResponse({"error": "Internal server error resolving store context."}, status=500)

        # 3. Bind authoritative tenant to request and database connection
        request.tenant = tenant
        if verified_user:
            request.user = verified_user

        connection.set_tenant(request.tenant)
        logger.debug("Resolved tenant schema '%s' for %s", tenant.schema_name, request.path)

        # Apply tenant specific URLCONF if configured
        return self.setup_url_routing(request)

    def process_response(self, request, response):
        """
        Neon Connection Pooler Safety Hook.
        Resets PostgreSQL search_path to public on request completion so pooled connections
        never leak tenant context into subsequent requests.
        """
        try:
            connection.set_schema_to_public()
        except Exception as exc:
            logger.debug("Could not reset search_path in process_response: %s", exc)
        return response

    def process_exception(self, request, exception):
        """
        Neon Connection Pooler Safety Hook on Unhandled Exceptions.
        Ensures search_path is always sanitized even when views crash.
        """
        try:
            connection.set_schema_to_public()
        except Exception as exc:
            logger.debug("Could not reset search_path in process_exception: %s", exc)
        return None
