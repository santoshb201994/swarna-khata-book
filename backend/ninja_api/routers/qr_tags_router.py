import logging
import random
import string
import datetime
from decimal import Decimal
from typing import List, Optional
from django.shortcuts import get_object_or_404
from ninja import Router

logger = logging.getLogger(__name__)

from apps.qr_tags.models import QRTag, Tray
from apps.products.models import Product
from apps.qr_tags.services import (
    generate_qr_for_product,
    generate_qr_batch_async,
    generate_qr_for_tray,
)
from ninja_api.auth import jwt_auth
from ninja_api.schemas import (
    QRTagOut,
    BatchQRIn,
    TrayOut,
    CreateTrayIn,
    UpdateTrayIn,
)

router = Router(tags=["Jewellery Barcode & QR Tags"])


def _format_qrtag(request, tag: QRTag) -> dict:
    qr_url = request.build_absolute_uri(tag.qr_image.url) if tag.qr_image else None
    prod = tag.product
    return {
        "id": tag.id,
        "product_id": prod.id,
        "product_name": prod.name,
        "product_sku": prod.sku,
        "purity": prod.purity.name if prod.purity else None,
        "gross_weight": prod.gross_weight,
        "net_weight": prod.net_weight,
        "qr_data": tag.qr_data,
        "qr_image_url": qr_url,
        "printed_count": tag.printed_count,
        "created_at": tag.created_at,
        "updated_at": tag.updated_at,
    }


def _format_tray(request, tray: Tray) -> dict:
    qr_url = request.build_absolute_uri(tray.qr_image.url) if tray.qr_image else None

    # Fetch items with related data
    items_list = list(tray.items.select_related('purity', 'category', 'qr_tag').all())

    # Map item status using billing Item model
    item_status_map = {}
    try:
        from apps.billing.models import Item
        skus = [p.sku for p in items_list]
        if skus:
            item_status_map = {item.qr_code: item.status for item in Item.objects.filter(qr_code__in=skus)}
    except Exception as e:
        logger.warning("Could not query billing Item status map for tray: %s", e)

    items_out = []
    total_gross = Decimal('0.000')
    total_net = Decimal('0.000')
    total_stone = Decimal('0.000')

    for item in items_list:
        total_gross += item.gross_weight
        total_net += item.net_weight
        total_stone += item.stone_weight

        raw_status = item_status_map.get(item.sku)
        stock_qty = getattr(getattr(item, 'stock_summary', None), 'quantity_on_hand', None)
        if (stock_qty is not None and stock_qty <= 0) or not item.is_active or raw_status == 'SOLD':
            effective_status = 'SOLD'
        elif raw_status == 'IN_CART':
            effective_status = 'IN_CART'
        else:
            effective_status = 'AVAILABLE'

        tag = getattr(item, 'qr_tag', None)
        item_qr_url = request.build_absolute_uri(tag.qr_image.url) if (tag and tag.qr_image) else None
        photo_url = request.build_absolute_uri(item.photo.url) if item.photo else None

        items_out.append({
            "id": item.id,
            "sku": item.sku,
            "name": item.name,
            "category_name": item.category.name if item.category else None,
            "purity": item.purity.name if item.purity else None,
            "gross_weight": item.gross_weight,
            "net_weight": item.net_weight,
            "stone_weight": item.stone_weight,
            "huid": item.huid or None,
            "item_status": effective_status,
            "qr_code_url": item_qr_url,
            "photo_url": photo_url,
        })

    return {
        "id": tray.id,
        "code": tray.code,
        "name": tray.name,
        "description": tray.description or "",
        "total_items": len(items_out),
        "total_gross_weight": total_gross,
        "total_net_weight": total_net,
        "total_stone_weight": total_stone,
        "qr_data": tray.qr_data,
        "qr_image_url": qr_url,
        "printed_count": tray.printed_count,
        "items": items_out,
        "created_at": tray.created_at,
        "updated_at": tray.updated_at,
    }


def _generate_tray_code() -> str:
    year = datetime.date.today().year
    count = Tray.objects.count() + 1
    candidate = f"TRAY-{year}-{count:03d}"
    if not Tray.objects.filter(code=candidate).exists():
        return candidate
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"TRAY-{year}-{suffix}"


# ==============================================================================
# INDIVIDUAL PRODUCT QR TAGS
# ==============================================================================

@router.get("/qr-tags/", response=List[QRTagOut], auth=jwt_auth)
def list_qr_tags(request):
    tags = QRTag.objects.select_related('product', 'product__purity').all()[:100]
    return [_format_qrtag(request, t) for t in tags]


@router.get("/qr-tags/{tag_id}/", response=QRTagOut, auth=jwt_auth)
def get_qr_tag(request, tag_id: int):
    tag = get_object_or_404(
        QRTag.objects.select_related('product', 'product__purity'),
        id=tag_id
    )
    return _format_qrtag(request, tag)


@router.post("/qr-tags/{tag_id}/mark-printed/", response={200: dict}, auth=jwt_auth)
def mark_tag_printed(request, tag_id: int):
    """Increment label print count to track physical tag wastage & printing history."""
    tag = get_object_or_404(QRTag, id=tag_id)
    tag.printed_count += 1
    tag.save(update_fields=['printed_count'])
    return 200, {"printed_count": tag.printed_count}


@router.post("/qr-tags/{tag_id}/regenerate/", response=QRTagOut, auth=jwt_auth)
def regenerate_tag(request, tag_id: int):
    tag = get_object_or_404(QRTag, id=tag_id)
    new_tag = generate_qr_for_product(tag.product)
    return _format_qrtag(request, new_tag)


@router.post("/qr-tags/batch-generate/", response={200: List[QRTagOut], 400: dict}, auth=jwt_auth)
def batch_generate_tags(request, payload: BatchQRIn):
    """
    Generate QR tags for a list of products concurrently.
    """
    if not payload.product_ids:
        return 400, {"error": "product_ids cannot be empty"}

    products = list(Product.objects.filter(id__in=payload.product_ids))
    if not products:
        return 400, {"error": "No matching products found."}

    from asgiref.sync import async_to_sync
    tags = async_to_sync(generate_qr_batch_async)(products)
    return 200, [_format_qrtag(request, t) for t in tags]


# ==============================================================================
# TRAY / GROUP QR CODES
# ==============================================================================

@router.get("/trays/", response=List[TrayOut], auth=jwt_auth)
@router.get("/qr-tags/trays/", response=List[TrayOut], auth=jwt_auth, include_in_schema=False)
def list_trays(request):
    """List all jewelry trays / group QR tags with summary statistics and items."""
    trays = Tray.objects.prefetch_related('items', 'items__purity', 'items__category').all()
    return [_format_tray(request, t) for t in trays]


@router.post("/trays/", response={201: TrayOut, 400: dict}, auth=jwt_auth)
@router.post("/qr-tags/trays/", response={201: TrayOut, 400: dict}, auth=jwt_auth, include_in_schema=False)
def create_tray(request, payload: CreateTrayIn):
    """
    Club multiple products into a Tray / Group QR Tag and generate group QR code.
    """
    if not payload.name.strip():
        return 400, {"error": "Tray name is required"}
    if not payload.product_ids:
        return 400, {"error": "At least one product is required to club into a tray"}

    code = payload.code.strip() if (payload.code and payload.code.strip()) else _generate_tray_code()
    if Tray.objects.filter(code__iexact=code).exists():
        return 400, {"error": f"A tray with code '{code}' already exists."}

    products = list(Product.objects.filter(id__in=payload.product_ids))
    if not products:
        return 400, {"error": "No matching products found for the provided IDs."}

    tray = Tray.objects.create(
        code=code,
        name=payload.name.strip(),
        description=payload.description or "",
    )
    tray.items.set(products)
    generate_qr_for_tray(tray)
    return 201, _format_tray(request, tray)


@router.get("/trays/{tray_id}/", response=TrayOut, auth=jwt_auth)
@router.get("/qr-tags/trays/{tray_id}/", response=TrayOut, auth=jwt_auth, include_in_schema=False)
def get_tray(request, tray_id: int):
    """Retrieve full details of a specific tray and all items inside it."""
    tray = get_object_or_404(
        Tray.objects.prefetch_related('items', 'items__purity', 'items__category'),
        id=tray_id
    )
    return _format_tray(request, tray)


@router.get("/trays/by-code/{code}/", response=TrayOut, auth=jwt_auth)
@router.get("/qr-tags/trays/by-code/{code}/", response=TrayOut, auth=jwt_auth, include_in_schema=False)
def get_tray_by_code(request, code: str):
    """Lookup tray and all items by scannable tray code (e.g. TRAY-2026-001)."""
    tray = get_object_or_404(
        Tray.objects.prefetch_related('items', 'items__purity', 'items__category'),
        code__iexact=code.strip()
    )
    return _format_tray(request, tray)


@router.put("/trays/{tray_id}/", response={200: TrayOut, 400: dict}, auth=jwt_auth)
@router.put("/qr-tags/trays/{tray_id}/", response={200: TrayOut, 400: dict}, auth=jwt_auth, include_in_schema=False)
def update_tray(request, tray_id: int, payload: UpdateTrayIn):
    """Update tray name, code, description, or assigned products and refresh QR code."""
    tray = get_object_or_404(Tray, id=tray_id)

    if payload.name is not None:
        if not payload.name.strip():
            return 400, {"error": "Tray name cannot be empty"}
        tray.name = payload.name.strip()

    if payload.code is not None:
        code = payload.code.strip()
        if not code:
            return 400, {"error": "Tray code cannot be empty"}
        if Tray.objects.filter(code__iexact=code).exclude(id=tray.id).exists():
            return 400, {"error": f"Tray code '{code}' already in use"}
        tray.code = code

    if payload.description is not None:
        tray.description = payload.description.strip()

    tray.save()

    if payload.product_ids is not None:
        products = list(Product.objects.filter(id__in=payload.product_ids))
        tray.items.set(products)

    generate_qr_for_tray(tray)
    return 200, _format_tray(request, tray)


@router.delete("/trays/{tray_id}/", response={200: dict}, auth=jwt_auth)
@router.delete("/qr-tags/trays/{tray_id}/", response={200: dict}, auth=jwt_auth, include_in_schema=False)
def delete_tray(request, tray_id: int):
    """Delete a tray / group QR tag (does not delete underlying inventory items)."""
    tray = get_object_or_404(Tray, id=tray_id)
    if tray.qr_image:
        tray.qr_image.delete(save=False)
    tray.delete()
    return 200, {"success": True, "message": "Tray deleted successfully"}


@router.post("/trays/{tray_id}/regenerate/", response=TrayOut, auth=jwt_auth)
def regenerate_tray_tag(request, tray_id: int):
    """Regenerate group QR code image and encoded payload for a tray."""
    tray = get_object_or_404(Tray, id=tray_id)
    new_tray = generate_qr_for_tray(tray)
    return _format_tray(request, new_tray)


@router.post("/trays/{tray_id}/mark-printed/", response={200: dict}, auth=jwt_auth)
def mark_tray_tag_printed(request, tray_id: int):
    """Increment label print count to track physical group tag printing."""
    tray = get_object_or_404(Tray, id=tray_id)
    tray.printed_count += 1
    tray.save(update_fields=['printed_count'])
    return 200, {"printed_count": tray.printed_count}
