import time
import uuid
import logging
from django.db import connection

logger = logging.getLogger('swarnakhata.access')
perf_logger = logging.getLogger('swarnakhata.performance')


class RequestLoggingMiddleware:
    """
    Enterprise-grade Tenant-Aware HTTP Access & Query Performance Telemetry Middleware.

    Features:
    1. Attaches/propagates unique X-Request-ID for end-to-end tracing across services.
    2. Measures total request latency and identifies slow endpoints (> 500ms).
    3. Tracks tenant schema, authenticated user, branch ID, and client IP.
    4. Attaches correlation headers to HTTP response.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 1. Attach / propagate Request-ID
        request_id = request.headers.get('X-Request-ID') or str(uuid.uuid4())
        request.request_id = request_id

        start_time = time.monotonic()
        response = self.get_response(request)
        duration_ms = (time.monotonic() - start_time) * 1000

        # 2. Extract tenant context
        tenant_schema = '-'
        tenant_name = '-'
        if hasattr(request, 'tenant') and request.tenant:
            tenant_schema = getattr(request.tenant, 'schema_name', '-')
            tenant_name = getattr(request.tenant, 'name', '-')

        # 3. Extract user & branch context
        user_identity = '-'
        branch_id = '-'
        if hasattr(request, 'user') and getattr(request.user, 'is_authenticated', False):
            user_identity = request.user.username
            branch_id = getattr(request.user, 'branch_id', '-') or '-'
        elif hasattr(request, 'auth') and request.auth:
            user_identity = getattr(request.auth, 'username', str(request.auth))

        # 4. Extract client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            client_ip = x_forwarded_for.split(',')[0].strip()
        else:
            client_ip = request.META.get('REMOTE_ADDR', '-')

        status_code = getattr(response, 'status_code', 0)
        method = request.method
        path = request.get_full_path()

        log_msg = (
            f"[{request_id[:8]}] {method} {path} {status_code} ({duration_ms:.1f}ms) "
            f"[tenant: {tenant_schema}] [user: {user_identity}] [branch: {branch_id}] [ip: {client_ip}]"
        )

        if status_code >= 500:
            logger.error(log_msg)
        elif status_code >= 400:
            logger.warning(log_msg)
        else:
            logger.info(log_msg)

        # 5. Slow request performance threshold monitoring (> 500ms)
        if duration_ms > 500:
            perf_logger.warning(
                "SLOW_REQUEST_ALERT: [%s] %s %s took %.1fms for tenant '%s' (%s)",
                request_id[:8], method, path, duration_ms, tenant_schema, tenant_name
            )

        # 6. Attach correlation ID to response headers
        response['X-Request-ID'] = request_id
        return response
