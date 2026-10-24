import json
from decimal import Decimal
from django.test import TestCase, Client as HttpClient
from django_tenants.utils import schema_context

from apps.tenants.models import Client, Domain
from apps.accounts.models import User, Branch
from apps.products.models import Product, Category, Purity
from ninja_api.auth import create_token


class StoreOnboardingAndRBACTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Setup base public tenant and demo tenant
        with schema_context('public'):
            cls.public_tenant, _ = Client.objects.get_or_create(
                schema_name='public',
                defaults={'name': 'Public System'}
            )
            Domain.objects.get_or_create(
                domain='localhost',
                defaults={'tenant': cls.public_tenant, 'is_primary': True}
            )

            cls.demo_tenant, _ = Client.objects.get_or_create(
                schema_name='demo',
                defaults={'name': 'Demo Jewellers'}
            )
            Domain.objects.get_or_create(
                domain='demo.localhost',
                defaults={'tenant': cls.demo_tenant, 'is_primary': True}
            )

        with schema_context(cls.demo_tenant.schema_name):
            cls.branch = Branch.objects.create(name='Main Showroom', is_active=True)
            cls.cat = Category.objects.create(name='Gold Rings')
            cls.purity = Purity.objects.create(name='22KT 916', fineness=Decimal('0.916'))

            cls.owner = User.objects.create_user(
                username='store_owner',
                password='Owner*Vault9',
                role=User.Role.OWNER,
                branch=cls.branch
            )
            cls.staff = User.objects.create_user(
                username='counter_salesman',
                password='Staff*Vault8',
                role=User.Role.STAFF,
                branch=cls.branch
            )
            cls.product = Product.objects.create(
                name='Classic Gold Band',
                category=cls.cat,
                purity=cls.purity,
                gross_weight=Decimal('5.500'),
                stone_weight=Decimal('0.000'),
                making_charge_type='per_gram',
                making_charge_value=Decimal('450.00'),
                branch=cls.branch,
                is_active=True
            )

        cls.client = HttpClient()

    @classmethod
    def tearDownClass(cls):
        from django.db import connection
        connection.set_schema_to_public()
        super().tearDownClass()

    def test_store_registration_success(self):
        payload = {
            "shop_name": "Sita Lakshmi Jewellers",
            "owner_username": "sita_owner",
            "owner_password": "Sita#Vault9",  # Compliant password
            "owner_email": "sita@example.com",
            "owner_phone": "9876543210",
            "address": "45 M.G. Road, Bangalore",
            "gstin": "29AAAAA0000A1Z5",
        }
        res = self.client.post(
            '/api/tenants/register-store/',
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_HOST='localhost'
        )
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertIn("schema_name", data)
        self.assertIn("access", data)
        self.assertTrue(Client.objects.filter(schema_name=data['schema_name']).exists())

        # Verify initial records inside newly provisioned tenant schema
        with schema_context(data['schema_name']):
            self.assertTrue(User.objects.filter(username="sita_owner", role=User.Role.OWNER).exists())
            self.assertTrue(Branch.objects.filter(name="Main Showroom").exists())
            self.assertTrue(Category.objects.filter(name="Gold Jewellery").exists())
            self.assertTrue(Purity.objects.filter(name="22KT Hallmarked 916").exists())

    def test_store_registration_rejects_weak_or_consecutive_password(self):
        # Rejected because of consecutive numbers 123
        payload_consecutive_num = {
            "shop_name": "Test Jewellers",
            "owner_username": "bad_owner1",
            "owner_password": "Owner#Shop123",
            "owner_phone": "9876543210",
        }
        res = self.client.post(
            '/api/tenants/register-store/',
            data=json.dumps(payload_consecutive_num),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 422)  # Pydantic validation error

        # Rejected because of consecutive duplicate letters 'ss'
        payload_consecutive_letters = {
            "shop_name": "Test Jewellers",
            "owner_username": "bad_owner2",
            "owner_password": "Pass#word8",
            "owner_phone": "9876543210",
        }
        res = self.client.post(
            '/api/tenants/register-store/',
            data=json.dumps(payload_consecutive_letters),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 422)

    def test_owner_can_create_salesman_with_compliant_password(self):
        with schema_context(self.demo_tenant.schema_name):
            owner_tok = create_token(self.owner, token_type='access')
            res = self.client.post(
                '/api/users/',
                data=json.dumps({
                    "username": "ramesh_sales",
                    "password": "Ramesh*Safe9",
                    "role": "staff",
                    "first_name": "Ramesh",
                    "phone": "9123456789",
                    "branch_id": self.branch.id,
                }),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {owner_tok}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 201)
            self.assertTrue(User.objects.filter(username="ramesh_sales").exists())

    def test_salesman_creation_fails_with_non_compliant_password(self):
        with schema_context(self.demo_tenant.schema_name):
            owner_tok = create_token(self.owner, token_type='access')
            # Missing special char, has consecutive numbers '123'
            res = self.client.post(
                '/api/users/',
                data=json.dumps({
                    "username": "suresh_sales",
                    "password": "Salesman123",
                    "role": "staff",
                    "branch_id": self.branch.id,
                }),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {owner_tok}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 422)
            self.assertFalse(User.objects.filter(username="suresh_sales").exists())

    def test_salesman_cannot_delete_product(self):
        with schema_context(self.demo_tenant.schema_name):
            staff_tok = create_token(self.staff, token_type='access')
            res = self.client.delete(
                f'/api/products/{self.product.id}/',
                HTTP_AUTHORIZATION=f'Bearer {staff_tok}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 403)
            # Product remains intact and active
            self.product.refresh_from_db()
            self.assertTrue(self.product.is_active)

    def test_salesman_cannot_sync_gold_rates(self):
        with schema_context(self.demo_tenant.schema_name):
            staff_tok = create_token(self.staff, token_type='access')
            res = self.client.post(
                '/api/gold-rates/sync/',
                data=json.dumps({"source": "ksjf"}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {staff_tok}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 403)

    def test_salesman_cannot_close_daybook(self):
        with schema_context(self.demo_tenant.schema_name):
            from apps.accounting.models import DayBook
            from django.utils import timezone
            day = DayBook.objects.create(
                date=timezone.localdate(),
                opening_balance=Decimal('10000.00'),
                branch=self.branch
            )
            staff_tok = create_token(self.staff, token_type='access')
            res = self.client.post(
                f'/api/day-book/{day.id}/close/',
                data=json.dumps({"notes": "Staff attempt"}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {staff_tok}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 403)
            day.refresh_from_db()
            self.assertFalse(day.is_closed)

    def test_owner_can_toggle_salesman_status(self):
        with schema_context(self.demo_tenant.schema_name):
            owner_tok = create_token(self.owner, token_type='access')
            res = self.client.post(
                f'/api/users/{self.staff.id}/toggle-status/',
                data=json.dumps({"is_active": False}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {owner_tok}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 200)
            self.staff.refresh_from_db()
            self.assertFalse(self.staff.is_active)

    def test_owner_cannot_deactivate_self(self):
        with schema_context(self.demo_tenant.schema_name):
            owner_tok = create_token(self.owner, token_type='access')
            res = self.client.post(
                f'/api/users/{self.owner.id}/toggle-status/',
                data=json.dumps({"is_active": False}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {owner_tok}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 400)
            self.owner.refresh_from_db()
            self.assertTrue(self.owner.is_active)

    def test_owner_can_reset_staff_password_with_policy(self):
        with schema_context(self.demo_tenant.schema_name):
            owner_tok = create_token(self.owner, token_type='access')
            res = self.client.post(
                f'/api/users/{self.staff.id}/reset-password/',
                data=json.dumps({"new_password": "New*Worker#Key7"}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {owner_tok}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 200)
            self.staff.refresh_from_db()
            self.assertTrue(self.staff.check_password("New*Worker#Key7"))
