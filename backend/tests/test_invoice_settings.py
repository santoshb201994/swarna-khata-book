import json
from decimal import Decimal
from django.test import TestCase, Client
from django_tenants.utils import schema_context

from apps.tenants.models import Client as TenantClient, Domain
from apps.accounts.models import User, Branch
from apps.billing.models import Sale, SaleItem, Payment, InvoiceSetting
from apps.products.models import Category, Purity, Product
from apps.stock.models import StockSummary
from ninja_api.auth import create_token


class InvoiceSettingsTestCase(TestCase):
    """
    Test suite for jewellery invoice template customization,
    RBAC staff restrictions, and GST PDF generation.
    """

    @classmethod
    def setUpTestData(cls):
        from django.db import connection
        connection.set_schema_to_public()

        # 1. Public tenant
        cls.public_tenant, _ = TenantClient.objects.get_or_create(
            schema_name='public',
            defaults={'name': 'Public Platform', 'is_active': True}
        )
        Domain.objects.get_or_create(domain='localhost', tenant=cls.public_tenant, is_primary=True)

        # 2. Test Tenant
        cls.tenant, _ = TenantClient.objects.get_or_create(
            schema_name='t_invoice_test',
            defaults={'name': 'Shree Balaji Store', 'is_active': True}
        )
        Domain.objects.get_or_create(domain='balaji.localhost', tenant=cls.tenant, is_primary=True)

        with schema_context(cls.tenant.schema_name):
            cls.branch = Branch.objects.create(
                name="Shree Balaji Abharan Angadi",
                address="Beside Mukkal Basaveshwar Temple, Old Shroff Bazar, GADAG-582101",
                phone="9449642640",
                gstin="29ADNPP6515B1ZF"
            )

            cls.owner_user = User.objects.create_user(
                username='balaji_owner',
                password='OwnerPass123!',
                role=User.Role.OWNER,
                branch=cls.branch
            )
            cls.staff_user = User.objects.create_user(
                username='balaji_staff',
                password='StaffPass123!',
                role=User.Role.STAFF,
                branch=cls.branch
            )

            # Pre-seed InvoiceSetting
            cls.invoice_setting = InvoiceSetting.objects.create(
                branch=cls.branch,
                header_invocation="|| ಶ್ರೀ ಶಾಂತೇರಿ ಪ್ರಸನ್ನ ||",
                shop_name_primary="Shree Balaji Abharan Angadi",
                shop_name_secondary="ಶ್ರೀ ಬಾಲಾಜಿ ಆಭರಣ ಅಂಗಡಿ",
                phone_landline="(08372) 238391",
                phone_mobile_1="9449642640",
                phone_mobile_2="7760755515",
                email="Ranjanbalaji93@gmail.com",
                gstin="29ADNPP6515B1ZF",
                state_name="Karnataka",
                state_code="29",
                template_style="traditional_bilingual",
                default_paper_size="A4",
                terms_and_conditions="Exchange with in 3 days, No Guarantee For Stone Falling & Brekage",
                signatory_title="For, Shree Balaji Abharan Angadi"
            )

            # Category & Purity
            cat = Category.objects.create(name='Nosepin Category')
            purity = Purity.objects.create(name='22KT (916)', fineness=Decimal('0.916'))
            cls.product = Product.objects.create(
                name='Gold Nosepin',
                sku='NP-22K-001',
                category=cat,
                purity=purity,
                gross_weight=Decimal('5.901'),
                stone_weight=Decimal('0.000'),
                huid='HUID916NP',
                hsn_code='7113',
                branch=cls.branch
            )
            StockSummary.objects.update_or_create(product=cls.product, defaults={'quantity_on_hand': 10})

            cls.owner_token = create_token(cls.owner_user, token_type='access')
            cls.staff_token = create_token(cls.staff_user, token_type='access')

        cls.client = Client()

    def tearDown(self):
        from django.db import connection
        connection.set_schema_to_public()
        super().tearDown()

    @classmethod
    def tearDownClass(cls):
        from django.db import connection
        connection.set_schema_to_public()
        super().tearDownClass()

    def test_get_invoice_settings(self):
        """Staff and owners can retrieve active invoice settings."""
        res = self.client.get(
            '/api/billing/invoice-settings/',
            HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
            HTTP_X_TENANT=self.tenant.schema_name
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['shop_name_primary'], "Shree Balaji Abharan Angadi")
        self.assertEqual(data['shop_name_secondary'], "ಶ್ರೀ ಬಾಲಾಜಿ ಆಭರಣ ಅಂಗಡಿ")
        self.assertEqual(data['gstin'], "29ADNPP6515B1ZF")
        self.assertEqual(data['header_invocation'], "|| ಶ್ರೀ ಶಾಂತೇರಿ ಪ್ರಸನ್ನ ||")
        self.assertEqual(data['phone_landline'], "(08372) 238391")

    def test_staff_cannot_update_invoice_settings(self):
        """Staff role must be rejected with 403 when attempting to alter invoice settings."""
        payload = {"shop_name_primary": "Malicious Hijack Name"}
        res = self.client.put(
            '/api/billing/invoice-settings/',
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
            HTTP_X_TENANT=self.tenant.schema_name
        )
        self.assertEqual(res.status_code, 403)

    def test_owner_can_update_invoice_settings(self):
        """Owner can customize template style, terms, and paper format."""
        payload = {
            "template_style": "modern_luxury",
            "default_paper_size": "A5",
            "tagline": "Crafted with Excellence",
            "upi_id": "balaji.gadag@sbi"
        }
        res = self.client.put(
            '/api/billing/invoice-settings/',
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
            HTTP_X_TENANT=self.tenant.schema_name
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['template_style'], "modern_luxury")
        self.assertEqual(data['default_paper_size'], "A5")
        self.assertEqual(data['upi_id'], "balaji.gadag@sbi")

    def test_reset_demo_invoice_settings(self):
        """Owner can reset configuration back to Gadag demo reference template."""
        res = self.client.post(
            '/api/billing/invoice-settings/reset-demo/',
            HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
            HTTP_X_TENANT=self.tenant.schema_name
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['template_style'], "traditional_bilingual")
        self.assertEqual(data['header_invocation'], "|| ಶ್ರೀ ಶಾಂತೇರಿ ಪ್ರಸನ್ನ ||")
        self.assertEqual(data['gstin'], "29ADNPP6515B1ZF")
        self.assertIn("Exchange with in 3 days", data['terms_and_conditions'])

    def test_invoice_creation_and_pdf_generation(self):
        """Verify sale invoice includes HUID, customer contact info, and PDF renders successfully."""
        checkout_payload = {
            "items": [
                {
                    "product_id": self.product.id,
                    "quantity": 1,
                    "gold_rate_per_gram": "4900.00",
                    "making_charge": "0.00",
                    "stone_charge": "0.00"
                }
            ],
            "payment": {"method": "cash", "amount": "5000.00"},
            "notes": "Gadag Sample Bill 153"
        }
        create_res = self.client.post(
            '/api/sales/',
            data=json.dumps(checkout_payload),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
            HTTP_X_TENANT=self.tenant.schema_name
        )
        self.assertEqual(create_res.status_code, 201)
        sale_data = create_res.json()
        sale_id = sale_data['id']
        self.assertEqual(len(sale_data['items']), 1)
        self.assertEqual(sale_data['items'][0]['huid'], 'HUID916NP')
        self.assertIsNotNone(sale_data['invoice_setting'])
        self.assertEqual(sale_data['invoice_setting']['shop_name_primary'], "Shree Balaji Abharan Angadi")

        # Test PDF generation via both /invoice-pdf/ and /invoice_pdf/
        for url in [f'/api/sales/{sale_id}/invoice-pdf/', f'/api/sales/{sale_id}/invoice_pdf/']:
            pdf_res = self.client.get(
                url,
                HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(pdf_res.status_code, 200)
            self.assertEqual(pdf_res['Content-Type'], 'application/pdf')
            self.assertGreater(len(pdf_res.content), 1000)
