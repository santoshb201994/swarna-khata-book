import qrcode
import json
import io
from django.core.files.base import ContentFile
from .models import QRTag


def generate_qr_for_product(product):
    """Generate or update QR code for a product. Returns QRTag instance."""
    # Build QR data payload
    qr_data = {
        'id': product.id,
        'sku': product.sku,
        'name': product.name,
        'purity': product.purity.name,
        'gross_wt': str(product.gross_weight),
        'net_wt': str(product.net_weight),
        'huid': product.huid,
    }
    qr_payload = json.dumps(qr_data, separators=(',', ':'))

    # Generate QR image
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
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
    image_content = ContentFile(buffer.read(), name=f'qr_{product.sku}.png')

    # Get or create QRTag
    qr_tag, created = QRTag.objects.get_or_create(product=product)
    qr_tag.qr_data = qr_payload
    if qr_tag.qr_image:
        qr_tag.qr_image.delete(save=False)
    qr_tag.qr_image.save(f'qr_{product.sku}.png', image_content, save=False)
    qr_tag.save()
    return qr_tag


async def generate_qr_batch_async(products):
    """
    Asynchronously generate QR tags for a list of products in parallel.
    Uses asyncio.to_thread to offload CPU-bound PIL image creation and disk I/O
    without blocking the server event loop.
    """
    import asyncio

    tasks = [asyncio.to_thread(generate_qr_for_product, product) for product in products]
    results = await asyncio.gather(*tasks)
    return list(results)
