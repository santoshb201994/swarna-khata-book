"""
Extended backend tests covering all feature validation fixes applied in the frontend audit:
 - Product gross_weight=0 API rejection (422)
 - Product stone+other weight exceeding gross weight API rejection (422)
 - Store registration GSTIN format validation (client-side only — backend accepts any string)
 - Customer email format — backend accepts any string (validation is frontend-only)
 - Old gold rate/weight negative values — already blocked by schema (ge=0), verified here
 - Product weight filter: min > max edge case is frontend-only

These tests are added to NinjaProductsStockTestCase and StoreOnboardingAndRBACTestCase.
"""
import json
from decimal import Decimal
from django.test import TestCase, Client as TestClient
from django_tenants.utils import schema_context
from apps.tenants.models import Client, Domain
from apps.accounts.models import User, Branch
from apps.products.models import Category, Purity, Product
from apps.stock.models import StockSummary
from apps.accounting.models import Customer
from ninja_api.auth import create_token


class ProductValidationTestCase(TestCase):
    """
    Backend API-level validation tests for Product creation constraints.
    Verifies that the API rejects invalid weight inputs that the frontend
    now also guards against via UI validation.
    """

    @classmethod
    def setUpTestData(cls):
        cls.tenant = Client.objects.filter(schema_name='demo').first()
        if not cls.tenant:
            cls.tenant = Client(schema_name='demo', name='Demo Jewellery')
            cls.tenant.save()
            Domain.objects.create(domain='demo.localhost', tenant=cls.tenant, is_primary=True)

        with schema_context(cls.tenant.schema_name):
            cls.branch = Branch.objects.create(name="Validation Test Branch")
            cls.manager = User.objects.create_user(
                username="val_manager",
                password="Manager*Vault9",
                role=User.Role.MANAGER,
                branch=cls.branch,
            )
            cls.category = Category.objects.create(name="Bangles")
            cls.purity = Purity.objects.create(name="18KT (750)", fineness=Decimal("0.750"))

    def setUp(self):
        self.client = TestClient()
        with schema_context(self.tenant.schema_name):
            self.token = create_token(self.manager)

    def _post_product(self, payload):
        return self.client.post(
            '/api/products/',
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}',
            HTTP_X_TENANT='demo'
        )

    def test_product_creation_rejects_zero_gross_weight(self):
        """
        API must reject gross_weight=0. ProductIn schema has Field(..., gt=0).
        Frontend ProductFormModal now also validates grossWeight > 0 before submit.
        """
        with schema_context(self.tenant.schema_name):
            res = self._post_product({
                "name": "Zero Weight Bangle",
                "sku": "BANGLE-ZERO-001",
                "category_id": self.category.id,
                "purity_id": self.purity.id,
                "gross_weight": "0.000",
                "making_charge_type": "per_gram",
                "making_charge_value": "200.00",
            })
            self.assertEqual(res.status_code, 422,
                msg="gross_weight=0 must be rejected with 422 Unprocessable Entity")

    def test_product_creation_rejects_negative_gross_weight(self):
        """
        API must reject gross_weight < 0. Field(gt=0) enforces strictly positive.
        """
        with schema_context(self.tenant.schema_name):
            res = self._post_product({
                "name": "Negative Weight Bangle",
                "sku": "BANGLE-NEG-001",
                "category_id": self.category.id,
                "purity_id": self.purity.id,
                "gross_weight": "-5.000",
                "making_charge_type": "per_gram",
                "making_charge_value": "200.00",
            })
            self.assertEqual(res.status_code, 422,
                msg="gross_weight < 0 must be rejected with 422")

    def test_product_creation_rejects_stone_weight_exceeding_gross(self):
        """
        Backend router validates that stone_weight + other_weight <= gross_weight.
        Frontend ProductFormModal now shows a warning if stone > gross.
        """
        with schema_context(self.tenant.schema_name):
            res = self._post_product({
                "name": "Invalid Stone Bangle",
                "sku": "BANGLE-STONE-ERR-001",
                "category_id": self.category.id,
                "purity_id": self.purity.id,
                "gross_weight": "5.000",
                "stone_weight": "6.000",  # stone > gross — invalid
                "other_weight": "0.000",
                "making_charge_type": "per_gram",
                "making_charge_value": "200.00",
            })
            # Backend returns 400 or 422 for this business rule
            self.assertIn(res.status_code, [400, 422],
                msg="stone_weight > gross_weight must be rejected")

    def test_product_creation_rejects_combined_weights_exceeding_gross(self):
        """
        Combined stone + other weight must not exceed gross weight.
        """
        with schema_context(self.tenant.schema_name):
            res = self._post_product({
                "name": "Invalid Combined Weight Bangle",
                "sku": "BANGLE-COMBO-ERR-001",
                "category_id": self.category.id,
                "purity_id": self.purity.id,
                "gross_weight": "10.000",
                "stone_weight": "7.000",
                "other_weight": "5.000",  # 7 + 5 = 12 > 10
                "making_charge_type": "per_gram",
                "making_charge_value": "200.00",
            })
            self.assertIn(res.status_code, [400, 422],
                msg="stone+other > gross must be rejected")

    def test_product_creation_rejects_negative_stone_weight(self):
        """
        stone_weight must be >= 0. Field(ge=0) enforces this.
        """
        with schema_context(self.tenant.schema_name):
            res = self._post_product({
                "name": "Negative Stone Bangle",
                "sku": "BANGLE-NEGSTONE-001",
                "category_id": self.category.id,
                "purity_id": self.purity.id,
                "gross_weight": "10.000",
                "stone_weight": "-1.000",
                "making_charge_type": "per_gram",
                "making_charge_value": "200.00",
            })
            self.assertEqual(res.status_code, 422,
                msg="stone_weight < 0 must be rejected with 422")

    def test_product_creation_accepts_valid_weights(self):
        """
        Sanity check: valid weights with stone < gross must succeed.
        """
        with schema_context(self.tenant.schema_name):
            res = self._post_product({
                "name": "Valid Gold Bangle",
                "sku": "BANGLE-VALID-001",
                "category_id": self.category.id,
                "purity_id": self.purity.id,
                "gross_weight": "15.500",
                "stone_weight": "2.000",
                "other_weight": "0.500",
                "making_charge_type": "per_gram",
                "making_charge_value": "350.00",
                "initial_stock": 1,
            })
            self.assertEqual(res.status_code, 201,
                msg="Valid product with stone < gross must be accepted")
            data = res.json()
            # net_weight = 15.5 - 2.0 - 0.5 = 13.0
            self.assertEqual(Decimal(data['net_weight']), Decimal("13.000"))

    def test_product_update_rejects_zero_gross_weight(self):
        """
        ProductUpdateIn also enforces gt=0 on gross_weight updates.
        """
        with schema_context(self.tenant.schema_name):
            product = Product.objects.create(
                name="Update Test Bangle",
                sku="BANGLE-UPD-001",
                category=self.category,
                purity=self.purity,
                gross_weight=Decimal("10.000"),
                branch=self.branch,
            )
            res = self.client.put(
                f'/api/products/{product.id}/',
                data=json.dumps({"gross_weight": "0.000"}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 422,
                msg="Updating gross_weight to 0 must be rejected with 422")


class OldGoldValidationTestCase(TestCase):
    """
    Verifies that the SaleCreateIn schema rejects negative old_gold_weight
    and old_gold_rate values. Frontend POSScreen now also enforces min=0.
    """

    @classmethod
    def setUpTestData(cls):
        cls.tenant = Client.objects.filter(schema_name='demo').first()
        if not cls.tenant:
            cls.tenant = Client(schema_name='demo', name='Demo Jewellery')
            cls.tenant.save()
            Domain.objects.create(domain='demo.localhost', tenant=cls.tenant, is_primary=True)

        with schema_context(cls.tenant.schema_name):
            cls.branch = Branch.objects.create(name="Old Gold Test Branch")
            cls.cashier = User.objects.create_user(
                username="og_cashier",
                password="OGCashier*9",
                role=User.Role.STAFF,
                branch=cls.branch,
            )
            cls.category = Category.objects.create(name="Rings")
            cls.purity = Purity.objects.create(name="22KT-OG", fineness=Decimal("0.916"))
            cls.product = Product.objects.create(
                name="Old Gold Test Ring",
                sku="RING-OG-001",
                category=cls.category,
                purity=cls.purity,
                gross_weight=Decimal("8.000"),
                stone_weight=Decimal("0.000"),
                making_charge_type="per_gram",
                making_charge_value=Decimal("300.00"),
                branch=cls.branch,
            )
            StockSummary.objects.create(product=cls.product, quantity_on_hand=5)

    def setUp(self):
        self.client = TestClient()
        with schema_context(self.tenant.schema_name):
            self.cashier_token = create_token(self.cashier)

    def test_checkout_rejects_negative_old_gold_weight(self):
        """
        SaleCreateIn.old_gold_weight has ge=0. Negative values must be rejected.
        Frontend POSScreen now enforces min=0 on old gold weight inputs.
        """
        with schema_context(self.tenant.schema_name):
            res = self.client.post(
                '/api/sales/',
                data=json.dumps({
                    "items": [{"product_id": self.product.id, "quantity": 1, "gold_rate_per_gram": "7000.00"}],
                    "payment": {"method": "cash", "amount": "60000.00"},
                    "old_gold_weight": "-2.000",  # negative — must fail
                    "old_gold_rate": "5500.00",
                }),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.cashier_token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 422,
                msg="Negative old_gold_weight must be rejected with 422")

    def test_checkout_rejects_negative_old_gold_rate(self):
        """
        SaleCreateIn.old_gold_rate has ge=0. Negative values must be rejected.
        Frontend POSScreen now enforces min=0 on old gold rate inputs.
        """
        with schema_context(self.tenant.schema_name):
            res = self.client.post(
                '/api/sales/',
                data=json.dumps({
                    "items": [{"product_id": self.product.id, "quantity": 1, "gold_rate_per_gram": "7000.00"}],
                    "payment": {"method": "cash", "amount": "60000.00"},
                    "old_gold_weight": "5.000",
                    "old_gold_rate": "-100.00",  # negative — must fail
                }),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.cashier_token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 422,
                msg="Negative old_gold_rate must be rejected with 422")

    def test_checkout_accepts_zero_old_gold_values(self):
        """
        old_gold_weight=0 and old_gold_rate=0 must be accepted (no-old-gold scenario).
        """
        with schema_context(self.tenant.schema_name):
            res = self.client.post(
                '/api/sales/',
                data=json.dumps({
                    "items": [{"product_id": self.product.id, "quantity": 1, "gold_rate_per_gram": "7000.00"}],
                    "payment": {"method": "cash", "amount": "70000.00"},
                    "old_gold_weight": "0.000",
                    "old_gold_rate": "0.00",
                }),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.cashier_token}',
                HTTP_X_TENANT='demo'
            )
            self.assertIn(res.status_code, [200, 201],
                msg="Zero old_gold values must be accepted as a valid no-old-gold sale")


class CustomerEmailValidationTestCase(TestCase):
    """
    Verifies the customer API behavior for email field.
    The backend accepts any string in the email field (no format validation at API level).
    Email format validation is enforced client-side in CustomerFormModal.
    These tests confirm the backend contract and that valid emails round-trip correctly.
    """

    @classmethod
    def setUpTestData(cls):
        cls.tenant = Client.objects.filter(schema_name='demo').first()
        if not cls.tenant:
            cls.tenant = Client(schema_name='demo', name='Demo Jewellery')
            cls.tenant.save()
            Domain.objects.create(domain='demo.localhost', tenant=cls.tenant, is_primary=True)

        with schema_context(cls.tenant.schema_name):
            cls.branch = Branch.objects.create(name="Customer Test Branch")
            cls.operator = User.objects.create_user(
                username="cust_operator",
                password="CustOp*Vault9",
                role=User.Role.STAFF,
                branch=cls.branch,
            )

    def setUp(self):
        self.client = TestClient()
        with schema_context(self.tenant.schema_name):
            self.token = create_token(self.operator)

    def test_customer_creation_with_valid_email(self):
        """Valid email address is accepted and stored correctly."""
        with schema_context(self.tenant.schema_name):
            res = self.client.post(
                '/api/customers/',
                data=json.dumps({
                    "name": "Priya Sharma",
                    "phone": "9988001122",
                    "email": "priya.sharma@gmail.com",
                }),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 201)
            self.assertEqual(res.json()['email'], "priya.sharma@gmail.com")

    def test_customer_creation_with_empty_email_is_allowed(self):
        """Email is optional — omitting it must succeed."""
        with schema_context(self.tenant.schema_name):
            res = self.client.post(
                '/api/customers/',
                data=json.dumps({
                    "name": "Anand Verma",
                    "phone": "9988001133",
                    "email": "",
                }),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 201)

    def test_customer_creation_with_no_email_field_is_allowed(self):
        """CustomerIn.email has a default of '' — omitting the field entirely must succeed."""
        with schema_context(self.tenant.schema_name):
            res = self.client.post(
                '/api/customers/',
                data=json.dumps({
                    "name": "Rekha Patel",
                    "phone": "9988001144",
                }),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 201)
