import uuid
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
        ('billing', '0005_sale_customer_snapshot_sale_pdf_sha256_and_more'),
    ]

    operations = [
        # Step 1: Add qr_token with uuid4 default and unique constraint
        migrations.AddField(
            model_name='item',
            name='qr_token',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        # Step 2: Add product ForeignKey
        migrations.AddField(
            model_name='item',
            name='product',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='items',
                to='products.product'
            ),
        ),
        # Step 3: Add printed_count
        migrations.AddField(
            model_name='item',
            name='printed_count',
            field=models.PositiveIntegerField(default=0),
        ),
        # Step 4: Relax qr_code unique constraint to allow multiple items per SKU
        migrations.AlterField(
            model_name='item',
            name='qr_code',
            field=models.CharField(blank=True, db_index=True, max_length=128),
        ),
        # Step 5: Add compound index for high-speed POS scanning & availability
        migrations.AddIndex(
            model_name='item',
            index=models.Index(fields=['status', 'qr_token'], name='billing_ite_stat_qr_tok_idx'),
        ),
    ]
