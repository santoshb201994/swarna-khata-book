from typing import List
from django.shortcuts import get_object_or_404
from ninja import Router

from apps.qr_tags.models import QRTag
from apps.products.models import Product
from apps.qr_tags.services import generate_qr_for_product, generate_qr_batch_async
from ninja_api.auth import jwt_auth
from ninja_api.schemas import QRTagOut, BatchQRIn

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
