import json
from decimal import Decimal
from django.utils import timezone
from django.test import TestCase, Client as TestClient
from django_tenants.utils import schema_context
from apps.tenants.models import Client, Domain
from apps.accounts.models import User, Branch
from apps.accounting.models import Customer, DayBook, ShopRateSetting, GoldRate
from apps.products.models import Purity
from ninja_api.auth import create_token


class EndpointsAccountingAndDaybookTestCase(TestCase):
    """
    Integration tests covering Accounting, Gold Rates, Customers, DayBook, and Tenant endpoints:
    - GET /api/gold-rates/settings/
    - PUT /api/gold-rates/settings/
    - GET /api/gold-rates/live-market/
    - GET /api/gold-rates/history/
    - GET /api/customers/{id}/
    - PUT /api/customers/{id}/
    - POST /api/day-book/{id}/close_day/
    - POST /api/day-book/{id}/reopen_day/
    - PATCH /api/day-book/{id}/
    - GET /api/tenants/
    - POST /api/tenants/
    - GET /api/tenants/status/{schema_name}/
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

            cls.superadmin = User.objects.create_superuser(
                username="acct_superadmin",
                password="Super*Vault99",
                email="superadmin2@swarnakhata.internal"
            )

        with schema_context(cls.tenant.schema_name):
            cls.branch = Branch.objects.create(
                name="Main Showroom",
                address="100 Sarafa Bazar, Gadag",
                phone="9449642640",
                gstin="29ADNPP6515B1ZF",
                is_active=True
            )
            cls.owner = User.objects.create_user(
                username="acct_owner",
                password="Owner*Vault9",
                role=User.Role.OWNER,
                branch=cls.branch
            )
            cls.staff = User.objects.create_user(
                username="acct_staff",
                password="Worker*Vault8",
                role=User.Role.STAFF,
                branch=cls.branch
            )
            cls.purity = Purity.objects.create(name="22K", fineness=Decimal('0.916'))
            cls.customer = Customer.objects.create(
                name="Suresh Kulkarni",
                phone="9448123456",
                email="suresh@gmail.com",
                address="Pala Badami Road, Gadag",
                pan_number="ABCDE1234F"
            )

    def setUp(self):
        self.client = TestClient()
        with schema_context(self.tenant.schema_name):
            self.owner.tenant_schema = self.tenant.schema_name
            self.staff.tenant_schema = self.tenant.schema_name
            self.owner_token = create_token(self.owner, token_type='access')
            self.staff_token = create_token(self.staff, token_type='access')

        with schema_context('public'):
            self.superadmin.tenant_schema = 'public'
            self.superadmin_token = create_token(self.superadmin, token_type='access')

    # -------------------------------------------------------------------------
    # Gold Rates Settings, Live Market & History
    # -------------------------------------------------------------------------
    def test_gold_rates_settings_and_history(self):
        with schema_context(self.tenant.schema_name):
            # GET rate settings
            res_get = self.client.get(
                '/api/gold-rates/settings/',
                HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_get.status_code, 200)

            # PUT update rate settings (owner/manager only)
            res_put = self.client.put(
                '/api/gold-rates/settings/',
                data=json.dumps({"preferred_source": "ibja"}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_put.status_code, 200)
            self.assertEqual(res_put.json()['preferred_source'], 'ibja')

            # Staff cannot update settings
            res_forbid = self.client.put(
                '/api/gold-rates/settings/',
                data=json.dumps({"preferred_source": "goodreturns"}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_forbid.status_code, 403)

            # Create a rate history entry
            with schema_context(self.tenant.schema_name):
                GoldRate.objects.create(
                    purity=self.purity,
                    rate_per_gram=Decimal('6850.00'),
                    effective_date=timezone.localdate(),
                    is_current=True,
                    entered_by=self.owner
                )

            # GET rate history
            res_hist = self.client.get(
                f'/api/gold-rates/history/?purity_id={self.purity.id}',
                HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_hist.status_code, 200)
            self.assertTrue(len(res_hist.json()) >= 1)

            # GET live market feed
            res_live = self.client.get(
                '/api/gold-rates/live-market/',
                HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_live.status_code, 200)
            self.assertIn("rates", res_live.json())

    # -------------------------------------------------------------------------
    # Customers Detail & Update
    # -------------------------------------------------------------------------
    def test_customer_detail_and_update(self):
        with schema_context(self.tenant.schema_name):
            # GET customer by id
            res_get = self.client.get(
                f'/api/customers/{self.customer.id}/',
                HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_get.status_code, 200)
            self.assertEqual(res_get.json()['name'], "Suresh Kulkarni")

            # PUT update customer
            res_put = self.client.put(
                f'/api/customers/{self.customer.id}/',
                data=json.dumps({
                    "name": "Suresh V Kulkarni",
                    "phone": "9448123456",
                    "email": "suresh.v@gmail.com",
                    "address": "Near Market Yard, Gadag",
                    "pan_number": "ABCDE1234F"
                }),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_put.status_code, 200)
            with schema_context(self.tenant.schema_name):
                updated_cust = Customer.objects.get(id=self.customer.id)
                self.assertEqual(updated_cust.name, "Suresh V Kulkarni")

    # -------------------------------------------------------------------------
    # DayBook Close, Reopen, and Patch
    # -------------------------------------------------------------------------
    def test_day_book_lifecycle_and_patch(self):
        with schema_context(self.tenant.schema_name):
            today = timezone.localdate()
            day_book, _ = DayBook.objects.get_or_create(
                date=today,
                branch=self.branch,
                defaults={
                    "opening_balance": Decimal('10000.00'),
                    "cash_in": Decimal('5000.00'),
                    "cash_out": Decimal('1500.00'),
                    "is_closed": False
                }
            )

            # PATCH update cash values
            res_patch = self.client.patch(
                f'/api/day-book/{day_book.id}/',
                data=json.dumps({
                    "cash_in": "6000.00",
                    "cash_out": "1500.00",
                    "notes": "Verified petty cash drawer"
                }),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_patch.status_code, 200)
            self.assertEqual(Decimal(str(res_patch.json()['cash_in'])), Decimal('6000.00'))

            # POST close_day
            res_close = self.client.post(
                f'/api/day-book/{day_book.id}/close_day/',
                data=json.dumps({"notes": "Evening closing audit complete"}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_close.status_code, 200)
            self.assertTrue(res_close.json()['is_closed'])
            self.assertEqual(Decimal(str(res_close.json()['closing_balance'])), Decimal('14500.00'))

            # Modifying closed daybook via patch should fail
            res_patch_closed = self.client.patch(
                f'/api/day-book/{day_book.id}/',
                data=json.dumps({"cash_in": "7000.00"}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_patch_closed.status_code, 400)

            # POST reopen_day
            res_reopen = self.client.post(
                f'/api/day-book/{day_book.id}/reopen_day/',
                HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_reopen.status_code, 200)
            self.assertFalse(res_reopen.json()['is_closed'])

    # -------------------------------------------------------------------------
    # Tenants Router: List, Validation & Status
    # -------------------------------------------------------------------------
    def test_tenants_router_endpoints(self):
        with schema_context('public'):
            # GET /api/tenants/ (Superadmin only)
            res_list = self.client.get(
                '/api/tenants/',
                HTTP_AUTHORIZATION=f'Bearer {self.superadmin_token}'
            )
            self.assertEqual(res_list.status_code, 200)
            tenants_data = res_list.json()
            self.assertTrue(any(t['schema_name'] == self.tenant.schema_name for t in tenants_data))

            # Non-superadmin forbidden
            res_list_forbid = self.client.get(
                '/api/tenants/',
                HTTP_AUTHORIZATION=f'Bearer {self.owner_token}'
            )
            self.assertEqual(res_list_forbid.status_code, 403)

            # POST /api/tenants/ validation tests:
            # 1. Non-superadmin forbidden
            res_create_forbid = self.client.post(
                '/api/tenants/',
                data=json.dumps({"name": "Shop", "schema_name": "t_shop", "domain": "shop.internal"}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.owner_token}'
            )
            self.assertEqual(res_create_forbid.status_code, 403)

            # 2. Invalid schema identifier (contains hyphens) rejected with 400
            res_create_invalid = self.client.post(
                '/api/tenants/',
                data=json.dumps({"name": "Invalid Shop", "schema_name": "invalid-schema-name!", "domain": "inv.internal"}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.superadmin_token}'
            )
            self.assertEqual(res_create_invalid.status_code, 400)

            # 3. Duplicate schema name rejected with 400
            res_create_dup = self.client.post(
                '/api/tenants/',
                data=json.dumps({"name": "Duplicate Tenant", "schema_name": self.tenant.schema_name, "domain": "demo2.internal"}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.superadmin_token}'
            )
            self.assertEqual(res_create_dup.status_code, 400)

            # GET /api/tenants/status/{schema_name}/
            # 1. Non-existent schema returns 404
            res_status_404 = self.client.get('/api/tenants/status/non_existent_schema_xyz/')
            self.assertEqual(res_status_404.status_code, 404)

            # 2. Existing active schema returns 200
            res_status_200 = self.client.get(f'/api/tenants/status/{self.tenant.schema_name}/')
            self.assertEqual(res_status_200.status_code, 200)
