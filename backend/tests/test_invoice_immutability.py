import json
import hashlib
from decimal import Decimal
from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django_tenants.utils import schema_context

from apps.tenants.models import Client as TenantClient, Domain
from apps.accounts.models import User, Branch
from apps.accounting.models import Customer
from apps.billing.models import Sale, InvoiceSetting
from apps.billing.services import create_sale, generate_invoice_pdf
from apps.products.models import Category, Purity, Product
from apps.stock.models import StockSummary
from ninja_api.auth import create_token


class InvoiceSnapshotImmutabilityTestCase(TestCase):
    """
    Test suite for PostgreSQL snapshot immutability, ensuring historical
    sales invoices and tax details cannot be mutated by future shop profile
    or customer profile modifications.
    """

    @classmethod
    def setUpTestData(cls):
        from django.db import connection
        connection.set_schema_to_public()

        cls.public_tenant, _ = TenantClient.objects.get_or_create(
            schema_name='public',
            defaults={'name': 'Public Platform', 'is_active': True}
        )
        Domain.objects.get_or_create(domain='localhost', tenant=cls.public_tenant, is_primary=True)

        cls.tenant, _ = TenantClient.objects.get_or_create(
            schema_name='t_immutability_test',
            defaults={'name': 'Kalyan Heritage Jewellers', 'is_active': True}
        )
        Domain.objects.get_or_create(domain='kalyan.localhost', tenant=cls.tenant, is_primary=True)

        with schema_context(cls.tenant.schema_name):
            cls.branch = Branch.objects.create(
                name="Kalyan Heritage Flagship",
                address="MG Road, Bangalore, Karnataka - 560001",
                phone="0802223344",
                gstin="29AAAAA0000A1Z5"
            )

            cls.owner_user = User.objects.create_user(
                username='kalyan_proprietor',
                password='OwnerPassword@123',
                role=User.Role.OWNER,
                branch=cls.branch
            )

            cls.inv_setting = InvoiceSetting.objects.create(
                branch=cls.branch,
                shop_name_primary="Kalyan Heritage Jewellers",
                shop_name_secondary="ಕಲ್ಯಾಣ್ ಹೆರಿಟೇಜ್ ಜ್ಯುವೆಲ್ಲರ್ಸ್",
                address_primary="MG Road, Bangalore, Karnataka - 560001",
                gstin="29AAAAA0000A1Z5",
                pan_number="AAAAA0000A",
                phone_landline="0802223344",
                terms_and_conditions="Original terms: 7 days exchange with original bill.",
                signatory_title="For, Kalyan Heritage Jewellers"
            )

            cls.cat = Category.objects.create(name='Gold Chains')
            cls.purity = Purity.objects.create(name='22KT 916', fineness=Decimal('0.916'))
            cls.product = Product.objects.create(
                name='Traditional Gold Chain',
                sku='CHAIN-916-01',
                category=cls.cat,
                purity=cls.purity,
                gross_weight=Decimal('10.000'),
                stone_weight=Decimal('0.000'),
                making_charge_type='per_gram',
                making_charge_value=Decimal('450.00'),
                branch=cls.branch,
                is_active=True
            )

            StockSummary.objects.create(
                product=cls.product,
                quantity_on_hand=50
            )

            cls.customer = Customer.objects.create(
                name="Ramesh Hegde",
                phone="9845012345",
                address="Jayanagar 4th Block, Bangalore",
                pan_number="ABCDE1234F",
                aadhar_last4="5678"
            )

            cls.owner_token = create_token(cls.owner_user, token_type='access')

        cls.client = Client()

    @classmethod
    def tearDownClass(cls):
        from django.db import connection
        connection.set_schema_to_public()
        super().tearDownClass()

    def test_sale_captures_immutable_snapshots(self):
        """Sale creation must capture frozen shop and customer snapshots in PostgreSQL JSONB."""
        with schema_context(self.tenant.schema_name):
            items_data = [{
                'product': self.product,
                'quantity': 1,
                'gold_rate_per_gram': Decimal('7200.00'),
                'making_charge': Decimal('4500.00'),
                'stone_charge': Decimal('0.00'),
            }]
            payment_data = {'method': 'cash', 'amount': '76500.00'}

            sale = create_sale(
                user=self.owner_user,
                items_data=items_data,
                payment_data=payment_data,
                customer=self.customer,
                notes="First sale with immutable snapshot"
            )

            # Assert snapshots exist and match
            self.assertIsNotNone(sale.shop_snapshot)
            self.assertEqual(sale.shop_snapshot['shop_name_primary'], "Kalyan Heritage Jewellers")
            self.assertEqual(sale.shop_snapshot['gstin'], "29AAAAA0000A1Z5")
            self.assertIn("Original terms", sale.shop_snapshot['terms_and_conditions'])

            self.assertIsNotNone(sale.customer_snapshot)
            self.assertEqual(sale.customer_snapshot['name'], "Ramesh Hegde")
            self.assertEqual(sale.customer_snapshot['phone'], "9845012345")
            self.assertEqual(sale.customer_snapshot['pan_number'], "ABCDE1234F")

            # Assert cryptographic PDF fingerprint
            self.assertTrue(len(sale.pdf_sha256) == 64)

    def test_future_shop_profile_modification_does_not_mutate_historical_invoice(self):
        """
        Altering store branding/GSTIN in InvoiceSetting months later must NOT
        alter the historical invoice or its rendered PDF.
        """
        with schema_context(self.tenant.schema_name):
            items_data = [{
                'product': self.product,
                'quantity': 1,
                'gold_rate_per_gram': Decimal('7200.00'),
                'making_charge': Decimal('4500.00'),
                'stone_charge': Decimal('0.00'),
            }]
            payment_data = {'method': 'cash', 'amount': '76500.00'}

            sale = create_sale(
                user=self.owner_user,
                items_data=items_data,
                payment_data=payment_data,
                customer=self.customer
            )

            # Initial PDF generation
            pdf_bytes_before = generate_invoice_pdf(sale)
            self.assertEqual(hashlib.sha256(pdf_bytes_before).hexdigest(), sale.pdf_sha256)

            # Store owner updates shop profile 6 months later
            self.inv_setting.shop_name_primary = "COMPLETELY DIFFERENT NEW STORE NAME"
            self.inv_setting.gstin = "99TAMPEREDGSTIN99"
            self.inv_setting.terms_and_conditions = "New modified terms."
            self.inv_setting.save()

            # Re-generate PDF for historical sale
            pdf_bytes_after = generate_invoice_pdf(sale)

            # Historical PDF must be 100% byte-for-byte identical, retaining frozen snapshot
            self.assertEqual(pdf_bytes_before, pdf_bytes_after)
            self.assertEqual(sale.shop_snapshot['shop_name_primary'], "Kalyan Heritage Jewellers")
            self.assertEqual(sale.shop_snapshot['gstin'], "29AAAAA0000A1Z5")

    def test_future_customer_profile_modification_does_not_mutate_historical_invoice(self):
        """
        Altering customer details in Customer table must NOT alter past invoices.
        """
        with schema_context(self.tenant.schema_name):
            items_data = [{
                'product': self.product,
                'quantity': 1,
                'gold_rate_per_gram': Decimal('7200.00'),
                'making_charge': Decimal('4500.00'),
                'stone_charge': Decimal('0.00'),
            }]
            payment_data = {'method': 'cash', 'amount': '76500.00'}

            sale = create_sale(
                user=self.owner_user,
                items_data=items_data,
                payment_data=payment_data,
                customer=self.customer
            )

            # Customer updates their name and PAN in the master customer khata
            self.customer.name = "Suresh Hegde Altered"
            self.customer.pan_number = "ALTRDPAN99"
            self.customer.save()

            # API formatting check
            res = self.client.get(
                f'/api/sales/{sale.id}/',
                HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data['customer_name'], "Ramesh Hegde")
            self.assertEqual(data['customer_pan'], "ABCDE1234F")

    def test_snapshot_immutability_validation_prevents_tampering(self):
        """Sale.clean() must reject any attempt to modify frozen snapshots."""
        with schema_context(self.tenant.schema_name):
            items_data = [{
                'product': self.product,
                'quantity': 1,
                'gold_rate_per_gram': Decimal('7200.00'),
                'making_charge': Decimal('4500.00'),
            }]
            sale = create_sale(
                user=self.owner_user,
                items_data=items_data,
                payment_data={'method': 'cash', 'amount': '76500.00'},
                customer=self.customer
            )

            # Attempt to tamper with shop_snapshot
            tampered_snapshot = dict(sale.shop_snapshot)
            tampered_snapshot['gstin'] = 'MALICIOUS_GSTIN'
            sale.shop_snapshot = tampered_snapshot

            with self.assertRaises(ValidationError) as ctx:
                sale.clean()

            self.assertIn("shop_snapshot is immutable", str(ctx.exception))
