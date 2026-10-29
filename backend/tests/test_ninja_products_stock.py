import json
from decimal import Decimal
from django.test import TestCase, Client as TestClient
from django_tenants.utils import schema_context
from apps.tenants.models import Client, Domain
from apps.accounts.models import User, Branch
from apps.products.models import Category, Purity, Product
from apps.stock.models import StockMovement, StockSummary
from ninja_api.auth import create_token


class NinjaProductsStockTestCase(TestCase):
    """
    Unit & Integration tests for Jewellery Products, QR Generation, and Stock movements.
    """

    @classmethod
    def setUpTestData(cls):
        cls.tenant = Client.objects.filter(schema_name='demo').first()
        if not cls.tenant:
            cls.tenant = Client(schema_name='demo', name='Demo Jewellery')
            cls.tenant.save()
            Domain.objects.create(domain='demo.localhost', tenant=cls.tenant, is_primary=True)

        with schema_context(cls.tenant.schema_name):
            cls.branch = Branch.objects.create(name="Flagship Showroom")
            cls.user = User.objects.create_user(
                username="prod_mgr",
                password="TestPassword@123",
                role=User.Role.MANAGER,
                branch=cls.branch,
            )
            cls.category = Category.objects.create(name="Necklaces")
            cls.purity = Purity.objects.create(name="22KT (916)", fineness=Decimal("0.916"))

    def setUp(self):
        self.client = TestClient()
        with schema_context(self.tenant.schema_name):
            self.token = create_token(self.user)

    def test_create_product_with_auto_qr_and_stock(self):
        with schema_context(self.tenant.schema_name):
            payload = {
                "name": "Royal Gold Choker",
                "sku": "CHOKER-22K-001",
                "category_id": self.category.id,
                "purity_id": self.purity.id,
                "gross_weight": "32.450",
                "stone_weight": "2.100",
                "other_weight": "0.000",
                "making_charge_type": "per_gram",
                "making_charge_value": "450.00",
                "hsn_code": "7113",
                "huid": "HUID776655",
                "initial_stock": 5,
            }

            res = self.client.post(
                '/api/products/',
                data=json.dumps(payload),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 201)
            data = res.json()
            self.assertEqual(data['sku'], "CHOKER-22K-001")
            self.assertEqual(Decimal(data['net_weight']), Decimal("30.350"))
            self.assertIsNotNone(data['qr_code_url'])

            # Verify StockSummary was materialized
            prod = Product.objects.get(sku="CHOKER-22K-001")
            summary = StockSummary.objects.get(product=prod)
            self.assertEqual(summary.quantity_on_hand, 5)

            # Verify StockMovement IN audit log was recorded
            movements = StockMovement.objects.filter(product=prod, movement_type='IN')
            self.assertEqual(movements.count(), 1)
            self.assertEqual(movements.first().quantity, 5)

    def test_stock_movement_recording(self):
        with schema_context(self.tenant.schema_name):
            prod = Product.objects.create(
                name="Gold Coin 10g",
                sku="COIN-10G-001",
                category=self.category,
                purity=self.purity,
                gross_weight=Decimal("10.000"),
            )
            # Create stock summary
            StockSummary.objects.create(product=prod, quantity_on_hand=10)

            # Record stock OUT
            res = self.client.post(
                '/api/stock-movements/',
                data=json.dumps({
                    "product_id": prod.id,
                    "movement_type": "OUT",
                    "quantity": 3,
                    "note": "Sent to branch display",
                }),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 201)

            summary = StockSummary.objects.get(product=prod)
            self.assertEqual(summary.quantity_on_hand, 7)
