from typing import Optional
from datetime import datetime, date
from django.http import FileResponse, HttpResponse
from ninja import Router
from ninja.errors import HttpError

from ninja_api.auth import jwt_auth, require_role
from apps.tenants.export_service import (
    generate_shop_export_archive,
    generate_all_shops_export_archive,
    CleanupFile
)

router = Router(tags=["Data Export Vault & Statutory Backups"])


def _parse_date(date_str: Optional[str], param_name: str) -> Optional[date]:
    if not date_str or not date_str.strip():
        return None
    try:
        return datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
    except ValueError:
        raise HttpError(400, f"Invalid {param_name} format. Expected YYYY-MM-DD (e.g. 2026-03-31).")


@router.get("/export/shop/", auth=jwt_auth)
def export_shop_data(request, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """
    Export all operational, billing, inventory, and customer data for the caller's shop
    within the specified date range.
    Restricted to Store Owner (Level 80) and Platform Superadmin (Level 100).
    Streams a compressed ZIP file containing Excel-compatible UTF-8 CSVs and a manifest.
    """
    require_role(request.auth, ['owner', 'superadmin'])

    start = _parse_date(start_date, 'start_date')
    end = _parse_date(end_date, 'end_date')

    if start and end and start > end:
        raise HttpError(400, "start_date cannot be later than end_date.")

    # Determine tenant schema
    schema_name = getattr(request.tenant, 'schema_name', None) if hasattr(request, 'tenant') else None
    if not schema_name or schema_name == 'public':
        schema_name = getattr(request.auth, 'tenant_schema', None)
    if not schema_name or schema_name == 'public':
        schema_name = 'demo'

    temp_path = generate_shop_export_archive(schema_name, start_date=start, end_date=end)

    date_label = f"{start or 'all'}_to_{end or 'current'}"
    filename = f"swarna_export_{schema_name}_{date_label}.zip"

    cleanup_file = CleanupFile(temp_path)
    response = FileResponse(cleanup_file, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@router.get("/export/all-shops/", auth=jwt_auth)
def export_all_shops_data(request, start_date: Optional[str] = None, end_date: Optional[str] = None):
    """
    Global multi-store data export for platform developers.
    Iterates through all active tenant schemas and generates an isolated folder per store.
    Strictly restricted to Platform Superadmin (Level 100).
    Streams a compressed ZIP file with a global manifest.
    """
    require_role(request.auth, ['superadmin'])

    start = _parse_date(start_date, 'start_date')
    end = _parse_date(end_date, 'end_date')

    if start and end and start > end:
        raise HttpError(400, "start_date cannot be later than end_date.")

    temp_path = generate_all_shops_export_archive(start_date=start, end_date=end)

    date_label = f"{start or 'all'}_to_{end or 'current'}"
    filename = f"swarna_global_all_shops_export_{date_label}.zip"

    cleanup_file = CleanupFile(temp_path)
    response = FileResponse(cleanup_file, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
