import json
from decimal import Decimal
from django.test import TestCase, Client as TestClient
from django_tenants.utils import schema_context
from apps.tenants.models import Client, Domain
from apps.accounts.models import User, Branch
from apps.products.models import Category, Purity, Product
from apps.qr_tags.models import Tray
from apps.billing.models import POSPairingSession
from apps.billing.pairing import resolve_and_record_scan
from ninja_api.auth import create_token


class TrayQRTagsTestCase(TestCase):
    """
    Unit & Integration tests for Clubbing QR Codes and Group Tray QR Tags.
    """

    @classmethod
    def setUpTestData(cls):
        with schema_context('public'):
            cls.tenant = Client.objects.filter(schema_name='demo').first()
            if not cls.tenant:
                cls.tenant = Client(schema_name='demo', name='Demo Jewellery')
                cls.tenant.save()
                Domain.objects.create(domain='demo.localhost', tenant=cls.tenant, is_primary=True)

        with schema_context(cls.tenant.schema_name):
            cls.branch = Branch.objects.create(name="Main Showroom")
            cls.user = User.objects.create_user(
                username="tray_mgr",
                password="TestPassword@123",
                role=User.Role.MANAGER,
                branch=cls.branch,
            )
            cls.category = Category.objects.create(name="Bangles")
            cls.purity = Purity.objects.create(name="22KT (916)", fineness=Decimal("0.916"))

            # Create multiple products to club
            cls.prod1 = Product.objects.create(
                name="Antique Kada 1",
                sku="KADA-22K-001",
                category=cls.category,
                purity=cls.purity,
                gross_weight=Decimal("25.500"),
                stone_weight=Decimal("1.500"),
                other_weight=Decimal("0.000"),
                huid="HUID101",
                branch=cls.branch,
            )
            cls.prod2 = Product.objects.create(
                name="Antique Kada 2",
                sku="KADA-22K-002",
                category=cls.category,
                purity=cls.purity,
                gross_weight=Decimal("24.800"),
                stone_weight=Decimal("0.800"),
                other_weight=Decimal("0.000"),
                huid="HUID102",
                branch=cls.branch,
            )
            cls.prod3 = Product.objects.create(
                name="Antique Kada 3",
                sku="KADA-22K-003",
                category=cls.category,
                purity=cls.purity,
                gross_weight=Decimal("26.200"),
                stone_weight=Decimal("1.200"),
                other_weight=Decimal("0.000"),
                huid="HUID103",
                branch=cls.branch,
            )

    def setUp(self):
        self.client = TestClient()
        with schema_context(self.tenant.schema_name):
            self.token = create_token(self.user)

    def test_club_qr_codes_into_tray(self):
        """Test creating a Tray by clubbing multiple products and generating a group QR tag."""
        with schema_context(self.tenant.schema_name):
            payload = {
                "name": "Display Tray 1 - 22KT Kadas",
                "code": "TRAY-2026-001",
                "description": "Counter 1 front display",
                "product_ids": [self.prod1.id, self.prod2.id, self.prod3.id],
            }

            res = self.client.post(
                '/api/trays/',
                data=json.dumps(payload),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 201)
            data = res.json()
            self.assertEqual(data['code'], "TRAY-2026-001")
            self.assertEqual(data['name'], "Display Tray 1 - 22KT Kadas")
            self.assertEqual(data['total_items'], 3)

            # Gross weight: 25.500 + 24.800 + 26.200 = 76.500
            self.assertEqual(Decimal(str(data['total_gross_weight'])), Decimal("76.500"))
            # Net weight: 24.000 + 24.000 + 25.000 = 73.000
            self.assertEqual(Decimal(str(data['total_net_weight'])), Decimal("73.000"))
            # Stone weight: 1.500 + 0.800 + 1.200 = 3.500
            self.assertEqual(Decimal(str(data['total_stone_weight'])), Decimal("3.500"))

            self.assertIsNotNone(data['qr_image_url'])
            self.assertIn("qr_data", data)
            qr_payload = json.loads(data['qr_data'])
            self.assertEqual(qr_payload['type'], "tray")
            self.assertEqual(qr_payload['code'], "TRAY-2026-001")
            self.assertEqual(len(qr_payload['items']), 3)

            # Verify itemized list in response
            items = data['items']
            self.assertEqual(len(items), 3)
            skus = {it['sku'] for it in items}
            self.assertEqual(skus, {"KADA-22K-001", "KADA-22K-002", "KADA-22K-003"})

    def test_list_and_get_tray_details(self):
        """Test retrieving all trays and fetching a specific tray by ID or code."""
        with schema_context(self.tenant.schema_name):
            tray = Tray.objects.create(
                code="TRAY-GOLD-099",
                name="Gold Bangles Set",
                description="Special collection",
            )
            tray.items.set([self.prod1, self.prod2])

            # List trays
            res = self.client.get(
                '/api/trays/',
                HTTP_AUTHORIZATION=f'Bearer {self.token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 200)
            trays = res.json()
            matching = [t for t in trays if t['code'] == "TRAY-GOLD-099"]
            self.assertEqual(len(matching), 1)
            self.assertEqual(matching[0]['total_items'], 2)

            # Get tray by ID
            res_id = self.client.get(
                f'/api/trays/{tray.id}/',
                HTTP_AUTHORIZATION=f'Bearer {self.token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res_id.status_code, 200)
            self.assertEqual(res_id.json()['id'], tray.id)
            self.assertEqual(len(res_id.json()['items']), 2)

            # Get tray by Code
            res_code = self.client.get(
                f'/api/trays/by-code/{tray.code}/',
                HTTP_AUTHORIZATION=f'Bearer {self.token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res_code.status_code, 200)
            self.assertEqual(res_code.json()['code'], "TRAY-GOLD-099")

    def test_update_and_delete_tray(self):
        """Test modifying items in a tray and deleting a tray."""
        with schema_context(self.tenant.schema_name):
            tray = Tray.objects.create(
                code="TRAY-TEMP-001",
                name="Temporary Tray",
            )
            tray.items.set([self.prod1])

            # Update tray: change name and add prod2
            update_payload = {
                "name": "Updated Tray Name",
                "product_ids": [self.prod1.id, self.prod2.id],
            }
            res = self.client.put(
                f'/api/trays/{tray.id}/',
                data=json.dumps(update_payload),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 200)
            updated_data = res.json()
            self.assertEqual(updated_data['name'], "Updated Tray Name")
            self.assertEqual(updated_data['total_items'], 2)

            # Delete tray
            del_res = self.client.delete(
                f'/api/trays/{tray.id}/',
                HTTP_AUTHORIZATION=f'Bearer {self.token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(del_res.status_code, 200)
            self.assertFalse(Tray.objects.filter(id=tray.id).exists())
            # Underlying products must remain intact
            self.assertTrue(Product.objects.filter(id=self.prod1.id).exists())

    def test_scanner_tray_resolution(self):
        """Test that scanning a group QR code payload resolves the tray and all its items."""
        with schema_context(self.tenant.schema_name):
            from django.utils import timezone
            import datetime

            tray = Tray.objects.create(
                code="TRAY-SCAN-001",
                name="Scannable Tray",
            )
            tray.items.set([self.prod1, self.prod2])

            session = POSPairingSession.objects.create(
                session_id="sess_test_123",
                pairing_code="123456",
                user=self.user,
                branch=self.branch,
                expires_at=timezone.now() + datetime.timedelta(hours=1),
                is_active=True,
            )

            # 1. Test scanning with JSON payload containing type='tray'
            qr_payload = json.dumps({
                "type": "tray",
                "tray_id": tray.id,
                "code": tray.code,
                "name": tray.name,
            })
            prod_data, err, is_dup = resolve_and_record_scan(session, "evt_tray_1", qr_payload)
            self.assertIsNone(err)
            self.assertFalse(is_dup)
            self.assertTrue(prod_data.get('is_tray'))
            self.assertEqual(prod_data['tray_code'], "TRAY-SCAN-001")
            self.assertEqual(prod_data['total_items'], 2)
            self.assertEqual(len(prod_data['items']), 2)

            # 2. Test scanning with plain string TRAY code
            prod_data2, err2, is_dup2 = resolve_and_record_scan(session, "evt_tray_2", "TRAY-SCAN-001")
            self.assertIsNone(err2)
            self.assertFalse(is_dup2)
            self.assertTrue(prod_data2.get('is_tray'))
            self.assertEqual(prod_data2['tray_code'], "TRAY-SCAN-001")
