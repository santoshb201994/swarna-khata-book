from typing import List, Optional
from django.shortcuts import get_object_or_404
from ninja import Router

from apps.products.models import Product
from apps.stock.models import StockMovement, StockSummary
from apps.stock.services import record_stock_movement
from ninja_api.auth import jwt_auth, require_role
from ninja_api.schemas import StockMovementIn, StockMovementOut, StockSummaryOut

router = Router(tags=["Inventory & Stock Ledger"])


@router.get("/stock-movements/", response=List[StockMovementOut], auth=jwt_auth)
def list_stock_movements(
    request,
    movement_type: Optional[str] = None,
    product_id: Optional[int] = None
):
    """
    List audit trail of all inventory movements (IN, OUT, RETURN, EXCHANGE, ADJUSTMENT).
    """
    qs = StockMovement.objects.select_related('product', 'created_by').all()
    if movement_type:
        qs = qs.filter(movement_type=movement_type)
    if product_id:
        qs = qs.filter(product_id=product_id)

    results = []
    for m in qs[:200]:  # Limit latest 200 for high performance
        created_by_name = m.created_by.get_full_name() or m.created_by.username if m.created_by else 'System'
        results.append({
            "id": m.id,
            "product_id": m.product_id,
            "product_name": m.product.name,
            "product_sku": m.product.sku,
            "movement_type": m.movement_type,
            "quantity": m.quantity,
            "reference_type": m.reference_type,
            "reference_id": m.reference_id,
            "note": m.note,
            "created_by_name": created_by_name,
            "created_at": m.created_at,
        })
    return results


@router.post("/stock-movements/", response={201: StockMovementOut, 400: dict}, auth=jwt_auth)
def create_stock_movement(request, payload: StockMovementIn):
    """
    Record an atomic stock adjustment or receipt.
    Locks the row in StockSummary during execution to prevent concurrency anomalies.
    """
    prod = get_object_or_404(Product, id=payload.product_id)
    movement = record_stock_movement(
        product=prod,
        movement_type=payload.movement_type,
        quantity=payload.quantity,
        reference_type=payload.reference_type or 'manual',
        reference_id=payload.reference_id,
        note=payload.note or '',
        user=request.auth,
        branch=request.auth.branch if request.auth else None,
    )

    created_by_name = request.auth.get_full_name() or request.auth.username if request.auth else 'System'
    return 201, {
        "id": movement.id,
        "product_id": movement.product_id,
        "product_name": prod.name,
        "product_sku": prod.sku,
        "movement_type": movement.movement_type,
        "quantity": movement.quantity,
        "reference_type": movement.reference_type,
        "reference_id": movement.reference_id,
        "note": movement.note,
        "created_by_name": created_by_name,
        "created_at": movement.created_at,
    }


@router.get("/stock-summary/", response=List[StockSummaryOut], auth=jwt_auth)
def list_stock_summary(request, search: Optional[str] = None):
    """
    Get current real-time stock balances across all jewellery items.
    """
    qs = StockSummary.objects.select_related('product', 'product__category').all()
    if search:
        qs = qs.filter(product__sku__icontains=search) | qs.filter(product__name__icontains=search)

    results = []
    for s in qs:
        results.append({
            "id": s.id,
            "product_id": s.product_id,
            "product_name": s.product.name,
            "product_sku": s.product.sku,
            "category": s.product.category.name if s.product and s.product.category else None,
            "quantity_on_hand": s.quantity_on_hand,
            "updated_at": s.updated_at,
        })
    return results
