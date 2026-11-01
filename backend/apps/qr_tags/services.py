import qrcode
import json
import io
from decimal import Decimal
from django.core.files.base import ContentFile
from .models import QRTag, Tray


def generate_qr_for_product(product):
    """
    Unified QR Architecture:
    Maintains QR identity metadata using canonical payload format 'SKB:<UUID>'.
    Dynamic rendering is performed client-side in React; no image binaries are saved to disk or DB.
    """
    token = getattr(product, 'qr_token', None)
    if not token and hasattr(product, 'items'):
        item = product.items.first()
        if item:
            token = item.qr_token

    qr_payload = f"SKB:{token}" if token else product.sku

    # Get or create QRTag metadata row without saving image bytes
    qr_tag, created = QRTag.objects.get_or_create(product=product)
    qr_tag.qr_data = qr_payload
    qr_tag.save(update_fields=['qr_data'])
    return qr_tag


def generate_qr_for_tray(tray: Tray):
    """Generate or update group QR code for a tray. Returns updated Tray instance."""
    items = list(tray.items.select_related('purity', 'category').all())

    total_gross = sum((i.gross_weight for i in items), Decimal('0.000'))
    total_net = sum((i.net_weight for i in items), Decimal('0.000'))
    total_stone = sum((i.stone_weight for i in items), Decimal('0.000'))

    qr_data = {
        'type': 'tray',
        'tray_id': tray.id,
        'code': tray.code,
        'name': tray.name,
        'total_items': len(items),
        'gross_wt': str(total_gross),
        'net_wt': str(total_net),
        'stone_wt': str(total_stone),
        'items': [
            {
                'id': item.id,
                'sku': item.sku,
                'name': item.name,
                'purity': item.purity.name if item.purity else '',
                'gross_wt': str(item.gross_weight),
                'net_wt': str(item.net_weight),
                'stone_wt': str(item.stone_weight),
                'huid': item.huid or '',
            }
            for item in items
        ]
    }
    qr_payload = json.dumps(qr_data, separators=(',', ':'))

    # Generate QR image with Medium error correction for dense payloads
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')

    # Save to bytes
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    image_content = ContentFile(buffer.read(), name=f'tray_qr_{tray.code}.png')

    tray.qr_data = qr_payload
    if tray.qr_image:
        tray.qr_image.delete(save=False)
    tray.qr_image.save(f'tray_qr_{tray.code}.png', image_content, save=False)
    tray.save(update_fields=['qr_data', 'qr_image', 'updated_at'])
    return tray


async def generate_qr_batch_async(products):
    """
    Asynchronously generate QR tags for a list of products in parallel.
    Safely captures the active tenant schema to prevent thread-local isolation loss.
    """
    import asyncio
    from django.db import connection
    from django_tenants.utils import schema_context
    current_schema = getattr(connection, 'schema_name', 'public')

    def _threaded_qr(prod):
        with schema_context(current_schema):
            return generate_qr_for_product(prod)

    tasks = [asyncio.to_thread(_threaded_qr, product) for product in products]
    results = await asyncio.gather(*tasks)
    return list(results)
