import time
import logging

logger = logging.getLogger('swarnakhata.access')


class RequestLoggingMiddleware:
    """
    Non-intrusive HTTP Request/Response logging middleware.
    Measures request duration, tracks tenant schema context, and logs access telemetry
    without modifying requests, responses, headers, or body parsing.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.monotonic()

        response = self.get_response(request)

        duration_ms = (time.monotonic() - start_time) * 1000

        # Safely extract tenant schema if resolved
        tenant_schema = '-'
        if hasattr(request, 'tenant') and request.tenant:
            tenant_schema = getattr(request.tenant, 'schema_name', '-')

        # Safely extract user identity
        user_identity = '-'
        if hasattr(request, 'user') and getattr(request.user, 'is_authenticated', False):
            user_identity = request.user.username
        elif hasattr(request, 'auth') and request.auth:
            user_identity = getattr(request.auth, 'username', str(request.auth))

        # Safely extract client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            client_ip = x_forwarded_for.split(',')[0].strip()
        else:
            client_ip = request.META.get('REMOTE_ADDR', '-')

        status_code = getattr(response, 'status_code', 0)
        method = request.method
        path = request.get_full_path()

        log_msg = (
            f"{method} {path} {status_code} ({duration_ms:.1f}ms) "
            f"[tenant: {tenant_schema}] [user: {user_identity}] [ip: {client_ip}]"
        )

        if status_code >= 500:
            logger.error(log_msg)
        elif status_code >= 400:
            logger.warning(log_msg)
        else:
            logger.info(log_msg)

        return response
