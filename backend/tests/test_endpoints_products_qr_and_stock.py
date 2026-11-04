import json
from decimal import Decimal
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client as TestClient
from django_tenants.utils import schema_context
from apps.tenants.models import Client, Domain
from apps.accounts.models import User, Branch
from apps.products.models import Category, Purity, Product
from apps.qr_tags.models import QRTag, Tray
from apps.stock.models import StockMovement, StockSummary
from ninja_api.auth import create_token


class EndpointsProductsQrAndStockTestCase(TestCase):
    """
    Comprehensive tests covering Products, Barcode/QR tags, and Stock Ledger endpoints:
    - POST /api/categories/
    - GET /api/categories/
    - POST /api/purities/
    - GET /api/purities/
    - POST /api/products/
    - GET /api/products/
    - GET /api/products/{id}/
    - PUT /api/products/{id}/
    - DELETE /api/products/{id}/
    - POST /api/products/{id}/regenerate-qr/
    - POST /api/products/{id}/upload-photo/
    - GET /api/qr-tags/
    - GET /api/qr-tags/{id}/
    - POST /api/qr-tags/{id}/mark-printed/
    - POST /api/qr-tags/{id}/regenerate/
    - POST /api/qr-tags/batch-generate/
    - GET /api/trays/
    - POST /api/trays/
    - GET /api/trays/{id}/
    - GET /api/trays/by-code/{code}/
    - PUT /api/trays/{id}/
    - DELETE /api/trays/{id}/
    - POST /api/trays/{id}/regenerate/
    - POST /api/trays/{id}/mark-printed/
    - GET /api/stock-summary/
    - GET /api/stock-movements/
    - POST /api/stock-movements/
    """

    @classmethod
    def setUpTestData(cls):
        with schema_context('public'):
            cls.public_client, _ = Client.objects.get_or_create(
                schema_name='public',
                defaults={'name': 'Public Platform'}
            )
            Domain.objects.get_or_create(
                domain='localhost',
                defaults={'tenant': cls.public_client, 'is_primary': True}
            )
            cls.tenant = Client.objects.filter(schema_name='demo').first()
            if not cls.tenant:
                cls.tenant, _ = Client.objects.get_or_create(schema_name='demo', defaults={'name': 'Demo Jewellers', 'is_active': True})
                Domain.objects.get_or_create(domain='demo.localhost', defaults={'tenant': cls.tenant, 'is_primary': True})

        with schema_context(cls.tenant.schema_name):
            cls.branch = Branch.objects.create(
                name="Main Showroom",
                address="100 Sarafa Bazar, Gadag",
                phone="9449642640",
                gstin="29ADNPP6515B1ZF",
                is_active=True
            )
            cls.owner = User.objects.create_user(
                username="prod_owner",
                password="Owner*Vault9",
                role=User.Role.OWNER,
                branch=cls.branch
            )
            cls.staff = User.objects.create_user(
                username="prod_staff",
                password="Worker*Vault8",
                role=User.Role.STAFF,
                branch=cls.branch
            )

            # Pre-populate base category and purity
            cls.category = Category.objects.create(name="Gold Rings", description="Pure gold rings")
            cls.purity = Purity.objects.create(name="22K", fineness=Decimal('0.916'))

    def setUp(self):
        self.client = TestClient()
        with schema_context(self.tenant.schema_name):
            self.owner.tenant_schema = self.tenant.schema_name
            self.staff.tenant_schema = self.tenant.schema_name
            self.owner_token = create_token(self.owner, token_type='access')
            self.staff_token = create_token(self.staff, token_type='access')

    # -------------------------------------------------------------------------
    # Categories & Purities
    # -------------------------------------------------------------------------
    def test_categories_crud(self):
        with schema_context(self.tenant.schema_name):
            # List categories
            res = self.client.get(
                '/api/categories/',
                HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertTrue(any(c['name'] == 'Gold Rings' for c in data))

            # Create new category as owner
            res = self.client.post(
                '/api/categories/',
                data=json.dumps({"name": "Bangles", "description": "Gold bangles"}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res.status_code, 201)
            cat_id = res.json()['id']

            # Duplicate name rejected
            res_dup = self.client.post(
                '/api/categories/',
                data=json.dumps({"name": "Bangles", "description": "Duplicate"}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_dup.status_code, 400)

            # Staff cannot create category (role restricted)
            res_forbidden = self.client.post(
                '/api/categories/',
                data=json.dumps({"name": "Necklaces", "description": ""}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_forbidden.status_code, 403)

    def test_purities_crud(self):
        with schema_context(self.tenant.schema_name):
            # List purities
            res = self.client.get(
                '/api/purities/',
                HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res.status_code, 200)
            self.assertTrue(any(p['name'] == '22K' for p in res.json()))

            # Create new purity
            res = self.client.post(
                '/api/purities/',
                data=json.dumps({"name": "18K", "fineness": "0.750"}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res.status_code, 201)

            # Duplicate purity rejected
            res_dup = self.client.post(
                '/api/purities/',
                data=json.dumps({"name": "18K", "fineness": "0.750"}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_dup.status_code, 400)

    # -------------------------------------------------------------------------
    # Products CRUD, Validation, and QR Tag Generation
    # -------------------------------------------------------------------------
    def test_product_create_and_detail(self):
        with schema_context(self.tenant.schema_name):
            payload = {
                "name": "Emerald Royal Ring",
                "sku": "SKU-RING-001",
                "category_id": self.category.id,
                "purity_id": self.purity.id,
                "gross_weight": "12.500",
                "stone_weight": "1.200",
                "other_weight": "0.300",
                "making_charge_type": "PERCENTAGE",
                "making_charge_value": "12.00",
                "initial_stock": 5,
                "hsn_code": "7113",
                "huid": "HUID778899",
                "description": "Hallmarked ring",
                "branch_id": self.branch.id
            }
            res = self.client.post(
                '/api/products/',
                data=json.dumps(payload),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res.status_code, 201)
            prod_data = res.json()
            prod_id = prod_data['id']
            self.assertEqual(prod_data['sku'], "SKU-RING-001")
            self.assertEqual(Decimal(str(prod_data['net_weight'])), Decimal('11.000'))
            self.assertIsNotNone(prod_data['qr_token'])

            # Verify GET /api/products/{id}/
            res_get = self.client.get(
                f'/api/products/{prod_id}/',
                HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_get.status_code, 200)
            self.assertEqual(res_get.json()['huid'], "HUID778899")

            # Verify GET /api/products/ list with search
            res_list = self.client.get(
                '/api/products/?search=Emerald',
                HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_list.status_code, 200)
            self.assertTrue(len(res_list.json()) >= 1)

            # Verify validation: stone + other >= gross weight rejected
            invalid_payload = dict(payload)
            invalid_payload['sku'] = "SKU-INVALID-001"
            invalid_payload['gross_weight'] = "5.000"
            invalid_payload['stone_weight'] = "4.000"
            invalid_payload['other_weight'] = "1.500"
            res_inv = self.client.post(
                '/api/products/',
                data=json.dumps(invalid_payload),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_inv.status_code, 400)
            self.assertIn("must be less than Gross weight", res_inv.json().get('error', ''))

    def test_product_update_and_delete(self):
        with schema_context(self.tenant.schema_name):
            prod = Product.objects.create(
                name="Traditional Kada",
                sku="SKU-KADA-001",
                category=self.category,
                purity=self.purity,
                gross_weight=Decimal('25.000'),
                stone_weight=Decimal('0.000'),
                other_weight=Decimal('0.000'),
                branch=self.branch,
                is_active=True
            )

            # PUT update
            res = self.client.put(
                f'/api/products/{prod.id}/',
                data=json.dumps({
                    "name": "Updated Kada",
                    "gross_weight": "26.000",
                    "stone_weight": "1.000",
                    "description": "Updated craftsmanship"
                }),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res.status_code, 200)
            with schema_context(self.tenant.schema_name):
                prod = Product.objects.get(id=prod.id)
                self.assertEqual(prod.name, "Updated Kada")
                self.assertEqual(prod.gross_weight, Decimal('26.000'))
                self.assertEqual(prod.net_weight, Decimal('25.000'))

            # DELETE soft delete
            res_del = self.client.delete(
                f'/api/products/{prod.id}/',
                HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_del.status_code, 200)
            with schema_context(self.tenant.schema_name):
                prod = Product.objects.get(id=prod.id)
                self.assertFalse(prod.is_active)

    def test_product_regenerate_qr_and_upload_photo(self):
        with schema_context(self.tenant.schema_name):
            prod = Product.objects.create(
                name="Solitaire Pendant",
                sku="SKU-PENDANT-001",
                category=self.category,
                purity=self.purity,
                gross_weight=Decimal('8.500'),
                stone_weight=Decimal('0.500'),
                other_weight=Decimal('0.000'),
                branch=self.branch
            )

            # POST regenerate-qr
            res_qr = self.client.post(
                f'/api/products/{prod.id}/regenerate-qr/',
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_qr.status_code, 200)
            self.assertIn("qr_data", res_qr.json())

            # POST upload photo (valid JPEG)
            dummy_image = BytesIO(b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08")
            photo_file = SimpleUploadedFile("pendant.jpg", dummy_image.getvalue(), content_type="image/jpeg")

            res_photo = self.client.post(
                f'/api/products/{prod.id}/upload-photo/',
                data={'photo': photo_file},
                HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_photo.status_code, 200)
            with schema_context(self.tenant.schema_name):
                prod = Product.objects.get(id=prod.id)
                self.assertTrue(bool(prod.photo))

            # POST upload invalid extension/content-type
            bad_file = SimpleUploadedFile("script.sh", b"#!/bin/bash echo bad", content_type="text/plain")
            res_bad = self.client.post(
                f'/api/products/{prod.id}/upload-photo/',
                data={'photo': bad_file},
                HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_bad.status_code, 400)

    # -------------------------------------------------------------------------
    # QR Tags & Trays
    # -------------------------------------------------------------------------
    def test_qr_tags_and_trays_operations(self):
        with schema_context(self.tenant.schema_name):
            prod1 = Product.objects.create(
                name="Necklace 1",
                sku="SKU-NECK-001",
                category=self.category,
                purity=self.purity,
                gross_weight=Decimal('30.000'),
                branch=self.branch
            )
            prod2 = Product.objects.create(
                name="Necklace 2",
                sku="SKU-NECK-002",
                category=self.category,
                purity=self.purity,
                gross_weight=Decimal('35.000'),
                branch=self.branch
            )

            # Batch generate QR tags
            res_batch = self.client.post(
                '/api/qr-tags/batch-generate/',
                data=json.dumps({"product_ids": [prod1.id, prod2.id]}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_batch.status_code, 200)
            self.assertEqual(len(res_batch.json()), 2)

            tag_id = res_batch.json()[0]['id']

            # GET single qr tag
            res_tag = self.client.get(
                f'/api/qr-tags/{tag_id}/',
                HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_tag.status_code, 200)
            self.assertEqual(res_tag.json()['id'], tag_id)

            # POST mark-printed
            res_printed = self.client.post(
                f'/api/qr-tags/{tag_id}/mark-printed/',
                HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_printed.status_code, 200)
            self.assertGreaterEqual(res_printed.json()['printed_count'], 1)

            # POST regenerate
            res_regen = self.client.post(
                f'/api/qr-tags/{tag_id}/regenerate/',
                HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_regen.status_code, 200)

            # Create Tray / Group QR
            tray_payload = {
                "name": "Wedding Collection Tray",
                "code": "TRAY-WED-01",
                "description": "Exclusive gold set",
                "product_ids": [prod1.id, prod2.id]
            }
            res_tray = self.client.post(
                '/api/trays/',
                data=json.dumps(tray_payload),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_tray.status_code, 201)
            tray_data = res_tray.json()
            tray_id = tray_data['id']
            self.assertEqual(tray_data['code'], "TRAY-WED-01")
            self.assertEqual(tray_data['total_items'], 2)

            # GET trays list
            res_trays = self.client.get(
                '/api/trays/',
                HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_trays.status_code, 200)
            self.assertTrue(any(t['id'] == tray_id for t in res_trays.json()))

            # GET tray by ID
            res_tray_id = self.client.get(
                f'/api/trays/{tray_id}/',
                HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_tray_id.status_code, 200)

            # GET tray by code
            res_by_code = self.client.get(
                '/api/trays/by-code/TRAY-WED-01/',
                HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_by_code.status_code, 200)

            # Mark tray printed
            res_tp = self.client.post(
                f'/api/trays/{tray_id}/mark-printed/',
                HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_tp.status_code, 200)
            self.assertEqual(res_tp.json()['printed_count'], 1)

            # Regenerate tray
            res_tr = self.client.post(
                f'/api/trays/{tray_id}/regenerate/',
                HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_tr.status_code, 200)

            # PUT update tray
            res_tu = self.client.put(
                f'/api/trays/{tray_id}/',
                data=json.dumps({"name": "Updated Wedding Tray"}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_tu.status_code, 200)
            self.assertEqual(res_tu.json()['name'], "Updated Wedding Tray")

            # DELETE tray
            res_td = self.client.delete(
                f'/api/trays/{tray_id}/',
                HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_td.status_code, 200)

    # -------------------------------------------------------------------------
    # Stock Ledger & Summaries
    # -------------------------------------------------------------------------
    def test_stock_movements_and_summary(self):
        with schema_context(self.tenant.schema_name):
            prod = Product.objects.create(
                name="Gold Chain 24-Inch",
                sku="SKU-CHN-001",
                category=self.category,
                purity=self.purity,
                gross_weight=Decimal('18.000'),
                branch=self.branch
            )

            # Record stock IN
            res_in = self.client.post(
                '/api/stock-movements/',
                data=json.dumps({
                    "product_id": prod.id,
                    "movement_type": "IN",
                    "quantity": 10,
                    "reference_type": "purchase_order",
                    "reference_id": 1001,
                    "note": "Received 10 chains"
                }),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_in.status_code, 201)
            self.assertEqual(res_in.json()['quantity'], 10)

            # Record stock ADJUSTMENT (e.g. damaged or discrepancy)
            res_adj = self.client.post(
                '/api/stock-movements/',
                data=json.dumps({
                    "product_id": prod.id,
                    "movement_type": "OUT",
                    "quantity": 2,
                    "reference_type": "audit_adjustment",
                    "note": "Moved to melting"
                }),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_adj.status_code, 201)

            # GET stock-summary
            res_sum = self.client.get(
                '/api/stock-summary/?search=SKU-CHN-001',
                HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_sum.status_code, 200)
            items = res_sum.json()
            self.assertEqual(len(items), 1)
            self.assertEqual(items[0]['quantity_on_hand'], 8)

            # GET stock-movements list
            res_movs = self.client.get(
                f'/api/stock-movements/?product_id={prod.id}',
                HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_movs.status_code, 200)
            self.assertEqual(len(res_movs.json()), 2)
