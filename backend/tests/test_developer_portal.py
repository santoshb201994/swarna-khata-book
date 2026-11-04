import json
from decimal import Decimal
from django.test import TestCase, Client as HttpClient
from django_tenants.utils import schema_context

from apps.tenants.models import Client, Domain
from apps.accounts.models import User, Branch
from ninja_api.auth import create_token


class DeveloperPortalTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        with schema_context('public'):
            cls.public_tenant, _ = Client.objects.get_or_create(
                schema_name='public',
                defaults={'name': 'Public Master'}
            )
            Domain.objects.get_or_create(
                domain='localhost',
                defaults={'tenant': cls.public_tenant, 'is_primary': True}
            )

            cls.demo_tenant, _ = Client.objects.get_or_create(
                schema_name='demo',
                defaults={'name': 'Demo Jewellers'}
            )
            Domain.objects.get_or_create(
                domain='demo.localhost',
                defaults={'tenant': cls.demo_tenant, 'is_primary': True}
            )

            # Superadmin in public
            cls.superadmin = User.objects.create_superuser(
                username='developer',
                password='Super*Vault9',
                email='developer@swarnakhata.internal'
            )

        with schema_context(cls.demo_tenant.schema_name):
            cls.branch = Branch.objects.create(name='Demo Branch', is_active=True)
            cls.owner = User.objects.create_user(
                username='shop_owner_1',
                password='Owner*Vault9',
                role=User.Role.OWNER,
                branch=cls.branch
            )
            cls.staff = User.objects.create_user(
                username='counter_worker_1',
                password='Worker*Vault8',
                role=User.Role.STAFF,
                branch=cls.branch
            )

        cls.client = HttpClient()

    @classmethod
    def tearDownClass(cls):
        from django.db import connection
        connection.set_schema_to_public()
        super().tearDownClass()

    def test_developer_overview_forbidden_for_owner_and_staff(self):
        with schema_context(self.demo_tenant.schema_name):
            self.owner.tenant_schema = self.demo_tenant.schema_name
            owner_tok = create_token(self.owner, token_type='access')

        res = self.client.get(
            '/api/developer/overview/',
            HTTP_AUTHORIZATION=f'Bearer {owner_tok}',
            HTTP_X_TENANT='demo'
        )
        self.assertEqual(res.status_code, 403)

        with schema_context(self.demo_tenant.schema_name):
            self.staff.tenant_schema = self.demo_tenant.schema_name
            staff_tok = create_token(self.staff, token_type='access')

        res = self.client.get(
            '/api/developer/overview/',
            HTTP_AUTHORIZATION=f'Bearer {staff_tok}',
            HTTP_X_TENANT='demo'
        )
        self.assertEqual(res.status_code, 403)

    def test_developer_overview_success_for_superadmin(self):
        superadmin_tok = create_token(self.superadmin, token_type='access')
        res = self.client.get(
            '/api/developer/overview/',
            HTTP_AUTHORIZATION=f'Bearer {superadmin_tok}'
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("total_tenants", data)
        self.assertIn("tenants", data)
        self.assertTrue(any(t['schema_name'] == 'demo' for t in data['tenants']))

    def test_developer_toggle_tenant_status(self):
        superadmin_tok = create_token(self.superadmin, token_type='access')
        res = self.client.post(
            f'/api/developer/tenants/{self.demo_tenant.schema_name}/toggle-status/',
            data=json.dumps({"is_active": False}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {superadmin_tok}'
        )
        self.assertEqual(res.status_code, 200)
        self.demo_tenant.refresh_from_db()
        self.assertFalse(self.demo_tenant.is_active)

    def test_developer_reset_tenant_user_password(self):
        superadmin_tok = create_token(self.superadmin, token_type='access')
        res = self.client.post(
            f'/api/developer/tenants/{self.demo_tenant.schema_name}/users/{self.owner.id}/reset-password/',
            data=json.dumps({"new_password": "New*Owner#Key7"}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {superadmin_tok}'
        )
        self.assertEqual(res.status_code, 200)
        with schema_context(self.demo_tenant.schema_name):
            self.owner.refresh_from_db()
            self.assertTrue(self.owner.check_password("New*Owner#Key7"))

    def test_developer_toggle_tenant_user_status(self):
        superadmin_tok = create_token(self.superadmin, token_type='access')
        res = self.client.post(
            f'/api/developer/tenants/{self.demo_tenant.schema_name}/users/{self.staff.id}/toggle-status/',
            data=json.dumps({"is_active": False}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {superadmin_tok}'
        )
        self.assertEqual(res.status_code, 200)
        with schema_context(self.demo_tenant.schema_name):
            self.staff.refresh_from_db()
            self.assertFalse(self.staff.is_active)

    def test_developer_switch_store_token(self):
        superadmin_tok = create_token(self.superadmin, token_type='access')
        res = self.client.post(
            '/api/developer/switch-store-token/',
            data=json.dumps({"schema_name": self.demo_tenant.schema_name}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {superadmin_tok}'
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("access", data)
        self.assertEqual(data["schema_name"], self.demo_tenant.schema_name)

    def test_developer_login_endpoint_success(self):
        res = self.client.post(
            '/api/developer/login/',
            data=json.dumps({"username": "developer", "password": "Super*Vault9"}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("access", data)
        self.assertEqual(data["user"]["role"], "superadmin")

    def test_developer_login_endpoint_rejects_non_superadmin(self):
        res = self.client.post(
            '/api/developer/login/',
            data=json.dumps({"username": "shop_owner_1", "password": "Owner*Vault9"}),
            content_type='application/json'
        )
        self.assertIn(res.status_code, [401, 403])

    def test_developer_login_syncs_with_env_password_change(self):
        from django.conf import settings
        # Simulate local .env password change
        original_pass = getattr(settings, 'DEVELOPER_SUPERUSER_PASSWORD', 'Super*Vault9')
        try:
            settings.DEVELOPER_SUPERUSER_PASSWORD = 'NewEnvSecretPassword@2026'
            
            # Old password must now fail
            old_res = self.client.post(
                '/api/developer/login/',
                data=json.dumps({"username": "developer", "password": original_pass}),
                content_type='application/json'
            )
            self.assertEqual(old_res.status_code, 401)

            # New .env password must succeed immediately
            new_res = self.client.post(
                '/api/developer/login/',
                data=json.dumps({"username": "developer", "password": "NewEnvSecretPassword@2026"}),
                content_type='application/json'
            )
            self.assertEqual(new_res.status_code, 200)
        finally:
            settings.DEVELOPER_SUPERUSER_PASSWORD = original_pass

    def test_developer_delete_tenant_cannot_delete_public(self):
        superadmin_tok = create_token(self.superadmin, token_type='access')
        res = self.client.delete(
            '/api/developer/tenants/public/delete/',
            HTTP_AUTHORIZATION=f'Bearer {superadmin_tok}'
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("Cannot delete", res.json().get("error", ""))

    def test_developer_delete_tenant_success(self):
        from django.db import connection
        with schema_context('public'):
            temp_tenant = Client(schema_name='t_temp_test', name='Temp Store')
            temp_tenant.auto_create_schema = False
            temp_tenant.save()
            with connection.cursor() as cur:
                cur.execute('CREATE SCHEMA IF NOT EXISTS "t_temp_test";')
            Domain.objects.create(domain='temp.swarnakhata.internal', tenant=temp_tenant, is_primary=True)

        superadmin_tok = create_token(self.superadmin, token_type='access')
        res = self.client.delete(
            '/api/developer/tenants/t_temp_test/delete/',
            HTTP_AUTHORIZATION=f'Bearer {superadmin_tok}'
        )
        self.assertEqual(res.status_code, 200)
        self.assertFalse(Client.objects.filter(schema_name='t_temp_test').exists())

    def test_register_store_rejects_duplicate_username(self):
        res = self.client.post(
            '/api/tenants/register-store/',
            data=json.dumps({
                "shop_name": "New Jewellery Store",
                "owner_username": "shop_owner_1",
                "owner_password": "Unique*Secur8#Key",
                "owner_email": "new@store.com",
                "owner_phone": "9876543210"
            }),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("already in use", res.json().get("error", "").lower())

    def test_register_store_rejects_platform_reserved_username(self):
        res = self.client.post(
            '/api/tenants/register-store/',
            data=json.dumps({
                "shop_name": "Another Store",
                "owner_username": "developer",
                "owner_password": "Unique*Secur8#Key",
                "owner_email": "another@store.com",
                "owner_phone": "9876543210"
            }),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("reserved", res.json().get("error", "").lower())

