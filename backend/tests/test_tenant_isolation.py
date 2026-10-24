from decimal import Decimal
from django.test import TestCase, Client as TestClient
from django_tenants.utils import schema_context
from apps.tenants.models import Client, Domain
from apps.accounts.models import User, Branch
from apps.products.models import Category, Purity, Product


class TenantIsolationTestCase(TestCase):
    """
    Validates complete data isolation across multiple tenants using PostgreSQL schemas.
    """

    @classmethod
    def setUpTestData(cls):
        # 1. Setup Public Tenant if not present
        cls.public_client = Client.objects.filter(schema_name='public').first()
        if not cls.public_client:
            cls.public_client = Client(schema_name='public', name='Public Platform')
            cls.public_client.auto_create_schema = False
            cls.public_client.save()
            Domain.objects.create(domain='localhost', tenant=cls.public_client, is_primary=True)

        # 2. Setup Tenant 1 (Swarna Jewels)
        cls.tenant1 = Client.objects.filter(schema_name='tenant_swarna').first()
        if not cls.tenant1:
            cls.tenant1 = Client(schema_name='tenant_swarna', name='Swarna Jewels Pune')
            cls.tenant1.save()
            Domain.objects.create(domain='swarna.localhost', tenant=cls.tenant1, is_primary=True)

        # 3. Setup Tenant 2 (Kalyan Heritage)
        cls.tenant2 = Client.objects.filter(schema_name='tenant_kalyan').first()
        if not cls.tenant2:
            cls.tenant2 = Client(schema_name='tenant_kalyan', name='Kalyan Heritage Mumbai')
            cls.tenant2.save()
            Domain.objects.create(domain='kalyan.localhost', tenant=cls.tenant2, is_primary=True)

    def test_tenant_data_isolation(self):
        """
        Verify that inventory created in Tenant 1 does not leak into Tenant 2.
        """
        # Create inventory item in Tenant 1
        with schema_context(self.tenant1.schema_name):
            cat1 = Category.objects.create(name="Gold Bangles Pune")
            purity1 = Purity.objects.create(name="22KT Pune", fineness=Decimal("0.916"))
            prod1 = Product.objects.create(
                name="Pune Bridal Kada",
                sku="KADA-PUN-001",
                category=cat1,
                purity=purity1,
                gross_weight=Decimal("25.500"),
                making_charge_type="per_gram",
                making_charge_value=Decimal("450.00"),
            )
            self.assertEqual(Product.objects.count(), 1)
            self.assertTrue(Product.objects.filter(sku="KADA-PUN-001").exists())

        # Switch to Tenant 2 — verify Tenant 1 product is completely invisible
        with schema_context(self.tenant2.schema_name):
            # Tenant 2 starts empty
            self.assertFalse(Product.objects.filter(sku="KADA-PUN-001").exists())
            self.assertFalse(Category.objects.filter(name="Gold Bangles Pune").exists())
            self.assertEqual(Product.objects.count(), 0)

            # Create distinct product in Tenant 2
            cat2 = Category.objects.create(name="Diamond Rings Mumbai")
            purity2 = Purity.objects.create(name="18KT Mumbai", fineness=Decimal("0.750"))
            Product.objects.create(
                name="Mumbai Solitaire Ring",
                sku="RING-MUM-001",
                category=cat2,
                purity=purity2,
                gross_weight=Decimal("5.200"),
                making_charge_type="fixed",
                making_charge_value=Decimal("1500.00"),
            )
            self.assertEqual(Product.objects.count(), 1)
            self.assertTrue(Product.objects.filter(sku="RING-MUM-001").exists())

        # Switch back to Tenant 1 — verify Tenant 2 product is invisible here
        with schema_context(self.tenant1.schema_name):
            self.assertEqual(Product.objects.count(), 1)
            self.assertTrue(Product.objects.filter(sku="KADA-PUN-001").exists())
            self.assertFalse(Product.objects.filter(sku="RING-MUM-001").exists())

    def test_tenant_middleware_header_resolution(self):
        """
        Verify tenant routing via 'X-Tenant' HTTP header.
        """
        client = TestClient()
        response = client.get('/api/tenants/', HTTP_X_TENANT='tenant_swarna')
        self.assertEqual(response.status_code, 200)
