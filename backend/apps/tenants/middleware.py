import logging
from django.conf import settings
from django.db import connection
from django.http import Http404, HttpResponseNotFound
from django_tenants.middleware.main import TenantMainMiddleware
from django_tenants.utils import get_tenant_model, get_tenant_domain_model, get_public_schema_name

logger = logging.getLogger(__name__)


class ProductionTenantMiddleware(TenantMainMiddleware):
    """
    Production-grade Tenant Middleware supporting:
    1. Standard host/subdomain matching (e.g. shop1.swarnakhata.com)
    2. 'X-Tenant' HTTP header (e.g. X-Tenant: demo or X-Tenant-Domain: demo.localhost)
       for single-page apps (React), mobile QR scanner fallback, and API test suites.
    3. Graceful fallback for localhost / development environments.
    """

    def process_request(self, request):
        # 1. Connection check & initial setup
        connection.set_schema_to_public()
        tenant_model = get_tenant_model()
        domain_model = get_tenant_domain_model()
        public_schema = get_public_schema_name()

        # If targeting platform developer/superadmin endpoints, enforce public schema immediately
        if request.path.startswith('/api/developer/'):
            tenant = tenant_model.objects.filter(schema_name=public_schema).first()
            if tenant:
                request.tenant = tenant
                connection.set_tenant(tenant)
                return self.setup_url_routing(request)

        # 2. Check JWT token if present in Authorization header
        tenant = None
        auth_hdr = request.headers.get('Authorization') or request.META.get('HTTP_AUTHORIZATION', '')
        is_superadmin_token = False

        if auth_hdr.startswith('Bearer '):
            token_str = auth_hdr.split(' ', 1)[1]
            try:
                import jwt
                secret = getattr(settings, 'JWT_SECRET_KEY', settings.SECRET_KEY)
                payload = jwt.decode(token_str, secret, algorithms=['HS256'])
                is_superadmin_token = bool(payload.get('is_superuser') or payload.get('role') == 'superadmin')
                jwt_schema = payload.get('tenant_schema')
                # Route to signed JWT tenant_schema if valid and not public
                if jwt_schema and jwt_schema != public_schema:
                    tenant = tenant_model.objects.filter(schema_name=jwt_schema).first()
            except Exception:
                pass

        # 3. Check for explicit header override (for unauthenticated calls or superadmins switching context)
        if not tenant:
            header_schema = request.headers.get('X-Tenant') or request.META.get('HTTP_X_TENANT')
            header_domain = request.headers.get('X-Tenant-Domain') or request.META.get('HTTP_X_TENANT_DOMAIN')

            if header_schema:
                tenant = tenant_model.objects.filter(schema_name=header_schema).first()
            elif header_domain:
                domain_obj = domain_model.objects.select_related('tenant').filter(domain=header_domain).first()
                if domain_obj:
                    tenant = domain_obj.tenant

        # 4. Standard domain resolution from HTTP Host
        if not tenant:
            hostname = self.hostname_from_request(request)
            clean_host = hostname.split(':')[0]

            # In development or development Cloudflare Tunnel (localhost / 127.0.0.1 / testserver / trycloudflare.com in DEBUG),
            # for store API endpoints, auto-route to default tenant schema if not explicitly public/developer/tenants
            is_dev_tunnel = bool(getattr(settings, 'DEBUG', False) and clean_host.endswith('.trycloudflare.com'))
            if (
                (clean_host in ['localhost', '127.0.0.1', 'testserver'] or is_dev_tunnel)
                and request.path.startswith('/api/')
                and not (request.path.startswith('/api/tenants/') or request.path.startswith('/api/developer/'))
            ):
                tenant = tenant_model.objects.exclude(schema_name=public_schema).first()

            if not tenant:
                domain_obj = domain_model.objects.select_related('tenant').filter(domain=hostname).first()
                if domain_obj:
                    tenant = domain_obj.tenant
                else:
                    domain_obj = domain_model.objects.select_related('tenant').filter(domain=clean_host).first()
                    if domain_obj:
                        tenant = domain_obj.tenant
                    else:
                        tenant = tenant_model.objects.exclude(schema_name=public_schema).first()
                        if not tenant:
                            tenant = tenant_model.objects.filter(schema_name=public_schema).first()

        if not tenant:
            # If no tenant found at all, try public
            tenant = tenant_model.objects.filter(schema_name=public_schema).first()

        if not tenant:
            logger.warning(f"No tenant could be resolved for request to {request.get_host()}")
            return HttpResponseNotFound("Tenant not found. Please verify host or X-Tenant header.")

        request.tenant = tenant
        connection.set_tenant(request.tenant)
        logger.debug("Resolved tenant schema '%s' for %s", tenant.schema_name, request.path)

        # Apply tenant specific URLCONF if configured
        self.setup_url_routing(request)
