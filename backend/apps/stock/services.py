from django.db import models, transaction
from .models import StockMovement, StockSummary


def record_stock_movement(product, movement_type, quantity, reference_type='', reference_id=None, note='', user=None, branch=None):
    """Atomic stock movement recording with strict non-negative inventory protection."""
    if movement_type != StockMovement.MovementType.ADJUSTMENT and quantity <= 0:
        raise ValueError("Movement quantity must be greater than zero.")
    if movement_type == StockMovement.MovementType.ADJUSTMENT and quantity < 0:
        raise ValueError("Stock adjustment quantity cannot be negative.")

    with transaction.atomic():
        # Lock summary first before creating movement
        summary, _ = StockSummary.objects.select_for_update().get_or_create(product=product)

        if movement_type in [StockMovement.MovementType.OUT, StockMovement.MovementType.EXCHANGE]:
            if summary.quantity_on_hand < quantity:
                raise ValueError(
                    f"Insufficient stock for '{product.sku}'. Available: {summary.quantity_on_hand}, Requested: {quantity}"
                )
            summary.quantity_on_hand -= quantity
        elif movement_type in [StockMovement.MovementType.IN, StockMovement.MovementType.RETURN]:
            summary.quantity_on_hand += quantity
        elif movement_type == StockMovement.MovementType.ADJUSTMENT:
            summary.quantity_on_hand = quantity

        summary.save()

        movement = StockMovement.objects.create(
            product=product,
            movement_type=movement_type,
            quantity=quantity,
            reference_type=reference_type,
            reference_id=reference_id,
            note=note,
            created_by=user,
            branch=branch,
        )
        return movement
