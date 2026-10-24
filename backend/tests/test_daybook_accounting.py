import json
from decimal import Decimal
from django.test import TestCase, Client as TestClient
from django_tenants.utils import schema_context
from apps.tenants.models import Client, Domain
from apps.accounts.models import User, Branch
from apps.accounting.models import DayBook
from ninja_api.auth import create_token


class DayBookAccountingTestCase(TestCase):
    """
    Unit & Integration tests for Daily DayBook cash accounting and cash drawer closing.
    """

    @classmethod
    def setUpTestData(cls):
        cls.tenant = Client.objects.filter(schema_name='demo').first()
        if not cls.tenant:
            cls.tenant = Client(schema_name='demo', name='Demo Jewellery')
            cls.tenant.save()
            Domain.objects.create(domain='demo.localhost', tenant=cls.tenant, is_primary=True)

        with schema_context(cls.tenant.schema_name):
            cls.branch = Branch.objects.create(name="Accounting Branch")
            cls.accountant = User.objects.create_user(
                username="head_accountant",
                password="AccountantPass@123",
                role=User.Role.ACCOUNTANT,
                branch=cls.branch,
            )
            cls.cashier = User.objects.create_user(
                username="floor_cashier",
                password="CashierPass@123",
                role=User.Role.STAFF,
                branch=cls.branch,
            )

    def setUp(self):
        self.client = TestClient()
        with schema_context(self.tenant.schema_name):
            self.accountant_token = create_token(self.accountant)
            self.cashier_token = create_token(self.cashier)

    def test_get_today_day_book(self):
        with schema_context(self.tenant.schema_name):
            res = self.client.get(
                '/api/day-book/today/',
                HTTP_AUTHORIZATION=f'Bearer {self.accountant_token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertIn('date', data)
            self.assertIn('opening_balance', data)
            self.assertFalse(data['is_closed'])

    def test_petty_cash_entry(self):
        with schema_context(self.tenant.schema_name):
            res = self.client.post(
                '/api/day-book/cash-entry/',
                data=json.dumps({
                    "entry_type": "out",
                    "amount": "250.00",
                    "note": "Office tea and mineral water",
                }),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.accountant_token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 201)
            data = res.json()
            self.assertGreaterEqual(Decimal(data['cash_out']), Decimal('250.00'))

    def test_day_book_closure(self):
        with schema_context(self.tenant.schema_name):
            # Get today
            get_res = self.client.get(
                '/api/day-book/today/',
                HTTP_AUTHORIZATION=f'Bearer {self.accountant_token}',
                HTTP_X_TENANT='demo'
            )
            day_id = get_res.json()['id']

            # Close day as accountant
            close_res = self.client.post(
                f'/api/day-book/{day_id}/close/',
                data=json.dumps({"notes": "All cash tallied with physical safe counter"}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.accountant_token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(close_res.status_code, 200)
            data = close_res.json()
            self.assertTrue(data['is_closed'])
            self.assertEqual(
                Decimal(data['closing_balance']),
                Decimal(data['opening_balance']) + Decimal(data['cash_in']) - Decimal(data['cash_out'])
            )

    def test_cashier_cannot_close_daybook(self):
        with schema_context(self.tenant.schema_name):
            day = DayBook.objects.filter(branch=self.branch, is_closed=False).first()
            if not day:
                from django.utils import timezone
                day = DayBook.objects.create(date=timezone.localdate(), branch=self.branch)

            close_res = self.client.post(
                f'/api/day-book/{day.id}/close/',
                data=json.dumps({}),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.cashier_token}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(close_res.status_code, 403)
