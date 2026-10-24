import json
import uuid
from decimal import Decimal
from django.test import TestCase, Client as TestClient
from django_tenants.utils import schema_context
from apps.tenants.models import Client, Domain
from apps.billing.models import Bill, Item, IdempotencyRecord
from ninja_api.auth import decode_token, generate_bill_token


class BackendAuthoritativePollingTestCase(TestCase):
    """
    Test suite for the Backend-Authoritative HTTP Polling Pattern:
    - Scoped JWT generation & HTTPS pairing
    - Optimized short-polling GET endpoint
    - Idempotency key handling (safe mobile retries)
    - Concurrency row locking (select_for_update) & 409 Conflict on double-scan
    - Path bill_id security validation
    - Multi-tenant schema isolation for Bills & Items
    """

    @classmethod
    def setUpTestData(cls):
        # 1. Primary Tenant (demo)
        cls.tenant = Client.objects.filter(schema_name='demo').first()
        if not cls.tenant:
            cls.tenant = Client(schema_name='demo', name='Demo Jewellery')
            cls.tenant.save()
            Domain.objects.create(domain='demo.localhost', tenant=cls.tenant, is_primary=True)

        # 2. Secondary Tenant for isolation tests (tenant_kalyan)
        cls.tenant_kalyan = Client.objects.filter(schema_name='tenant_kalyan').first()
        if not cls.tenant_kalyan:
            cls.tenant_kalyan = Client(schema_name='tenant_kalyan', name='Kalyan Heritage')
            cls.tenant_kalyan.save()
            Domain.objects.create(domain='kalyan.localhost', tenant=cls.tenant_kalyan, is_primary=True)

    def setUp(self):
        self.client = TestClient()

    def test_create_bill_and_scoped_token(self):
        """Verify POST /api/bills/ creates Bill and returns scoped JWT."""
        with schema_context(self.tenant.schema_name):
            res = self.client.post(
                '/api/bills/',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 201)
            data = res.json()

            bill_id = uuid.UUID(data['bill_id'])
            self.assertEqual(data['status'], 'DRAFT')
            self.assertIn('token', data)
            self.assertIn('https://', data['https_url'])

            # Verify Bill exists in tenant database
            bill = Bill.objects.get(id=bill_id)
            self.assertEqual(bill.status, Bill.Status.DRAFT)

            # Verify JWT payload claims
            payload = decode_token(data['token'], expected_type='access')  # or jwt.decode directly
            import jwt
            from django.conf import settings
            claims = jwt.decode(data['token'], settings.JWT_SECRET_KEY, algorithms=['HS256'])
            self.assertEqual(claims['bill_id'], str(bill_id))
            self.assertEqual(claims['tenant_schema'], 'demo')
            self.assertEqual(claims['scope'], 'bill_session')

    def test_get_bill_cart_polling_and_weight_aggregation(self):
        """Verify GET /api/bills/{bill_id} returns accurate cart items and total weight."""
        with schema_context(self.tenant.schema_name):
            bill = Bill.objects.create(status=Bill.Status.DRAFT)
            token = generate_bill_token('demo', bill.id)

            # Initial empty cart
            res = self.client.get(
                f'/api/bills/{bill.id}',
                HTTP_AUTHORIZATION=f'Bearer {token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data['item_count'], 0)
            self.assertEqual(Decimal(str(data['total_weight'])), Decimal('0.000'))

            # Add two items to cart
            it1 = Item.objects.create(
                qr_code="TEST-RING-01",
                name="22KT Gold Ring",
                weight=Decimal("5.500"),
                status=Item.Status.IN_CART,
                locked_by_bill=bill
            )
            it2 = Item.objects.create(
                qr_code="TEST-CHAIN-02",
                name="22KT Gold Chain",
                weight=Decimal("12.250"),
                status=Item.Status.IN_CART,
                locked_by_bill=bill
            )

            # Poll cart again
            poll_res = self.client.get(
                f'/api/bills/{bill.id}',
                HTTP_AUTHORIZATION=f'Bearer {token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(poll_res.status_code, 200)
            poll_data = poll_res.json()
            self.assertEqual(poll_data['item_count'], 2)
            self.assertEqual(Decimal(str(poll_data['total_weight'])), Decimal("17.750"))
            self.assertEqual(len(poll_data['items']), 2)

    def test_scan_item_concurrency_lock_and_cart_mutation(self):
        """Verify POST /api/bills/{bill_id}/scan atomically locks and updates item status."""
        with schema_context(self.tenant.schema_name):
            bill = Bill.objects.create(status=Bill.Status.DRAFT)
            token = generate_bill_token('demo', bill.id)

            item = Item.objects.create(
                qr_code="BRACELET-22K-999",
                name="Gold Temple Bracelet",
                weight=Decimal("24.800"),
                status=Item.Status.AVAILABLE
            )

            scan_res = self.client.post(
                f'/api/bills/{bill.id}/scan',
                data=json.dumps({"qr_code": "BRACELET-22K-999"}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {token}',
                HTTP_IDEMPOTENCY_KEY='MOBILE-UUID-SCAN-1',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(scan_res.status_code, 200)
            data = scan_res.json()
            self.assertEqual(data['status'], 'success')
            self.assertFalse(data['is_duplicate'])

            # Verify in DB: item is now IN_CART and locked by bill
            item.refresh_from_db()
            self.assertEqual(item.status, Item.Status.IN_CART)
            self.assertEqual(item.locked_by_bill_id, bill.id)

            # Verify IdempotencyRecord was created
            record = IdempotencyRecord.objects.get(bill=bill, key='MOBILE-UUID-SCAN-1')
            self.assertIsNotNone(record)

    def test_idempotency_key_replay_prevents_duplicate_scan(self):
        """Verify duplicate scan requests with same Idempotency-Key safely return 200 without side-effects."""
        with schema_context(self.tenant.schema_name):
            bill = Bill.objects.create(status=Bill.Status.DRAFT)
            token = generate_bill_token('demo', bill.id)

            item = Item.objects.create(
                qr_code="PENDANT-18K-001",
                name="Diamond Pendant",
                weight=Decimal("3.200"),
                status=Item.Status.AVAILABLE
            )

            # First scan
            res1 = self.client.post(
                f'/api/bills/{bill.id}/scan',
                data=json.dumps({"qr_code": "PENDANT-18K-001"}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {token}',
                HTTP_IDEMPOTENCY_KEY='RETRY-KEY-555',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res1.status_code, 200)
            self.assertFalse(res1.json()['is_duplicate'])

            # Second scan (mobile network retry with same idempotency key)
            res2 = self.client.post(
                f'/api/bills/{bill.id}/scan',
                data=json.dumps({"qr_code": "PENDANT-18K-001"}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {token}',
                HTTP_IDEMPOTENCY_KEY='RETRY-KEY-555',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res2.status_code, 200)
            self.assertTrue(res2.json()['is_duplicate'])
            self.assertIn("Idempotent replay", res2.json()['message'])

            # Check that only one idempotency record exists
            self.assertEqual(IdempotencyRecord.objects.filter(bill=bill, key='RETRY-KEY-555').count(), 1)
            # Item remains IN_CART once
            self.assertEqual(bill.items.count(), 1)

    def test_concurrency_conflict_409_when_item_already_in_cart_or_sold(self):
        """Verify that scanning an item that is already IN_CART or SOLD returns 409 Conflict."""
        with schema_context(self.tenant.schema_name):
            bill1 = Bill.objects.create(status=Bill.Status.DRAFT)
            bill2 = Bill.objects.create(status=Bill.Status.DRAFT)
            token2 = generate_bill_token('demo', bill2.id)

            # Item already in Bill 1
            item = Item.objects.create(
                qr_code="UNIQUE-TIARA-01",
                name="Bridal Tiara",
                weight=Decimal("50.000"),
                status=Item.Status.IN_CART,
                locked_by_bill=bill1
            )

            # Bill 2 tries to scan the same item
            res = self.client.post(
                f'/api/bills/{bill2.id}/scan',
                data=json.dumps({"qr_code": "UNIQUE-TIARA-01"}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {token2}',
                HTTP_IDEMPOTENCY_KEY='BILL2-SCAN-KEY',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 409)
            self.assertIn("not available", res.json()['error'])
            self.assertIn("IN_CART", res.json()['error'])

            # Also test when item status is SOLD
            item.status = Item.Status.SOLD
            item.save()

            res_sold = self.client.post(
                f'/api/bills/{bill2.id}/scan',
                data=json.dumps({"qr_code": "UNIQUE-TIARA-01"}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {token2}',
                HTTP_IDEMPOTENCY_KEY='BILL2-SCAN-KEY-2',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res_sold.status_code, 409)
            self.assertIn("SOLD", res_sold.json()['error'])

    def test_scan_missing_idempotency_key_header(self):
        """Verify missing Idempotency-Key returns HTTP 400 Bad Request."""
        with schema_context(self.tenant.schema_name):
            bill = Bill.objects.create(status=Bill.Status.DRAFT)
            token = generate_bill_token('demo', bill.id)

            res = self.client.post(
                f'/api/bills/{bill.id}/scan',
                data=json.dumps({"qr_code": "ANY-QR"}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 400)
            self.assertIn("Idempotency-Key", res.json()['error'])

    def test_scan_nonexistent_item_returns_404(self):
        """Verify scanning a non-existent QR code returns HTTP 404."""
        with schema_context(self.tenant.schema_name):
            bill = Bill.objects.create(status=Bill.Status.DRAFT)
            token = generate_bill_token('demo', bill.id)

            res = self.client.post(
                f'/api/bills/{bill.id}/scan',
                data=json.dumps({"qr_code": "NONEXISTENT-BARCODE-999"}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {token}',
                HTTP_IDEMPOTENCY_KEY='KEY-NONEXISTENT',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 404)
            self.assertIn("does not exist", res.json()['error'])

    def test_token_bill_id_mismatch_security(self):
        """Verify that a token issued for Bill A cannot access or mutate Bill B."""
        with schema_context(self.tenant.schema_name):
            bill_a = Bill.objects.create(status=Bill.Status.DRAFT)
            bill_b = Bill.objects.create(status=Bill.Status.DRAFT)
            token_a = generate_bill_token('demo', bill_a.id)

            # Attempt to use token_a on bill_b
            res = self.client.get(
                f'/api/bills/{bill_b.id}',
                HTTP_AUTHORIZATION=f'Bearer {token_a}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 401)

            res_scan = self.client.post(
                f'/api/bills/{bill_b.id}/scan',
                data=json.dumps({"qr_code": "ANY-QR"}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {token_a}',
                HTTP_IDEMPOTENCY_KEY='KEY-MISMATCH',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res_scan.status_code, 401)

    def test_cross_tenant_isolation_on_bills_and_items(self):
        """
        Verify strict PostgreSQL schema multi-tenancy:
        Bill created in Tenant 1 (demo) cannot see or lock items in Tenant 2 (tenant_kalyan).
        """
        # Create item in Tenant 2
        with schema_context(self.tenant_kalyan.schema_name):
            item_kalyan = Item.objects.create(
                qr_code="SHARED-SKU-777",
                name="Kalyan Special Ring",
                weight=Decimal("8.000"),
                status=Item.Status.AVAILABLE
            )

        # In Tenant 1, create a Bill and try to scan "SHARED-SKU-777"
        with schema_context(self.tenant.schema_name):
            bill_demo = Bill.objects.create(status=Bill.Status.DRAFT)
            token_demo = generate_bill_token('demo', bill_demo.id)

            res = self.client.post(
                f'/api/bills/{bill_demo.id}/scan',
                data=json.dumps({"qr_code": "SHARED-SKU-777"}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {token_demo}',
                HTTP_IDEMPOTENCY_KEY='CROSS-TENANT-KEY',
                HTTP_X_TENANT='demo'
            )
            # Must return 404 because the item only exists in Tenant 2's schema!
            self.assertEqual(res.status_code, 404)

        # Confirm that in Tenant 2, the item is still AVAILABLE and unlocked
        with schema_context(self.tenant_kalyan.schema_name):
            item_kalyan.refresh_from_db()
            self.assertEqual(item_kalyan.status, Item.Status.AVAILABLE)
            self.assertIsNone(item_kalyan.locked_by_bill)
