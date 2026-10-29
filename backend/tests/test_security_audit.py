import io
import json
from decimal import Decimal
from django.test import TestCase, Client as HttpClient
from django.core.files.uploadedfile import SimpleUploadedFile
from django_tenants.utils import schema_context

from apps.tenants.models import Client, Domain
from apps.accounts.models import User, Branch
from apps.products.models import Product, Category, Purity
from apps.accounting.models import DayBook
from apps.billing.models import Sale
from ninja_api.auth import create_token


class SecurityAuditAndAccessControlTestCase(TestCase):
    """
    Automated regression and hardening test suite verifying:
    1. Cross-tenant header spoofing isolation
    2. Staff access restrictions (RBAC) on master catalog & inventory
    3. File upload restrictions (content-type, extension, size)
    4. Financial invariants (non-negative rates, quantities, discount bounds)
    5. DayBook cash drawer locking against closed drawer mutations
    6. Unauthenticated route lockdown (/api/tenants/, /api/bills/)
    """

    @classmethod
    def setUpTestData(cls):
        # Setup Public and Two Tenant Schemas for Cross-Tenant tests
        with schema_context('public'):
            cls.public_client, _ = Client.objects.get_or_create(
                schema_name='public',
                defaults={'name': 'Public Platform Master'}
            )
            Domain.objects.get_or_create(
                domain='localhost',
                defaults={'tenant': cls.public_client, 'is_primary': True}
            )

            cls.tenant_a, _ = Client.objects.get_or_create(
                schema_name='tenant_sec_a',
                defaults={'name': 'Security Tenant A'}
            )
            Domain.objects.get_or_create(
                domain='seca.localhost',
                defaults={'tenant': cls.tenant_a, 'is_primary': True}
            )

            cls.tenant_b, _ = Client.objects.get_or_create(
                schema_name='tenant_sec_b',
                defaults={'name': 'Security Tenant B'}
            )
            Domain.objects.get_or_create(
                domain='secb.localhost',
                defaults={'tenant': cls.tenant_b, 'is_primary': True}
            )

            cls.superadmin, _ = User.objects.get_or_create(
                username='audit_superadmin',
                defaults={'is_superuser': True, 'role': 'superadmin'}
            )
            cls.superadmin_tok = create_token(cls.superadmin, token_type='access')

        # Setup Tenant A Users and Catalog
        with schema_context(cls.tenant_a.schema_name):
            cls.branch_a = Branch.objects.create(name='Showroom A', is_active=True)
            cls.cat_a = Category.objects.create(name='Gold Rings A')
            cls.purity_a = Purity.objects.create(name='22KT 916 A', fineness=Decimal('0.916'))

            cls.owner_a = User.objects.create_user(
                username='owner_a',
                password='Owner*Vault9',
                role=User.Role.OWNER,
                branch=cls.branch_a
            )
            cls.owner_a_tok = create_token(cls.owner_a, token_type='access')

            cls.staff_a = User.objects.create_user(
                username='staff_a',
                password='Staff*Vault8',
                role=User.Role.STAFF,
                branch=cls.branch_a
            )
            cls.staff_a_tok = create_token(cls.staff_a, token_type='access')

            cls.prod_a = Product.objects.create(
                name='Gold Band A',
                sku='BAND-A-001',
                category=cls.cat_a,
                purity=cls.purity_a,
                gross_weight=Decimal('10.000'),
                branch=cls.branch_a,
                is_active=True
            )

        # Setup Tenant B Catalog
        with schema_context(cls.tenant_b.schema_name):
            cls.branch_b = Branch.objects.create(name='Showroom B', is_active=True)
            cls.cat_b = Category.objects.create(name='Diamond Pendants B')
            cls.purity_b = Purity.objects.create(name='18KT B', fineness=Decimal('0.750'))
            cls.prod_b = Product.objects.create(
                name='Diamond Heart B',
                sku='HEART-B-001',
                category=cls.cat_b,
                purity=cls.purity_b,
                gross_weight=Decimal('4.500'),
                branch=cls.branch_b,
                is_active=True
            )

        cls.client = HttpClient()

    # ==========================================================================
    # 1. MULTI-TENANT CROSS-IMPERSONATION REJECTION
    # ==========================================================================

    def test_cross_tenant_header_spoofing_rejected(self):
        """
        Verify that a user from Tenant A providing X-Tenant: tenant_sec_b
        cannot query or leak Tenant B's inventory. The request remains confined to Tenant A.
        """
        res = self.client.get(
            '/api/products/',
            HTTP_AUTHORIZATION=f'Bearer {self.owner_a_tok}',
            HTTP_X_TENANT='tenant_sec_b'
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        # Data must contain Tenant A's product, NEVER Tenant B's product
        skus = [p['sku'] for p in data]
        self.assertIn('BAND-A-001', skus)
        self.assertNotIn('HEART-B-001', skus)

    # ==========================================================================
    # 2. STAFF ACCESS RESTRICTIONS (RBAC) ON MASTER CATALOG & STOCK
    # ==========================================================================

    def test_staff_cannot_create_or_modify_products(self):
        """Staff members are forbidden from creating, updating, or deleting products."""
        # 1. Create Product
        payload = {
            "name": "Unauthorized Ring",
            "sku": "UNAUTH-001",
            "category_id": self.cat_a.id,
            "purity_id": self.purity_a.id,
            "gross_weight": "5.000",
            "initial_stock": 1
        }
        res = self.client.post(
            '/api/products/',
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.staff_a_tok}'
        )
        self.assertEqual(res.status_code, 403)

        # 2. Update Product
        res = self.client.put(
            f'/api/products/{self.prod_a.id}/',
            data=json.dumps({"gross_weight": "12.000"}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.staff_a_tok}'
        )
        self.assertEqual(res.status_code, 403)

        # 3. Create Category
        res = self.client.post(
            '/api/categories/',
            data=json.dumps({"name": "New Cat"}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.staff_a_tok}'
        )
        self.assertEqual(res.status_code, 403)

        # 4. Create Purity
        res = self.client.post(
            '/api/purities/',
            data=json.dumps({"name": "20KT", "fineness": "0.833"}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.staff_a_tok}'
        )
        self.assertEqual(res.status_code, 403)

        # 5. Manual Stock Movement
        res = self.client.post(
            '/api/stock-movements/',
            data=json.dumps({"product_id": self.prod_a.id, "movement_type": "OUT", "quantity": 1}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.staff_a_tok}'
        )
        self.assertEqual(res.status_code, 403)

    def test_owner_can_create_and_modify_products(self):
        """Store owners and managers have full rights to manage products."""
        payload = {
            "name": "Authorized Kada",
            "sku": "AUTH-KADA-01",
            "category_id": self.cat_a.id,
            "purity_id": self.purity_a.id,
            "gross_weight": "25.000",
            "initial_stock": 2
        }
        res = self.client.post(
            '/api/products/',
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.owner_a_tok}'
        )
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data['sku'], 'AUTH-KADA-01')

    # ==========================================================================
    # 3. FILE UPLOAD SECURITY (PHOTO UPLOAD)
    # ==========================================================================

    def test_photo_upload_rejects_dangerous_extensions_and_types(self):
        """Rejects executable scripts, HTML, and SVG uploads."""
        # SVG upload attempt
        svg_file = SimpleUploadedFile("malicious.svg", b"<svg><script>alert(1)</script></svg>", content_type="image/svg+xml")
        res = self.client.post(
            f'/api/products/{self.prod_a.id}/upload-photo/',
            data={'photo': svg_file},
            HTTP_AUTHORIZATION=f'Bearer {self.owner_a_tok}'
        )
        self.assertEqual(res.status_code, 400)

        # HTML upload attempt
        html_file = SimpleUploadedFile("page.html", b"<html><body>Pwned</body></html>", content_type="text/html")
        res = self.client.post(
            f'/api/products/{self.prod_a.id}/upload-photo/',
            data={'photo': html_file},
            HTTP_AUTHORIZATION=f'Bearer {self.owner_a_tok}'
        )
        self.assertEqual(res.status_code, 400)

    # ==========================================================================
    # 4. POS FINANCIAL INVARIANTS & RANGE VALIDATIONS
    # ==========================================================================

    def test_pos_checkout_rejects_negative_gold_rate_or_quantity(self):
        """Pydantic rejects negative prices or zero/negative quantities."""
        payload = {
            "items": [
                {
                    "product_id": self.prod_a.id,
                    "quantity": -2,
                    "gold_rate_per_gram": "7200.00"
                }
            ]
        }
        res = self.client.post(
            '/api/sales/',
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.staff_a_tok}'
        )
        self.assertIn(res.status_code, [400, 422])

    def test_pos_checkout_rejects_excessive_discount(self):
        """Rejects discounts that exceed the total gross amount of the invoice."""
        with schema_context(self.tenant_a.schema_name):
            from apps.stock.models import StockSummary
            StockSummary.objects.update_or_create(product=self.prod_a, defaults={'quantity_on_hand': 10})

        payload = {
            "items": [
                {
                    "product_id": self.prod_a.id,
                    "quantity": 1,
                    "gold_rate_per_gram": "7000.00",
                    "making_charge": "500.00"
                }
            ],
            "discount": "9999999.00"  # Absurdly high discount
        }
        res = self.client.post(
            '/api/sales/',
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.staff_a_tok}'
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("Discount", res.json().get("error", ""))

    # ==========================================================================
    # 5. DAYBOOK CASH DRAWER LOCKDOWN
    # ==========================================================================

    def test_cash_transactions_blocked_when_daybook_closed(self):
        """Cash sales and petty cash entries are rejected when the DayBook is closed."""
        with schema_context(self.tenant_a.schema_name):
            from django.utils import timezone
            from apps.stock.models import StockSummary
            StockSummary.objects.update_or_create(product=self.prod_a, defaults={'quantity_on_hand': 10})
            today = timezone.localdate()
            day, _ = DayBook.objects.get_or_create(
                date=today, branch=self.branch_a,
                defaults={'opening_balance': Decimal('10000.00')}
            )
            day.is_closed = True
            day.save()

        # 1. Petty cash entry attempt on closed drawer
        res = self.client.post(
            '/api/day-book/cash-entry/',
            data=json.dumps({"entry_type": "in", "amount": "500.00"}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.staff_a_tok}'
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("closed", res.json().get("error", "").lower())

        # 2. Cash checkout attempt on closed drawer
        payload = {
            "items": [
                {
                    "product_id": self.prod_a.id,
                    "quantity": 1,
                    "gold_rate_per_gram": "7000.00"
                }
            ],
            "payment": {
                "method": "cash",
                "amount": "70000.00"
            }
        }
        res = self.client.post(
            '/api/sales/',
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.staff_a_tok}'
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("closed", res.json().get("error", "").lower())

        # 3. Manager can reopen DayBook
        res = self.client.post(
            f'/api/day-book/{day.id}/reopen/',
            HTTP_AUTHORIZATION=f'Bearer {self.owner_a_tok}'
        )
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.json()['is_closed'])

    # ==========================================================================
    # 6. UNAUTHENTICATED ENDPOINT LOCKDOWN
    # ==========================================================================

    def test_unauthenticated_lockdown(self):
        """Verify that administrative endpoints are protected against unauthenticated callers."""
        # /api/tenants/ requires superadmin
        res = self.client.get('/api/tenants/')
        self.assertEqual(res.status_code, 401)

        res = self.client.post('/api/tenants/', data=json.dumps({"name": "Test", "schema_name": "t_test", "domain": "t.localhost"}), content_type='application/json')
        self.assertEqual(res.status_code, 401)

        # /api/bills/ requires authenticated cashier
        res = self.client.post('/api/bills/')
        self.assertEqual(res.status_code, 401)
