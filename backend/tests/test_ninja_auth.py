import json
from django.test import TestCase, Client as TestClient
from django_tenants.utils import schema_context
from apps.tenants.models import Client, Domain
from apps.accounts.models import User, Branch
from ninja_api.auth import create_token


class NinjaAuthTestCase(TestCase):
    """
    Unit & Integration tests for Django Ninja JWT authentication and RBAC.
    """

    @classmethod
    def setUpTestData(cls):
        cls.tenant = Client.objects.filter(schema_name='demo').first()
        if not cls.tenant:
            cls.tenant = Client(schema_name='demo', name='Demo Jewellery')
            cls.tenant.save()
            Domain.objects.create(domain='demo.localhost', tenant=cls.tenant, is_primary=True)

        with schema_context(cls.tenant.schema_name):
            cls.branch = Branch.objects.create(name="Main Showroom", phone="9876543210")
            cls.owner = User.objects.create_user(
                username="owner_user",
                password="SecurePassword@123",
                role=User.Role.OWNER,
                branch=cls.branch,
            )
            cls.staff = User.objects.create_user(
                username="cashier_user",
                password="CashierPass@123",
                role=User.Role.STAFF,
                branch=cls.branch,
            )

    def setUp(self):
        self.client = TestClient()

    def test_obtain_token_success(self):
        with schema_context(self.tenant.schema_name):
            res = self.client.post(
                '/api/auth/token/',
                data=json.dumps({"username": "owner_user", "password": "SecurePassword@123"}),
                content_type='application/json',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertIn('access', data)
            self.assertIn('refresh', data)
            self.assertEqual(data['user']['username'], 'owner_user')
            self.assertEqual(data['user']['role'], 'owner')

    def test_obtain_token_invalid_password(self):
        with schema_context(self.tenant.schema_name):
            res = self.client.post(
                '/api/auth/token/',
                data=json.dumps({"username": "owner_user", "password": "WrongPassword"}),
                content_type='application/json',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 401)

    def test_refresh_token(self):
        with schema_context(self.tenant.schema_name):
            refresh_tok = create_token(self.owner, token_type='refresh')
            res = self.client.post(
                '/api/auth/token/refresh/',
                data=json.dumps({"refresh": refresh_tok}),
                content_type='application/json',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertIn('access', data)

    def test_get_current_user_profile(self):
        with schema_context(self.tenant.schema_name):
            access_tok = create_token(self.owner, token_type='access')
            res = self.client.get(
                '/api/auth/me',
                HTTP_AUTHORIZATION=f'Bearer {access_tok}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 200)
            data = res.json()
            self.assertEqual(data['username'], 'owner_user')
            self.assertEqual(data['role'], 'owner')
            self.assertEqual(data['branch_name'], 'Main Showroom')

    def test_rbac_owner_can_create_user(self):
        with schema_context(self.tenant.schema_name):
            access_tok = create_token(self.owner, token_type='access')
            res = self.client.post(
                '/api/users/',
                data=json.dumps({
                    "username": "new_accountant",
                    "password": "Finance*Key9",
                    "role": "accountant",
                    "branch_id": self.branch.id,
                }),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {access_tok}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 201)
            self.assertTrue(User.objects.filter(username="new_accountant").exists())

    def test_rbac_staff_cannot_create_user(self):
        with schema_context(self.tenant.schema_name):
            access_tok = create_token(self.staff, token_type='access')
            res = self.client.post(
                '/api/users/',
                data=json.dumps({
                    "username": "unauthorized_user",
                    "password": "Worker*Secret9",
                    "role": "staff",
                }),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {access_tok}',
                HTTP_X_TENANT='demo'
            )
            self.assertEqual(res.status_code, 403)
            self.assertFalse(User.objects.filter(username="unauthorized_user").exists())
