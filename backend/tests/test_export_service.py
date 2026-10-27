import io
import json
import zipfile
from decimal import Decimal
from django.test import TestCase, Client
from django_tenants.utils import schema_context

from apps.tenants.models import Client as TenantClient, Domain
from apps.accounts.models import User, Branch
from apps.products.models import Category, Purity, Product
from apps.stock.models import StockSummary
from apps.accounting.models import Customer
from apps.billing.models import Sale, InvoiceSetting
from apps.billing.services import create_sale
from ninja_api.auth import create_token


class DataExportTestCase(TestCase):
    """
    Test suite for Data Export Vault:
    - Owner can export their store's data as a compressed ZIP.
    - Developer can export all shops globally.
    - Staff/Manager roles are forbidden (403).
    - Archive contains sanitized CSVs and manifest.
    """

    @classmethod
    def setUpTestData(cls):
        from django.db import connection
        connection.set_schema_to_public()

        # Public superadmin
        cls.public_tenant, _ = TenantClient.objects.get_or_create(
            schema_name='public',
            defaults={'name': 'Public Platform', 'is_active': True}
        )
        Domain.objects.get_or_create(domain='localhost', tenant=cls.public_tenant, is_primary=True)

        with schema_context('public'):
            cls.superadmin = User.objects.create_superuser(
                username='dev_export_admin',
                password='SuperPassword@123',
                email='superadmin@swarnakhata.internal',
                role='superadmin'
            )
            cls.superadmin_token = create_token(cls.superadmin, token_type='access')

        # Test Tenant A
        cls.tenant_a, _ = TenantClient.objects.get_or_create(
            schema_name='t_export_a',
            defaults={'name': 'Store Alpha Jewellers', 'is_active': True}
        )
        Domain.objects.get_or_create(domain='alpha.localhost', tenant=cls.tenant_a, is_primary=True)

        with schema_context(cls.tenant_a.schema_name):
            cls.branch_a = Branch.objects.create(
                name="Store Alpha Flagship",
                address="MG Road, Bangalore",
                phone="0801111222",
                gstin="29AAAAA1111A1Z1"
            )
            cls.owner_a = User.objects.create_user(
                username='owner_alpha',
                password='OwnerPassword@123',
                role=User.Role.OWNER,
                branch=cls.branch_a
            )
            cls.manager_a = User.objects.create_user(
                username='manager_alpha',
                password='ManagerPassword@123',
                role=User.Role.MANAGER,
                branch=cls.branch_a
            )
            cls.staff_a = User.objects.create_user(
                username='staff_alpha',
                password='StaffPassword@123',
                role=User.Role.STAFF,
                branch=cls.branch_a
            )

            cls.cat = Category.objects.create(name='Bangles')
            cls.purity = Purity.objects.create(name='22KT 916', fineness=Decimal('0.916'))
            cls.product = Product.objects.create(
                name='Gold Bangle 22KT',
                sku='BANGLE-01',
                category=cls.cat,
                purity=cls.purity,
                gross_weight=Decimal('15.000'),
                stone_weight=Decimal('0.000'),
                making_charge_type='per_gram',
                making_charge_value=Decimal('400.00'),
                branch=cls.branch_a,
                is_active=True
            )
            StockSummary.objects.create(product=cls.product, quantity_on_hand=20)

            cls.customer = Customer.objects.create(
                name="Anand Kumar",
                phone="9876543210",
                pan_number="ABCDE1234F"
            )

            # Create a sale in Store Alpha
            cls.sale = create_sale(
                user=cls.owner_a,
                items_data=[{
                    'product': cls.product,
                    'quantity': 1,
                    'gold_rate_per_gram': Decimal('7000.00'),
                    'making_charge': Decimal('6000.00'),
                }],
                payment_data={'method': 'cash', 'amount': '111000.00'},
                customer=cls.customer,
                notes="Alpha Sale Export Test"
            )

            cls.owner_a_token = create_token(cls.owner_a, token_type='access')
            cls.manager_a_token = create_token(cls.manager_a, token_type='access')
            cls.staff_a_token = create_token(cls.staff_a, token_type='access')

        cls.client = Client()

    @classmethod
    def tearDownClass(cls):
        from django.db import connection
        connection.set_schema_to_public()
        super().tearDownClass()

    def test_owner_can_export_shop_data(self):
        """Store owner receives streaming ZIP containing all shop CSVs."""
        res = self.client.get(
            '/api/export/shop/',
            HTTP_AUTHORIZATION=f'Bearer {self.owner_a_token}',
            HTTP_X_TENANT=self.tenant_a.schema_name
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], 'application/zip')
        self.assertIn('attachment;', res['Content-Disposition'])

        # Verify ZIP contents
        zip_content = b"".join(res.streaming_content)
        with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
            file_list = z.namelist()
            self.assertIn('sales_invoices.csv', file_list)
            self.assertIn('sale_items.csv', file_list)
            self.assertIn('inventory_products.csv', file_list)
            self.assertIn('customers.csv', file_list)
            self.assertIn('export_manifest.json', file_list)

            # Read and verify manifest
            manifest_bytes = z.read('export_manifest.json')
            manifest = json.loads(manifest_bytes.decode('utf-8'))
            self.assertEqual(manifest['schema_name'], self.tenant_a.schema_name)
            self.assertGreaterEqual(manifest['record_counts']['sales_invoices'], 1)

    def test_owner_export_with_date_range(self):
        """Owner can filter export by valid date range."""
        res = self.client.get(
            '/api/export/shop/?start_date=2026-01-01&end_date=2026-12-31',
            HTTP_AUTHORIZATION=f'Bearer {self.owner_a_token}',
            HTTP_X_TENANT=self.tenant_a.schema_name
        )
        self.assertEqual(res.status_code, 200)
        zip_content = b"".join(res.streaming_content)
        self.assertGreater(len(zip_content), 500)

    def test_staff_and_manager_cannot_export_shop_data(self):
        """Subordinate roles (manager, staff) are strictly forbidden (403)."""
        # Manager attempt
        res_mgr = self.client.get(
            '/api/export/shop/',
            HTTP_AUTHORIZATION=f'Bearer {self.manager_a_token}',
            HTTP_X_TENANT=self.tenant_a.schema_name
        )
        self.assertEqual(res_mgr.status_code, 403)

        # Staff attempt
        res_staff = self.client.get(
            '/api/export/shop/',
            HTTP_AUTHORIZATION=f'Bearer {self.staff_a_token}',
            HTTP_X_TENANT=self.tenant_a.schema_name
        )
        self.assertEqual(res_staff.status_code, 403)

    def test_developer_can_export_all_shops(self):
        """Superadmin can export multi-store global archive containing all tenants."""
        res = self.client.get(
            '/api/export/all-shops/',
            HTTP_AUTHORIZATION=f'Bearer {self.superadmin_token}',
            HTTP_X_TENANT='public'
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], 'application/zip')

        zip_content = b"".join(res.streaming_content)
        with zipfile.ZipFile(io.BytesIO(zip_content)) as z:
            file_list = z.namelist()
            self.assertIn('global_export_summary.json', file_list)
            # Must have tenant A subdirectory
            self.assertTrue(any(f.startswith(f"{self.tenant_a.schema_name}/") for f in file_list))

    def test_owner_cannot_export_all_shops(self):
        """Store owner calling global all-shops export is rejected with 403."""
        res = self.client.get(
            '/api/export/all-shops/',
            HTTP_AUTHORIZATION=f'Bearer {self.owner_a_token}',
            HTTP_X_TENANT=self.tenant_a.schema_name
        )
        self.assertEqual(res.status_code, 403)
