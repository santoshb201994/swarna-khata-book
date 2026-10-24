from django.db import models, transaction
from .models import StockMovement, StockSummary


def record_stock_movement(product, movement_type, quantity, reference_type='', reference_id=None, note='', user=None, branch=None):
    """Atomic stock movement recording with summary update."""
    with transaction.atomic():
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
        # Update summary
        summary, _ = StockSummary.objects.select_for_update().get_or_create(product=product)
        if movement_type in [StockMovement.MovementType.IN, StockMovement.MovementType.RETURN]:
            summary.quantity_on_hand += quantity
        elif movement_type in [StockMovement.MovementType.OUT, StockMovement.MovementType.EXCHANGE]:
            summary.quantity_on_hand -= quantity
        elif movement_type == StockMovement.MovementType.ADJUSTMENT:
            summary.quantity_on_hand = quantity
        summary.save()
        return movement
