import json
import uuid
from decimal import Decimal
from django.test import TestCase, Client as TestClient
from django_tenants.utils import schema_context
from apps.tenants.models import Client, Domain
from apps.accounts.models import User, Branch
from apps.accounting.models import Customer
from apps.products.models import Category, Purity, Product
from apps.billing.models import Sale, SaleItem, Payment, InvoiceSetting, Item
from ninja_api.auth import create_token


class EndpointsBillingPosAndExportTestCase(TestCase):
    """
    Integration tests covering Billing, POS Pairing, and Data Export endpoints:
    - GET /api/sales/{id}/invoice-pdf/ & /api/sales/{id}/invoice_pdf/
    - POST /api/sales/{id}/add-payment/
    - POST /api/billing/invoice-settings/reset-demo/
    - POST /api/pos-pairing/start/
    - POST /api/pos-pairing/redeem/
    - POST /api/pos-pairing/scan-fallback/
    - POST /api/pos-pairing/revoke/
    - GET /api/export/shop/
    - GET /api/export/all-shops/
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
                username="bill_superadmin",
                password="Super*Vault99",
                email="superadmin@swarnakhata.internal"
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
                username="bill_owner",
                password="Owner*Vault9",
                role=User.Role.OWNER,
                branch=cls.branch
            )
            cls.staff = User.objects.create_user(
                username="bill_staff",
                password="Worker*Vault8",
                role=User.Role.STAFF,
                branch=cls.branch
            )
            cls.customer = Customer.objects.create(
                name="Ramesh Patil",
                phone="9876543210",
                address="Station Road, Gadag"
            )
            cls.category = Category.objects.create(name="Gold Coins", description="Bullion")
            cls.purity = Purity.objects.create(name="24K", fineness=Decimal('0.999'))
            cls.product = Product.objects.create(
                name="Lakshmi Gold Coin 10g",
                sku="COIN-LAKSHMI-10G",
                category=cls.category,
                purity=cls.purity,
                gross_weight=Decimal('10.000'),
                stone_weight=Decimal('0.000'),
                other_weight=Decimal('0.000'),
                branch=cls.branch,
                is_active=True
            )
            cls.item = Item.objects.create(
                product=cls.product,
                qr_code=cls.product.sku,
                name=cls.product.name,
                weight=cls.product.gross_weight,
                status=Item.Status.AVAILABLE
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
    # Invoice PDF Generation & Add Payment
    # -------------------------------------------------------------------------
    def test_invoice_pdf_download_and_add_payment(self):
        with schema_context(self.tenant.schema_name):
            # Create a completed sale
            sale = Sale.objects.create(
                customer=self.customer,
                branch=self.branch,
                invoice_number="INV-2026-9001",
                gold_rate_per_gram=Decimal('7000.00'),
                subtotal=Decimal('70000.00'),
                discount=Decimal('0.00'),
                cgst_amount=Decimal('1050.00'),
                sgst_amount=Decimal('1050.00'),
                igst_amount=Decimal('0.00'),
                total_amount=Decimal('72100.00'),
                amount_paid=Decimal('40000.00'),
                balance_due=Decimal('32100.00'),
                payment_status=Sale.PaymentStatus.PARTIAL,
                created_by=self.owner
            )
            SaleItem.objects.create(
                sale=sale,
                product=self.product,
                product_name=self.product.name,
                sku=self.product.sku,
                purity="24K",
                quantity=1,
                gross_weight=Decimal('10.000'),
                net_weight=Decimal('10.000'),
                gold_rate_per_gram=Decimal('7000.00'),
                making_charge=Decimal('0.00'),
                stone_charge=Decimal('0.00'),
                unit_price=Decimal('70000.00'),
                total_price=Decimal('70000.00'),
                hsn_code="7113",
                gst_rate=Decimal('3.00')
            )
            Payment.objects.create(
                sale=sale,
                method='cash',
                amount=Decimal('40000.00'),
                reference='INITIAL'
            )

            # Test GET /api/sales/{id}/invoice-pdf/
            res_pdf = self.client.get(
                f'/api/sales/{sale.id}/invoice-pdf/',
                HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_pdf.status_code, 200)
            self.assertEqual(res_pdf['Content-Type'], 'application/pdf')
            self.assertTrue(res_pdf.content.startswith(b'%PDF-'))

            # Test GET /api/sales/{id}/invoice_pdf/ (underscore alias)
            res_pdf2 = self.client.get(
                f'/api/sales/{sale.id}/invoice_pdf/',
                HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_pdf2.status_code, 200)
            self.assertEqual(res_pdf2['Content-Type'], 'application/pdf')

            # Test POST /api/sales/{id}/add-payment/
            res_pay = self.client.post(
                f'/api/sales/{sale.id}/add-payment/',
                data=json.dumps({
                    "method": "upi",
                    "amount": "32100.00",
                    "reference": "UPI/987654321/AXIS",
                    "note": "Balance settled via PhonePe"
                }),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_pay.status_code, 200)
            data = res_pay.json()
            self.assertEqual(Decimal(str(data['amount_paid'])), Decimal('72100.00'))
            self.assertEqual(Decimal(str(data['balance_due'])), Decimal('0.00'))
            self.assertEqual(data['payment_status'], 'paid')

            # Re-fetch sale from db to verify persistence
            with schema_context(self.tenant.schema_name):
                sale = Sale.objects.get(id=sale.id)
                self.assertEqual(sale.payment_status, Sale.PaymentStatus.PAID)
                self.assertEqual(sale.payments.count(), 2)

    # -------------------------------------------------------------------------
    # Invoice Settings Reset Demo
    # -------------------------------------------------------------------------
    def test_invoice_settings_reset_demo(self):
        with schema_context(self.tenant.schema_name):
            res = self.client.post(
                '/api/billing/invoice-settings/reset-demo/',
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data['shop_name_primary'], "Shree Balaji Abharan Angadi")
            self.assertEqual(data['gstin'], "29ADNPP6515B1ZF")
            self.assertEqual(data['bank_name'], "State Bank of India")

            # Staff role cannot reset invoice settings
            res_forbid = self.client.post(
                '/api/billing/invoice-settings/reset-demo/',
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_forbid.status_code, 403)

    # -------------------------------------------------------------------------
    # POS Mobile Pairing Lifecycle
    # -------------------------------------------------------------------------
    def test_pos_pairing_lifecycle(self):
        with schema_context(self.tenant.schema_name):
            # 1. Laptop initiates pairing
            res_start = self.client.post(
                '/api/pos-pairing/start/',
                data=json.dumps({"base_url": "https://demo.swarnakhata.internal"}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_start.status_code, 201)
            pairing_info = res_start.json()
            session_id = pairing_info['session_id']
            pairing_code = pairing_info['pairing_code']

            # 2. Smartphone redeems pairing code (no user JWT required; uses pairing code)
            res_redeem = self.client.post(
                '/api/pos-pairing/redeem/',
                data=json.dumps({
                    "session_id": session_id,
                    "pairing_code": pairing_code,
                    "device_info": "Samsung Galaxy S23 Ultra - Chrome Mobile",
                    "tenant_schema": self.tenant.schema_name
                }),
                content_type='application/json'
            )
            self.assertEqual(res_redeem.status_code, 200)
            redeem_data = res_redeem.json()
            mobile_token = redeem_data['mobile_token']
            self.assertTrue(bool(mobile_token))

            # 3. Mobile submits scanned QR via scan-fallback endpoint
            event_id = str(uuid.uuid4())
            res_scan = self.client.post(
                '/api/pos-pairing/scan-fallback/',
                data=json.dumps({
                    "event_id": event_id,
                    "qr_payload": f"SKB:{self.item.qr_token}"
                }),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {mobile_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_scan.status_code, 200)

            # 4. Laptop revokes pairing
            res_revoke = self.client.post(
                '/api/pos-pairing/revoke/',
                data=json.dumps({"session_id": session_id}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_revoke.status_code, 200)
            self.assertEqual(res_revoke.json()['status'], 'revoked')

    # -------------------------------------------------------------------------
    # Data Export Vault (Statutory Backup ZIPs)
    # -------------------------------------------------------------------------
    def test_export_shop_and_all_shops(self):
        with schema_context(self.tenant.schema_name):
            # 1. Shop owner exports shop vault
            res_shop = self.client.get(
                '/api/export/shop/?start_date=2026-01-01&end_date=2026-12-31',
                HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_shop.status_code, 200)
            self.assertEqual(res_shop['Content-Type'], 'application/zip')

            # Staff is forbidden from statutory data export
            res_shop_forbid = self.client.get(
                '/api/export/shop/',
                HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res_shop_forbid.status_code, 403)

        # 2. Platform superadmin exports all shops
        with schema_context('public'):
            res_all = self.client.get(
                '/api/export/all-shops/?start_date=2026-01-01&end_date=2026-12-31',
                HTTP_AUTHORIZATION=f'Bearer {self.superadmin_token}'
            )
            self.assertEqual(res_all.status_code, 200)
            self.assertEqual(res_all['Content-Type'], 'application/zip')
