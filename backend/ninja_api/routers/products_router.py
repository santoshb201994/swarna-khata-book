from typing import List, Optional
from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.db.models import Q
from ninja import Router, File, UploadedFile
from ninja.errors import HttpError

from apps.products.models import Category, Purity, Product
from apps.stock.models import StockMovement, StockSummary
from apps.stock.services import record_stock_movement
from apps.qr_tags.services import generate_qr_for_product
from ninja_api.auth import jwt_auth, require_role
from ninja_api.schemas import (
    CategoryIn, CategoryOut, PurityIn, PurityOut,
    ProductIn, ProductUpdateIn, ProductOut, ProductListOut, QRTagOut
)

router = Router(tags=["Jewellery Products & Inventory Items"])


def _format_product(request, prod: Product) -> dict:
    photo_url = request.build_absolute_uri(prod.photo.url) if prod.photo else None
    qr_url = None
    try:
        if prod.qr_tag and prod.qr_tag.qr_image:
            qr_url = request.build_absolute_uri(prod.qr_tag.qr_image.url)
    except Exception:
        pass

    return {
        "id": prod.id,
        "name": prod.name,
        "sku": prod.sku,
        "category_id": prod.category_id,
        "category_name": prod.category.name if prod.category else None,
        "purity_id": prod.purity_id,
        "purity_name": prod.purity.name if prod.purity else None,
        "gross_weight": prod.gross_weight,
        "stone_weight": prod.stone_weight,
        "other_weight": prod.other_weight,
        "net_weight": prod.net_weight,
        "making_charge_type": prod.making_charge_type,
        "making_charge_value": prod.making_charge_value,
        "description": prod.description,
        "hsn_code": prod.hsn_code,
        "huid": prod.huid,
        "photo_url": photo_url,
        "qr_code_url": qr_url,
        "is_active": prod.is_active,
        "branch_id": prod.branch_id,
        "created_at": prod.created_at,
        "updated_at": prod.updated_at,
    }


# ==============================================================================
# CATEGORIES & PURITIES
# ==============================================================================

@router.get("/categories/", response=List[CategoryOut], auth=jwt_auth)
def list_categories(request):
    return Category.objects.all()


@router.post("/categories/", response={201: CategoryOut, 400: dict}, auth=jwt_auth)
def create_category(request, payload: CategoryIn):
    if Category.objects.filter(name__iexact=payload.name).exists():
        return 400, {"error": f"Category '{payload.name}' already exists."}
    cat = Category.objects.create(name=payload.name, description=payload.description)
    return 201, cat


@router.get("/purities/", response=List[PurityOut], auth=jwt_auth)
def list_purities(request):
    return Purity.objects.all()


@router.post("/purities/", response={201: PurityOut, 400: dict}, auth=jwt_auth)
def create_purity(request, payload: PurityIn):
    if Purity.objects.filter(name__iexact=payload.name).exists():
        return 400, {"error": f"Purity '{payload.name}' already exists."}
    purity = Purity.objects.create(name=payload.name, fineness=payload.fineness)
    return 201, purity


# ==============================================================================
# PRODUCTS
# ==============================================================================

@router.get("/products/", response=List[ProductListOut], auth=jwt_auth)
def list_products(
    request,
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    purity_id: Optional[int] = None,
    is_active: Optional[bool] = True
):
    """
    Search and list products with optional filters on SKU, name, purity, category.
    """
    qs = Product.objects.select_related('category', 'purity', 'branch', 'qr_tag').all()
    if is_active is not None:
        qs = qs.filter(is_active=is_active)
    if category_id:
        qs = qs.filter(category_id=category_id)
    if purity_id:
        qs = qs.filter(purity_id=purity_id)
    if search:
        qs = qs.filter(
            Q(sku__icontains=search) | Q(name__icontains=search) | Q(huid__icontains=search)
        )

    qs = qs.order_by('-id')
    # Batch query corresponding Item statuses for high-speed listing
    from apps.billing.models import Item
    skus = [p.sku for p in qs]
    item_status_map = {item.qr_code: item.status for item in Item.objects.filter(qr_code__in=skus)}

    results = []
    for prod in qs:
        photo_url = request.build_absolute_uri(prod.photo.url) if prod.photo else None
        qr_url = None
        try:
            if prod.qr_tag and prod.qr_tag.qr_image:
                qr_url = request.build_absolute_uri(prod.qr_tag.qr_image.url)
        except Exception:
            pass

        results.append({
            "id": prod.id,
            "name": prod.name,
            "sku": prod.sku,
            "category_id": prod.category_id,
            "category_name": prod.category.name if prod.category else None,
            "purity_id": prod.purity_id,
            "purity_name": prod.purity.name if prod.purity else None,
            "gross_weight": prod.gross_weight,
            "stone_weight": prod.stone_weight,
            "other_weight": prod.other_weight,
            "net_weight": prod.net_weight,
            "making_charge_type": prod.making_charge_type,
            "making_charge_value": prod.making_charge_value,
            "huid": prod.huid,
            "photo_url": photo_url,
            "qr_code_url": qr_url,
            "item_status": item_status_map.get(prod.sku, 'AVAILABLE'),
            "is_active": prod.is_active,
            "created_at": prod.created_at,
        })
    return results


@router.post("/products/", response={201: ProductOut, 400: dict}, auth=jwt_auth)
def create_product(request, payload: ProductIn):
    """
    Create a new jewellery product.
    Automatically:
    - Generates unique QR Tag
    - Registers into authoritative Item inventory for QR scanning & billing
    - Records initial inventory stock if initial_stock > 0
    """
    if Product.objects.filter(sku__iexact=payload.sku).exists():
        return 400, {"error": f"Product with SKU '{payload.sku}' already exists."}

    category = get_object_or_404(Category, id=payload.category_id)
    purity = get_object_or_404(Purity, id=payload.purity_id)

    branch = None
    if payload.branch_id:
        from apps.accounts.models import Branch
        branch = Branch.objects.filter(id=payload.branch_id).first()
    elif request.auth and request.auth.branch:
        branch = request.auth.branch

    prod = Product.objects.create(
        name=payload.name,
        sku=payload.sku,
        category=category,
        purity=purity,
        gross_weight=payload.gross_weight,
        stone_weight=payload.stone_weight,
        other_weight=payload.other_weight,
        making_charge_type=payload.making_charge_type,
        making_charge_value=payload.making_charge_value,
        description=payload.description or '',
        hsn_code=payload.hsn_code or '7113',
        huid=payload.huid or '',
        branch=branch,
        is_active=True,
    )

    # 1. Automatically generate high-resolution QR Tag
    generate_qr_for_product(prod)

    # 2. Automatically register into authoritative Item inventory for POS & QR Scanner
    from apps.billing.models import Item
    Item.objects.update_or_create(
        qr_code=prod.sku,
        defaults={
            'name': prod.name,
            'weight': prod.gross_weight,
            'status': Item.Status.AVAILABLE,
        }
    )

    # 3. Record initial stock movement & summary if specified
    if payload.initial_stock > 0:
        record_stock_movement(
            product=prod,
            movement_type=StockMovement.MovementType.IN,
            quantity=payload.initial_stock,
            reference_type='initial_stock',
            note='Initial inventory on product creation',
            user=request.auth,
            branch=branch,
        )

    # Reload with relations
    prod = Product.objects.select_related('category', 'purity', 'branch', 'qr_tag').get(id=prod.id)
    return 201, _format_product(request, prod)


@router.get("/products/{product_id}/", response=ProductOut, auth=jwt_auth)
def get_product(request, product_id: int):
    prod = get_object_or_404(
        Product.objects.select_related('category', 'purity', 'branch', 'qr_tag'),
        id=product_id
    )
    return _format_product(request, prod)


@router.put("/products/{product_id}/", response={200: ProductOut, 400: dict}, auth=jwt_auth)
def update_product(request, product_id: int, payload: ProductUpdateIn):
    prod = get_object_or_404(Product, id=product_id)

    if payload.name is not None:
        prod.name = payload.name
    if payload.category_id is not None:
        prod.category = get_object_or_404(Category, id=payload.category_id)
    if payload.purity_id is not None:
        prod.purity = get_object_or_404(Purity, id=payload.purity_id)
    if payload.gross_weight is not None:
        prod.gross_weight = payload.gross_weight
    if payload.stone_weight is not None:
        prod.stone_weight = payload.stone_weight
    if payload.other_weight is not None:
        prod.other_weight = payload.other_weight
    if payload.making_charge_type is not None:
        prod.making_charge_type = payload.making_charge_type
    if payload.making_charge_value is not None:
        prod.making_charge_value = payload.making_charge_value
    if payload.description is not None:
        prod.description = payload.description
    if payload.hsn_code is not None:
        prod.hsn_code = payload.hsn_code
    if payload.huid is not None:
        prod.huid = payload.huid
    if payload.is_active is not None:
        prod.is_active = payload.is_active

    prod.save()
    # Regenerate QR tag with updated product payload
    generate_qr_for_product(prod)

    # Sync to authoritative Item model
    from apps.billing.models import Item
    Item.objects.filter(qr_code=prod.sku).update(name=prod.name, weight=prod.gross_weight)

    prod = Product.objects.select_related('category', 'purity', 'branch', 'qr_tag').get(id=prod.id)
    return 200, _format_product(request, prod)


@router.delete("/products/{product_id}/", response={200: dict}, auth=jwt_auth)
def delete_product(request, product_id: int):
    """Soft delete product (marks is_active=False)"""
    require_role(request.auth, ['owner', 'manager'])
    prod = get_object_or_404(Product, id=product_id)
    prod.is_active = False
    prod.save(update_fields=['is_active'])
    return 200, {"status": "success", "message": f"Product {prod.sku} marked inactive."}


@router.post("/products/{product_id}/upload-photo/", response={200: ProductOut, 400: dict}, auth=jwt_auth)
def upload_photo(request, product_id: int, photo: UploadedFile = File(...)):
    """Upload product photograph."""
    prod = get_object_or_404(Product, id=product_id)
    prod.photo = photo
    prod.save()
    generate_qr_for_product(prod)
    prod = Product.objects.select_related('category', 'purity', 'branch', 'qr_tag').get(id=prod.id)
    return 200, _format_product(request, prod)


@router.post("/products/{product_id}/regenerate-qr/", response={200: QRTagOut}, auth=jwt_auth)
def regenerate_product_qr(request, product_id: int):
    """Force re-generate the QR code image for a product."""
    prod = get_object_or_404(Product, id=product_id)
    tag = generate_qr_for_product(prod)
    qr_url = request.build_absolute_uri(tag.qr_image.url) if tag.qr_image else None
    return 200, {
        "id": tag.id,
        "product_id": tag.product_id,
        "product_name": tag.product.name,
        "product_sku": tag.product.sku,
        "purity": tag.product.purity.name,
        "gross_weight": tag.product.gross_weight,
        "net_weight": tag.product.net_weight,
        "qr_data": tag.qr_data,
        "qr_image_url": qr_url,
        "printed_count": tag.printed_count,
        "created_at": tag.created_at,
        "updated_at": tag.updated_at,
    }
