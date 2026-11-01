import uuid
from decimal import Decimal
from typing import List, Optional
from django.shortcuts import get_object_or_404
from django.db import transaction
from ninja import Router
from ninja.errors import HttpError

from apps.billing.models import Bill, Item, IdempotencyRecord
from ninja_api.auth import bill_jwt_auth, generate_bill_token, jwt_auth
from ninja_api.schemas import (
    BillCreateResponse, BillDetailResponse, ScanItemIn, ScanItemResponse, ItemOut
)

router = Router(tags=["Authoritative Bill Cart & Mobile QR Polling"])


# ==============================================================================
# 1. CREATE BILL & ISSUE SCOPED JWT
# ==============================================================================

@router.post("/bills/", response={201: BillCreateResponse, 400: dict}, auth=jwt_auth)
def create_bill(request):
    """
    Creates a new draft Bill and returns a scoped JWT token bound to this bill_id
    and the authenticated user's PostgreSQL tenant schema.
    """
    user = request.auth
    schema_name = getattr(user, 'tenant_schema', None)
    if not schema_name or schema_name == 'public':
        tenant = getattr(request, 'tenant', None)
        schema_name = tenant.schema_name if tenant else 'public'

    bill = Bill.objects.create(status=Bill.Status.DRAFT)
    token = generate_bill_token(tenant_schema=schema_name, bill_id=bill.id)

    # Construct authoritative HTTPS pairing link
    proto = "https" if request.is_secure() or request.headers.get('x-forwarded-proto') == 'https' else "https"
    host = request.get_host()
    https_url = f"{proto}://{host}/scan/{bill.id}?token={token}"

    return 201, {
        "bill_id": bill.id,
        "status": bill.status,
        "token": token,
        "https_url": https_url,
        "created_at": bill.created_at,
    }


# ==============================================================================
# 2. HTTP POLLING ENDPOINT (Laptop POS Screen)
# ==============================================================================

@router.get("/bills/{bill_id}", response={200: BillDetailResponse, 404: dict}, auth=bill_jwt_auth)
def get_bill_cart(request, bill_id: uuid.UUID):
    """
    High-frequency polling endpoint (called every 2 seconds by the laptop client).
    Highly optimized: single round-trip database query returning the bill status,
    all currently locked items, and the total calculated gold weight.
    """
    bill = Bill.objects.prefetch_related('items').filter(id=bill_id).first()
    if not bill:
        return 404, {"error": "Bill not found."}

    items_list = list(bill.items.filter(status=Item.Status.IN_CART))
    total_weight = sum((it.weight for it in items_list), Decimal('0.000'))

    formatted_items = [
        {
            "id": it.id,
            "qr_code": it.qr_code,
            "name": it.name or '',
            "weight": it.weight,
            "status": it.status,
        }
        for it in items_list
    ]

    return 200, {
        "bill_id": bill.id,
        "status": bill.status,
        "created_at": bill.created_at,
        "total_weight": total_weight,
        "item_count": len(items_list),
        "items": formatted_items,
    }


# ==============================================================================
# 3. CONCURRENCY-SAFE IDEMPOTENT SCAN ENDPOINT (Mobile Phone)
# ==============================================================================

@router.post(
    "/bills/{bill_id}/scan",
    response={200: ScanItemResponse, 400: dict, 404: dict, 409: dict},
    auth=bill_jwt_auth
)
def scan_item_into_bill(request, bill_id: uuid.UUID, payload: ScanItemIn):
    """
    Write endpoint for the smartphone camera scanner:
    - Protected by scoped JWT Bearer authentication.
    - Requires 'Idempotency-Key' in HTTP request headers.
    - Uses PostgreSQL row-level locks (.select_for_update()) to prevent race conditions.
    - Strictly checks that Item status is AVAILABLE.
    - Mutates status to IN_CART and links to bill_id atomically.
    """
    idempotency_key = (
        request.headers.get('Idempotency-Key')
        or request.META.get('HTTP_IDEMPOTENCY_KEY')
    )
    if not idempotency_key:
        return 400, {"error": "Missing required 'Idempotency-Key' header."}

    idempotency_key = idempotency_key.strip()

    with transaction.atomic():
        # Parse canonical SKB:<UUID> or raw UUID
        token_str = (payload.qr_code or '').strip()
        if token_str.upper().startswith("SKB:"):
            token_str = token_str[4:].strip()
        parsed_uuid = None
        try:
            parsed_uuid = uuid.UUID(token_str)
        except (ValueError, TypeError, AttributeError):
            parsed_uuid = None

        # Step 1: Check IdempotencyRecord for the key
        existing_record = IdempotencyRecord.objects.select_related('bill').filter(
            bill_id=bill_id, key=idempotency_key
        ).first()

        if existing_record:
            if parsed_uuid:
                item = Item.objects.filter(qr_token=parsed_uuid).first()
            else:
                item = Item.objects.filter(qr_code=payload.qr_code).first()

            if not item:
                return 404, {"error": f"Item with QR identifier '{payload.qr_code}' not found."}

            return 200, {
                "status": "success",
                "message": "Idempotent replay: Item already processed.",
                "bill_id": bill_id,
                "item": {
                    "id": item.id,
                    "qr_code": item.qr_code,
                    "name": item.name or '',
                    "weight": item.weight,
                    "status": item.status,
                },
                "is_duplicate": True,
            }

        # Step 2: Query the Item using select_for_update() (Pessimistic Row Lock)
        if parsed_uuid:
            item = Item.objects.select_for_update().filter(qr_token=parsed_uuid).first()
        else:
            item = Item.objects.select_for_update().filter(qr_code=payload.qr_code).first()

        # Step 3: Validate item existence and status
        if not item:
            return 404, {"error": f"Item with QR code '{payload.qr_code}' does not exist."}

        if item.status != Item.Status.AVAILABLE:
            return 409, {
                "error": f"Item '{item.qr_code}' is not available (Current status: {item.status})."
            }

        bill = Bill.objects.select_for_update().filter(id=bill_id).first()
        if not bill:
            return 404, {"error": "Bill not found."}

        if bill.status != Bill.Status.DRAFT:
            return 400, {"error": f"Cannot add items to bill with status '{bill.status}'."}

        # Step 4: Update item status to IN_CART and link to bill_id
        item.status = Item.Status.IN_CART
        item.locked_by_bill = bill
        item.save(update_fields=['status', 'locked_by_bill', 'updated_at'])

        # Step 5: Save IdempotencyRecord
        IdempotencyRecord.objects.create(key=idempotency_key, bill=bill)

        # Step 6: Return 200 OK
        return 200, {
            "status": "success",
            "message": "Item successfully scanned into cart.",
            "bill_id": bill.id,
            "item": {
                "id": item.id,
                "qr_code": item.qr_code,
                "name": item.name or '',
                "weight": item.weight,
                "status": item.status,
            },
            "is_duplicate": False,
        }
