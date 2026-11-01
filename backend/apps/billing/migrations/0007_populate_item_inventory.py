import uuid
from django.db import migrations


def populate_item_uuids_and_products(apps, schema_editor):
    Item = apps.get_model('billing', 'Item')
    Product = apps.get_model('products', 'Product')

    # 1. Ensure all existing Items have a permanent UUID and link to Product by SKU
    for item in Item.objects.all():
        if not item.qr_token:
            item.qr_token = uuid.uuid4()
        if not item.product and item.qr_code:
            prod = Product.objects.filter(sku=item.qr_code).first()
            if prod:
                item.product = prod
        item.save()

    # 2. For every Product that doesn't have an Item record yet, create an Item with a permanent UUID
    for prod in Product.objects.all():
        if not Item.objects.filter(product=prod).exists():
            Item.objects.create(
                qr_token=uuid.uuid4(),
                product=prod,
                qr_code=prod.sku,
                name=prod.name,
                weight=prod.gross_weight,
                status='AVAILABLE',
            )


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0006_item_qr_token_and_product'),
    ]

    operations = [
        migrations.RunPython(
            populate_item_uuids_and_products,
            reverse_code=migrations.RunPython.noop
        ),
    ]
