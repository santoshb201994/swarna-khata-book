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

            # Test query token authentication fallback (for browser tab window.open downloads)
            query_res = self.client.get(
                f'/api/sales/{sale_id}/invoice-pdf/?token={self.cashier_token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(query_res.status_code, 200)
            self.assertEqual(query_res['Content-Type'], 'application/pdf')

            # Test underscore compatibility route
            underscore_res = self.client.get(
                f'/api/sales/{sale_id}/invoice_pdf/?token={self.cashier_token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(underscore_res.status_code, 200)
            self.assertEqual(underscore_res['Content-Type'], 'application/pdf')

    def test_customer_create_search_and_duplicate_prevention(self):
        """
        Tests customer addition, autocomplete search, and duplicate phone handling.
        """
        with schema_context(self.tenant.schema_name):
            # 1. Create a new customer
            cust_payload = {
                "name": "Suresh Vernekar",
                "phone": "9845012345",
                "pan_number": "ABCDE1234F",
                "address": "Sarafa Bazaar, Gadag",
                "email": "suresh@example.com",
            }
            res = self.client.post(
                '/api/customers/',
                data=json.dumps(cust_payload),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.cashier_token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 201)
            created_data = res.json()
            self.assertEqual(created_data['name'], "Suresh Vernekar")
            self.assertEqual(created_data['phone'], "9845012345")
            self.assertEqual(created_data['pan_number'], "ABCDE1234F")

            # 2. Search customer by name
            search_name_res = self.client.get(
                '/api/customers/?search=Vernekar',
                HTTP_AUTHORIZATION=f'Bearer {self.cashier_token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(search_name_res.status_code, 200)
            results = search_name_res.json()
            self.assertTrue(any(c['id'] == created_data['id'] for c in results))

            # 3. Search customer by phone
            search_phone_res = self.client.get(
                '/api/customers/?search=98450',
                HTTP_AUTHORIZATION=f'Bearer {self.cashier_token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(search_phone_res.status_code, 200)
            self.assertTrue(any(c['id'] == created_data['id'] for c in search_phone_res.json()))

            # 4. Search customer by PAN
            search_pan_res = self.client.get(
                '/api/customers/?search=ABCDE1234F',
                HTTP_AUTHORIZATION=f'Bearer {self.cashier_token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(search_pan_res.status_code, 200)
            self.assertTrue(any(c['id'] == created_data['id'] for c in search_pan_res.json()))

            # 5. Duplicate phone prevention
            dup_res = self.client.post(
                '/api/customers/',
                data=json.dumps(cust_payload),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.cashier_token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(dup_res.status_code, 400)
            self.assertIn("already exists", dup_res.json()['error'])
            self.assertEqual(dup_res.json()['existing_customer_id'], created_data['id'])

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

    def test_multi_metal_billing_gold_and_silver_distinct_rates(self):
        """
        Verify that billing a mixed bill with both Gold and Silver items
        properly bills each item with respect to its own metal rates,
        without applying the gold rate to silver.
        """
        with schema_context(self.tenant.schema_name):
            silver_purity, _ = Purity.objects.get_or_create(
                name="Silver (925)", defaults={"fineness": Decimal("0.925")}
            )
            silver_cat, _ = Category.objects.get_or_create(name="Silver Ornaments")
            silver_prod = Product.objects.create(
                name="Silver Leg Chain 925",
                sku="SLV-LEG-TEST-01",
                category=silver_cat,
                purity=silver_purity,
                gross_weight=Decimal("50.000"),
                stone_weight=Decimal("0.000"),
                other_weight=Decimal("0.000"),
                making_charge_type="per_gram",
                making_charge_value=Decimal("15.00"),
                branch=self.branch,
            )
            StockSummary.objects.create(product=silver_prod, quantity_on_hand=5)

            # Ensure stock on gold product
            gold_summary = StockSummary.objects.get(product=self.product)
            gold_summary.quantity_on_hand = 5
            gold_summary.save()

            # Checkout: 1 unit Gold (net 9.5g @ 7000.00/g + 400 mk = 66,900.00)
            #           1 unit Silver (net 50.0g @ 95.00/g + (50 * 15 mk = 750) = 5,500.00)
            # Subtotal = 66,900.00 + 5,500.00 = 72,400.00
            # 3% GST = 2,172.00
            # Total = 74,572.00
            payload = {
                "items": [
                    {
                        "product_id": self.product.id,
                        "quantity": 1,
                        "gold_rate_per_gram": "7000.00",
                        "making_charge": "400.00",
                        "stone_charge": "0.00",
                    },
                    {
                        "product_id": silver_prod.id,
                        "quantity": 1,
                        "gold_rate_per_gram": "95.00",
                        "making_charge": "750.00",
                        "stone_charge": "0.00",
                    },
                ],
                "payment": {"method": "cash", "amount": "74572.00"},
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
            self.assertEqual(Decimal(str(data['subtotal'])), Decimal("72400.00"))
            self.assertEqual(Decimal(str(data['total_amount'])), Decimal("74572.00"))

            items = data['items']
            self.assertEqual(len(items), 2)
            gold_item = next(it for it in items if it['product_id'] == self.product.id)
            silver_item = next(it for it in items if it['product_id'] == silver_prod.id)

            self.assertEqual(Decimal(str(gold_item['gold_rate_per_gram'])), Decimal("7000.00"))
            self.assertEqual(Decimal(str(gold_item['total_price'])), Decimal("66900.00"))

            self.assertEqual(Decimal(str(silver_item['gold_rate_per_gram'])), Decimal("95.00"))
            self.assertEqual(Decimal(str(silver_item['total_price'])), Decimal("5500.00"))

    def test_get_current_rates_returns_all_configured_purities_including_silver(self):
        """
        Verify that /api/gold-rates/current/ returns active benchmark rates
        for all configured purities, ensuring silver has its rate populated.
        """
        with schema_context(self.tenant.schema_name):
            Purity.objects.get_or_create(
                name="Silver (925)", defaults={"fineness": Decimal("0.925")}
            )
            res = self.client.get(
                '/api/gold-rates/current/',
                HTTP_AUTHORIZATION=f'Bearer {self.cashier_token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 200)
            rates = res.json()
            rate_names = [r['purity_name'] for r in rates]
            self.assertIn("Silver (925)", rate_names)
            silver_rate = next(r for r in rates if r['purity_name'] == "Silver (925)")
            self.assertEqual(Decimal(str(silver_rate['rate_per_gram'])), Decimal("92.00"))

    def test_sold_item_automatically_removed_from_shop_inventory(self):
        """
        Verify that after selling a particular item:
        1. It is automatically removed from active shop inventory (is_active=False).
        2. Its authoritative Item status is marked SOLD.
        3. Stock on hand reaches 0.
        4. It is no longer returned in GET /api/products/.
        5. If the sale is cancelled, it is automatically restored to active inventory.
        """
        from apps.billing.models import Item
        with schema_context(self.tenant.schema_name):
            # Create a unique jewellery piece with 1 unit in stock
            piece = Product.objects.create(
                name="Diamond Solitaire Ring",
                sku="SOLITAIRE-001",
                category=self.category,
                purity=self.purity,
                gross_weight=Decimal("5.000"),
                stone_weight=Decimal("0.500"),
                branch=self.branch,
                is_active=True,
            )
            StockSummary.objects.create(product=piece, quantity_on_hand=1)
            Item.objects.create(
                qr_code=piece.sku,
                name=piece.name,
                weight=piece.gross_weight,
                status=Item.Status.AVAILABLE
            )

            # Before sale: Item is present in active inventory
            res_before = self.client.get(
                '/api/products/',
                HTTP_AUTHORIZATION=f'Bearer {self.cashier_token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res_before.status_code, 200)
            skus_before = [p['sku'] for p in res_before.json()]
            self.assertIn("SOLITAIRE-001", skus_before)

            # Sell the item
            payload = {
                "items": [
                    {
                        "product_id": piece.id,
                        "quantity": 1,
                        "gold_rate_per_gram": "7000.00",
                        "making_charge": "500.00",
                        "stone_charge": "2000.00",
                    }
                ],
                "payments": [{"method": "cash", "amount": "40000.00"}],
            }
            sale_res = self.client.post(
                '/api/sales/',
                data=json.dumps(payload),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.cashier_token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(sale_res.status_code, 201)
            sale_id = sale_res.json()['id']

            # After sale: piece is automatically deactivated and marked SOLD
            piece.refresh_from_db()
            self.assertFalse(piece.is_active)

            item_rec = Item.objects.get(qr_code=piece.sku)
            self.assertEqual(item_rec.status, Item.Status.SOLD)

            summary = StockSummary.objects.get(product=piece)
            self.assertEqual(summary.quantity_on_hand, 0)

            # Product list now strictly excludes the sold item from active shop inventory
            res_after = self.client.get(
                '/api/products/',
                HTTP_AUTHORIZATION=f'Bearer {self.cashier_token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res_after.status_code, 200)
            skus_after = [p['sku'] for p in res_after.json()]
            self.assertNotIn("SOLITAIRE-001", skus_after)

            # Void / Cancel the sale -> restores item to active inventory
            cancel_res = self.client.post(
                f'/api/sales/{sale_id}/cancel/',
                HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(cancel_res.status_code, 200)

            piece.refresh_from_db()
            self.assertTrue(piece.is_active)
            item_rec.refresh_from_db()
            self.assertEqual(item_rec.status, Item.Status.AVAILABLE)
            summary.refresh_from_db()
            self.assertEqual(summary.quantity_on_hand, 1)

            res_restored = self.client.get(
                '/api/products/',
                HTTP_AUTHORIZATION=f'Bearer {self.cashier_token}',
                HTTP_X_TENANT='demo'
            )
            skus_restored = [p['sku'] for p in res_restored.json()]
            self.assertIn("SOLITAIRE-001", skus_restored)
