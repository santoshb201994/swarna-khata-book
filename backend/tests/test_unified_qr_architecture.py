import json
import uuid
from decimal import Decimal
from django.test import TestCase, Client as TestClient
from django_tenants.utils import schema_context
from apps.tenants.models import Client, Domain
from apps.accounts.models import User, Branch
from apps.products.models import Category, Purity, Product
from apps.billing.models import Item
from apps.qr_tags.models import QRTag
from ninja_api.auth import create_token


class UnifiedQRArchitectureTestCase(TestCase):
    """
    Comprehensive tests for Swarna Khata Unified QR Code Architecture:
    1. Permanent UUID qr_token per physical item.
    2. No image blobs stored in PostgreSQL.
    3. Canonical payload SKB:<UUID> resolution.
    4. Django Ninja GET /api/pos/items/by-qr/{qr_token}/.
    5. Physical Tag Verification POST /api/pos/items/{qr_token}/verify-tag/.
    6. Branch and Tenant Isolation.
    7. Backward compatibility with legacy SKUs.
    """

    @classmethod
    def setUpTestData(cls):
        cls.tenant = Client.objects.filter(schema_name='demo').first()
        if not cls.tenant:
            cls.tenant = Client(schema_name='demo', name='Demo Jewellery')
            cls.tenant.save()
            Domain.objects.create(domain='demo.localhost', tenant=cls.tenant, is_primary=True)

        with schema_context(cls.tenant.schema_name):
            cls.branch_a = Branch.objects.create(name="Central Showroom")
            cls.branch_b = Branch.objects.create(name="Airport Branch")

            cls.manager_user = User.objects.create_user(
                username="qr_manager",
                password="TestPassword@123",
                role=User.Role.MANAGER,
                branch=cls.branch_a,
            )

            cls.staff_branch_b = User.objects.create_user(
                username="staff_b",
                password="TestPassword@123",
                role=User.Role.STAFF,
                branch=cls.branch_b,
            )

            cls.category = Category.objects.create(name="Bangles & Bracelets")
            cls.purity = Purity.objects.create(name="22KT (916)", fineness=Decimal("0.916"))

    def setUp(self):
        self.client = TestClient()
        with schema_context(self.tenant.schema_name):
            self.manager_token = create_token(self.manager_user)
            self.staff_b_token = create_token(self.staff_branch_b)

    def test_item_permanent_uuid_generation(self):
        """Verify each physical inventory Item receives a unique permanent UUID v4 qr_token."""
        with schema_context(self.tenant.schema_name):
            prod = Product.objects.create(
                name="Antique Kada 22KT",
                sku="KADA-22K-999",
                category=self.category,
                purity=self.purity,
                gross_weight=Decimal("25.500"),
                branch=self.branch_a,
            )

            item1 = Item.objects.create(
                product=prod,
                qr_code=prod.sku,
                name=prod.name,
                weight=prod.gross_weight,
            )
            item2 = Item.objects.create(
                product=prod,
                qr_code=prod.sku,
                name=prod.name,
                weight=prod.gross_weight,
            )

            self.assertIsNotNone(item1.qr_token)
            self.assertIsNotNone(item2.qr_token)
            self.assertNotEqual(item1.qr_token, item2.qr_token)
            self.assertIsInstance(item1.qr_token, uuid.UUID)

    def test_create_product_does_not_store_qr_image_bytes(self):
        """Verify product creation sets up qr_token metadata without persisting binary image files."""
        with schema_context(self.tenant.schema_name):
            payload = {
                "name": "Emerald Floral Ring",
                "sku": "RNG-EMR-001",
                "category_id": self.category.id,
                "purity_id": self.purity.id,
                "gross_weight": "8.500",
                "stone_weight": "0.500",
                "other_weight": "0.000",
                "making_charge_type": "per_gram",
                "making_charge_value": "350.00",
                "hsn_code": "7113",
                "huid": "HUID998811",
                "branch_id": self.branch_a.id,
                "initial_stock": 1,
            }

            res = self.client.post(
                '/api/products/',
                data=json.dumps(payload),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.manager_token}',
                HTTP_X_TENANT='demo',
            )
            self.assertEqual(res.status_code, 201)
            data = res.json()

            # Verify qr_token is returned in ProductOut schema
            self.assertIn('qr_token', data)
            self.assertIsNotNone(data['qr_token'])

            # Verify associated Item exists
            prod = Product.objects.get(sku="RNG-EMR-001")
            item = Item.objects.filter(product=prod).first()
            self.assertIsNotNone(item)
            self.assertEqual(str(item.qr_token), str(data['qr_token']))

            # Verify QRTag does NOT have a binary image file saved
            tag = QRTag.objects.filter(product=prod).first()
            if tag:
                self.assertFalse(bool(tag.qr_image))

    def test_get_item_by_canonical_qr(self):
        """Verify GET /api/pos/items/by-qr/{qr_token}/ resolves canonical 'SKB:<UUID>' and raw UUID."""
        with schema_context(self.tenant.schema_name):
            prod = Product.objects.create(
                name="Diamond Solitaire Pendant",
                sku="PND-DIA-001",
                category=self.category,
                purity=self.purity,
                gross_weight=Decimal("5.200"),
                branch=self.branch_a,
            )
            item = Item.objects.create(
                product=prod,
                qr_code=prod.sku,
                name=prod.name,
                weight=prod.gross_weight,
            )

            # Test 1: Query with Canonical prefix "SKB:<UUID>"
            canonical_payload = f"SKB:{item.qr_token}"
            res = self.client.get(
                f'/api/pos/items/by-qr/{canonical_payload}/',
                HTTP_AUTHORIZATION=f'Bearer {self.manager_token}',
                HTTP_X_TENANT='demo',
            )
            self.assertEqual(res.status_code, 200)
            res_data = res.json()
            self.assertEqual(res_data['sku'], "PND-DIA-001")
            self.assertEqual(res_data['qr_token'], str(item.qr_token))
            self.assertEqual(res_data['stock_status'], "AVAILABLE")

            # Test 2: Query with Raw UUID
            res2 = self.client.get(
                f'/api/pos/items/by-qr/{item.qr_token}/',
                HTTP_AUTHORIZATION=f'Bearer {self.manager_token}',
                HTTP_X_TENANT='demo',
            )
            self.assertEqual(res2.status_code, 200)
            self.assertEqual(res2.json()['qr_token'], str(item.qr_token))

            # Test 3: Query with Legacy SKU fallback
            res3 = self.client.get(
                f'/api/pos/items/by-qr/{prod.sku}/',
                HTTP_AUTHORIZATION=f'Bearer {self.manager_token}',
                HTTP_X_TENANT='demo',
            )
            self.assertEqual(res3.status_code, 200)
            self.assertEqual(res3.json()['sku'], "PND-DIA-001")

    def test_physical_tag_verification(self):
        """Verify POST /api/pos/items/{qr_token}/verify-tag/ validates tag match and increments printed_count."""
        with schema_context(self.tenant.schema_name):
            prod = Product.objects.create(
                name="Temple Gold Necklace",
                sku="NCK-TMP-001",
                category=self.category,
                purity=self.purity,
                gross_weight=Decimal("45.000"),
                branch=self.branch_a,
            )
            item = Item.objects.create(
                product=prod,
                qr_code=prod.sku,
                name=prod.name,
                weight=prod.gross_weight,
                printed_count=0,
            )

            # Test Match
            verify_payload = {"scanned_payload": f"SKB:{item.qr_token}"}
            res = self.client.post(
                f'/api/pos/items/{item.qr_token}/verify-tag/',
                data=json.dumps(verify_payload),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.manager_token}',
                HTTP_X_TENANT='demo',
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertTrue(data['success'])
            self.assertTrue(data['match'])
            self.assertEqual(data['printed_count'], 1)

            # Refresh item from DB
            item.refresh_from_db()
            self.assertEqual(item.printed_count, 1)

            # Test Mismatch with arbitrary UUID
            wrong_uuid = str(uuid.uuid4())
            mismatch_payload = {"scanned_payload": f"SKB:{wrong_uuid}"}
            res_mismatch = self.client.post(
                f'/api/pos/items/{item.qr_token}/verify-tag/',
                data=json.dumps(mismatch_payload),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.manager_token}',
                HTTP_X_TENANT='demo',
            )
            self.assertEqual(res_mismatch.status_code, 200)
            mismatch_data = res_mismatch.json()
            self.assertFalse(mismatch_data['match'])

    def test_branch_isolation_on_qr_lookup(self):
        """Verify staff from branch B cannot access items assigned strictly to branch A."""
        with schema_context(self.tenant.schema_name):
            prod_a = Product.objects.create(
                name="Exclusive Branch A Choker",
                sku="CHK-BRA-001",
                category=self.category,
                purity=self.purity,
                gross_weight=Decimal("30.000"),
                branch=self.branch_a,
            )
            item_a = Item.objects.create(
                product=prod_a,
                qr_code=prod_a.sku,
                name=prod_a.name,
                weight=prod_a.gross_weight,
            )

            # Staff B attempts to query Branch A item
            res = self.client.get(
                f'/api/pos/items/by-qr/{item_a.qr_token}/',
                HTTP_AUTHORIZATION=f'Bearer {self.staff_b_token}',
                HTTP_X_TENANT='demo',
            )
            self.assertEqual(res.status_code, 403)
            self.assertIn("different branch", res.json()['error'])
