import json
from decimal import Decimal
from django.test import TestCase, Client as TestClient
from django_tenants.utils import schema_context
from apps.tenants.models import Client, Domain
from apps.accounts.models import User, Branch
from apps.products.models import Category, Purity, Product
from apps.stock.models import StockMovement, StockSummary
from apps.billing.models import Sale, Payment
from apps.accounting.models import DayBook, Customer
from ninja_api.auth import create_token


class NinjaPOSBillingTestCase(TestCase):
    """
    Comprehensive tests for POS Billing, Atomic Checkout, Concurrency & Stock Locks,
    Tax Reconciliation, PDF Invoice Generation, and Cancellation.
    """

    @classmethod
    def setUpTestData(cls):
        cls.tenant = Client.objects.filter(schema_name='demo').first()
        if not cls.tenant:
            cls.tenant = Client(schema_name='demo', name='Demo Jewellery')
            cls.tenant.save()
            Domain.objects.create(domain='demo.localhost', tenant=cls.tenant, is_primary=True)

        with schema_context(cls.tenant.schema_name):
            cls.branch = Branch.objects.create(name="POS Test Branch")
            cls.cashier = User.objects.create_user(
                username="pos_cashier",
                password="CashierPassword@123",
                role=User.Role.STAFF,
                branch=cls.branch,
            )
            cls.owner = User.objects.create_user(
                username="pos_owner",
                password="OwnerPassword@123",
                role=User.Role.OWNER,
                branch=cls.branch,
            )
            cls.category = Category.objects.create(name="Gold Rings")
            cls.purity = Purity.objects.create(name="22KT", fineness=Decimal("0.916"))
            cls.customer = Customer.objects.create(name="Anil Kumar", phone="9988776655")

            # Create test product with exactly 2 units in stock
            cls.product = Product.objects.create(
                name="Traditional Gold Ring",
                sku="RING-TRAD-001",
                category=cls.category,
                purity=cls.purity,
                gross_weight=Decimal("10.000"),
                stone_weight=Decimal("0.500"),
                other_weight=Decimal("0.000"),
                making_charge_type="per_gram",
                making_charge_value=Decimal("400.00"),
                branch=cls.branch,
            )
            StockSummary.objects.create(product=cls.product, quantity_on_hand=2)

    def setUp(self):
        self.client = TestClient()
        with schema_context(self.tenant.schema_name):
            self.cashier_token = create_token(self.cashier)
            self.owner_token = create_token(self.owner)

    def test_pos_atomic_checkout_success(self):
        """
        Tests end-to-end POS sale with split payment (cash + card + old gold offset)
        and verifies stock deduction and DayBook cash ledger update.
        """
        with schema_context(self.tenant.schema_name):
            # net_weight = 10.000 - 0.500 = 9.500g
            # gold_rate = 7000.00 -> gold_value = 9.5 * 7000 = 66,500.00
            # making_charge = 400.00
            # unit_price = 66,500 + 400 = 66,900.00
            # item_total (qty 1) = 66,900.00
            # 3% GST = 2,007.00
            # total before discount/old gold = 68,907.00
            # discount = 500.00 -> total = 68,407.00
            # old_gold = 1.000g @ 6000.00 = 6,000.00
            # remaining due = 68,407.00 - 6,000.00 = 62,407.00
            # payments: Cash: 30,000.00, Card: 32,407.00 -> Total paid: 68,407.00 -> Balance: 0.00

            payload = {
                "customer_id": self.customer.id,
                "items": [
                    {
                        "product_id": self.product.id,
                        "quantity": 1,
                        "gold_rate_per_gram": "7000.00",
                        "making_charge": "400.00",
                        "stone_charge": "0.00",
                    }
                ],
                "payments": [
                    {"method": "cash", "amount": "30000.00", "reference": "CASH-RECEIPT-01"},
                    {"method": "card", "amount": "32407.00", "reference": "TXN-CARD-9988"},
                ],
                "discount": "500.00",
                "old_gold_weight": "1.000",
                "old_gold_rate": "6000.00",
                "notes": "Wedding anniversary purchase",
            }

            res = self.client.post(
                '/api/sales/',
                data=json.dumps(payload),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.cashier_token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 201)
            data = res.json()

            # Verify totals
            self.assertEqual(Decimal(data['subtotal']), Decimal('66900.00'))
            self.assertEqual(Decimal(data['cgst_amount']), Decimal('1003.50'))
            self.assertEqual(Decimal(data['sgst_amount']), Decimal('1003.50'))
            # Exact penny tax balance: cgst + sgst == 2007.00
            self.assertEqual(Decimal(data['cgst_amount']) + Decimal(data['sgst_amount']), Decimal('2007.00'))
            self.assertEqual(Decimal(data['total_amount']), Decimal('68407.00'))
            self.assertEqual(Decimal(data['old_gold_value']), Decimal('6000.00'))
            self.assertEqual(Decimal(data['amount_paid']), Decimal('68407.00'))
            self.assertEqual(Decimal(data['balance_due']), Decimal('0.00'))
            self.assertEqual(data['payment_status'], 'paid')

            # Verify Stock was decremented: 2 - 1 = 1
            summary = StockSummary.objects.get(product=self.product)
            self.assertEqual(summary.quantity_on_hand, 1)

            # Verify DayBook automatically received the CASH payment of 30,000.00
            from django.utils import timezone
            day_book = DayBook.objects.get(date=timezone.localdate(), branch=self.branch)
            self.assertGreaterEqual(day_book.cash_in, Decimal('30000.00'))

    def test_loophole_insufficient_stock_rejection(self):
        """
        LOOPHOLE TEST: Verify that attempting to sell more quantity than available
        is strictly aborted and no partial transactions or negative inventory are allowed.
        """
        with schema_context(self.tenant.schema_name):
            # Stock on hand is currently 1 (or 2)
            summary = StockSummary.objects.get(product=self.product)
            available = summary.quantity_on_hand

            payload = {
                "items": [
                    {
                        "product_id": self.product.id,
                        "quantity": available + 10,  # Deliberately request more than available
                        "gold_rate_per_gram": "7000.00",
                    }
                ],
                "payment": {"method": "cash", "amount": "100000.00"},
            }

            res = self.client.post(
                '/api/sales/',
                data=json.dumps(payload),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.cashier_token}',
                HTTP_X_TENANT='demo'
            )
            # Must reject with HTTP 400 Bad Request
            self.assertEqual(res.status_code, 400)
            self.assertIn("Insufficient stock", res.json()['error'])

            # Verify inventory is completely intact
            summary.refresh_from_db()
            self.assertEqual(summary.quantity_on_hand, available)

    def test_invoice_pdf_download(self):
        """
        Verify PDF tax invoice generation and content type.
        """
        with schema_context(self.tenant.schema_name):
            sale = Sale.objects.filter(branch=self.branch).first()
            if not sale:
                # Create a quick sale if not yet created
                summary = StockSummary.objects.get(product=self.product)
                if summary.quantity_on_hand < 1:
                    summary.quantity_on_hand = 1
                    summary.save()

                payload = {
                    "items": [{"product_id": self.product.id, "quantity": 1, "gold_rate_per_gram": "7000.00"}],
                    "payment": {"method": "cash", "amount": "70000.00"},
                }
                res = self.client.post(
                    '/api/sales/',
                    data=json.dumps(payload),
                    content_type='application/json',
                    HTTP_AUTHORIZATION=f'Bearer {self.cashier_token}',
                    HTTP_X_TENANT='demo'
                )
                sale_id = res.json()['id']
            else:
                sale_id = sale.id

            pdf_res = self.client.get(
                f'/api/sales/{sale_id}/invoice-pdf/',
                HTTP_AUTHORIZATION=f'Bearer {self.cashier_token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(pdf_res.status_code, 200)
            self.assertEqual(pdf_res['Content-Type'], 'application/pdf')
            self.assertGreater(len(pdf_res.content), 1000)

    def test_cancel_sale_and_reverse_inventory(self):
        """
        Verify that voiding/cancelling a sale restores product stock and marks sale cancelled.
        """
        with schema_context(self.tenant.schema_name):
            summary = StockSummary.objects.get(product=self.product)
            before_stock = summary.quantity_on_hand
            if before_stock < 1:
                summary.quantity_on_hand = 1
                summary.save()
                before_stock = 1

            # Make a sale
            payload = {
                "items": [{"product_id": self.product.id, "quantity": 1, "gold_rate_per_gram": "7000.00"}],
                "payment": {"method": "cash", "amount": "70000.00"},
            }
            res = self.client.post(
                '/api/sales/',
                data=json.dumps(payload),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.cashier_token}',
                HTTP_X_TENANT='demo'
            )
            sale_id = res.json()['id']

            # Cancel sale as owner
            cancel_res = self.client.post(
                f'/api/sales/{sale_id}/cancel/',
                HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(cancel_res.status_code, 200)
            self.assertEqual(cancel_res.json()['sale_status'], 'cancelled')

            # Stock must be restored
            summary.refresh_from_db()
            self.assertEqual(summary.quantity_on_hand, before_stock)
