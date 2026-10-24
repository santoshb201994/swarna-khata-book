from ninja import NinjaAPI
from ninja.errors import ValidationError, HttpError
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse

from ninja_api.routers.auth_router import router as auth_router
from ninja_api.routers.products_router import router as products_router
from ninja_api.routers.stock_router import router as stock_router
from ninja_api.routers.billing_router import router as billing_router
from ninja_api.routers.accounting_router import router as accounting_router
from ninja_api.routers.qr_tags_router import router as qr_tags_router
from ninja_api.routers.pos_pairing_router import router as pos_pairing_router
from ninja_api.routers.tenants_router import router as tenants_router
from ninja_api.routers.bills_router import router as bills_router

api = NinjaAPI(
    title="Swarna Khata Jewellery ERP API",
    version="2.0.0",
    description=(
        "Production-grade Multi-Tenant Jewellery ERP, Billing & Khata Book API. "
        "Engineered with Django Ninja (Pydantic type-safety) and django-tenants (PostgreSQL schema isolation)."
    ),
    docs_url="/docs",
    openapi_url="/openapi.json",
)


# Exception Handlers
@api.exception_handler(PermissionError)
def permission_error_handler(request, exc):
    return api.create_response(
        request,
        {"error": str(exc)},
        status=403,
    )


@api.exception_handler(ValueError)
def value_error_handler(request, exc):
    return api.create_response(
        request,
        {"error": str(exc)},
        status=400,
    )


@api.exception_handler(ObjectDoesNotExist)
def not_found_handler(request, exc):
    return api.create_response(
        request,
        {"error": "Resource not found."},
        status=404,
    )


# Mount All Module Routers
api.add_router("/", auth_router)
api.add_router("/", products_router)
api.add_router("/", stock_router)
api.add_router("/", billing_router)
api.add_router("/", accounting_router)
api.add_router("/", qr_tags_router)
api.add_router("/", pos_pairing_router)
api.add_router("/", tenants_router)
api.add_router("/", bills_router)
