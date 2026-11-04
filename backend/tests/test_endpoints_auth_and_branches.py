import json
from django.test import TestCase, Client as TestClient
from django_tenants.utils import schema_context
from apps.tenants.models import Client, Domain
from apps.accounts.models import User, Branch
from ninja_api.auth import create_token


class EndpointsAuthAndBranchesTestCase(TestCase):
    """
    Integration tests covering auth & branch management endpoints:
    - POST /api/auth/change-password/
    - GET /api/branches/
    - POST /api/branches/
    - GET /api/branches/{branch_id}/
    - PUT /api/branches/{branch_id}/
    - GET /api/users/
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
            cls.tenant = Client.objects.exclude(schema_name='public').first()
            if not cls.tenant:
                cls.tenant = Client(schema_name='demo', name='Demo Jewellers', is_active=True)
                cls.tenant.auto_create_schema = False
                cls.tenant.save()
                Domain.objects.get_or_create(domain='demo.localhost', defaults={'tenant': cls.tenant, 'is_primary': True})

        with schema_context(cls.tenant.schema_name):
            cls.branch = Branch.objects.create(
                name="Main Showroom",
                address="100 Sarafa Bazar, Gadag",
                phone="9449642640",
                gstin="29ADNPP6515B1ZF",
                is_active=True
            )
            cls.owner = User.objects.create_user(
                username="branch_owner",
                password="Owner*Vault9",
                role=User.Role.OWNER,
                branch=cls.branch
            )
            cls.staff = User.objects.create_user(
                username="branch_staff",
                password="Worker*Vault8",
                role=User.Role.STAFF,
                branch=cls.branch
            )

    def setUp(self):
        self.client = TestClient()
        with schema_context(self.tenant.schema_name):
            self.owner.tenant_schema = self.tenant.schema_name
            self.staff.tenant_schema = self.tenant.schema_name
            self.owner_token = create_token(self.owner, token_type='access')
            self.staff_token = create_token(self.staff, token_type='access')

    def test_change_password_success(self):
        res = self.client.post(
            '/api/auth/change-password/',
            data=json.dumps({
                "current_password": "Worker*Vault8",
                "new_password": "New*Worker#Key7"
            }),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
            HTTP_X_TENANT=self.tenant.schema_name
        )
        self.assertEqual(res.status_code, 200)
        with schema_context(self.tenant.schema_name):
            updated_staff = User.objects.get(id=self.staff.id)
            self.assertTrue(updated_staff.check_password("New*Worker#Key7"))

    def test_change_password_invalid_current_password(self):
        with schema_context(self.tenant.schema_name):
            res = self.client.post(
                '/api/auth/change-password/',
                data=json.dumps({
                    "current_password": "WrongPassword@123",
                    "new_password": "New*Worker#Key7"
                }),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(res.status_code, 400)
            self.assertIn("Incorrect", res.json().get("error", ""))

    def test_change_password_violates_jewellery_shield_policy(self):
        with schema_context(self.tenant.schema_name):
            res = self.client.post(
                '/api/auth/change-password/',
                data=json.dumps({
                    "current_password": "Worker*Vault8",
                    "new_password": "short"
                }),
                content_type='application/json',
                HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertIn(res.status_code, [400, 422])

    def test_list_branches_authenticated(self):
        res = self.client.get(
            '/api/branches/',
            HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
            HTTP_X_TENANT=self.tenant.schema_name
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreaterEqual(len(data), 1)
        self.assertEqual(data[0]['name'], "Main Showroom")

    def test_create_branch_owner_success(self):
        payload = {
            "name": "Branch 2 Mall Showroom",
            "address": "42 MG Road, Bangalore",
            "phone": "9845012345",
            "gstin": "29ABCDE1234F1Z5",
            "is_active": True
        }
        res = self.client.post(
            '/api/branches/',
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
            HTTP_X_TENANT=self.tenant.schema_name
        )
        self.assertEqual(res.status_code, 201)
        data = res.json()
        self.assertEqual(data['name'], "Branch 2 Mall Showroom")
        with schema_context(self.tenant.schema_name):
            self.assertTrue(Branch.objects.filter(name="Branch 2 Mall Showroom").exists())

    def test_create_branch_forbidden_for_staff(self):
        payload = {
            "name": "Unauthorized Branch",
            "phone": "9845012345"
        }
        res = self.client.post(
            '/api/branches/',
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
            HTTP_X_TENANT=self.tenant.schema_name
        )
        self.assertEqual(res.status_code, 403)

    def test_get_branch_detail(self):
        res = self.client.get(
            f'/api/branches/{self.branch.id}/',
            HTTP_AUTHORIZATION=f'Bearer {self.staff_token}',
            HTTP_X_TENANT=self.tenant.schema_name
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['name'], self.branch.name)

    def test_update_branch_detail(self):
        payload = {
            "name": "Main Showroom Renovated",
            "address": "100 Old Sarafa Bazar, Gadag",
            "phone": "9449642640",
            "gstin": "29ADNPP6515B1ZF",
            "is_active": True
        }
        res = self.client.put(
            f'/api/branches/{self.branch.id}/',
            data=json.dumps(payload),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
            HTTP_X_TENANT=self.tenant.schema_name
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()['name'], "Main Showroom Renovated")
        with schema_context(self.tenant.schema_name):
            updated_branch = Branch.objects.get(id=self.branch.id)
            self.assertEqual(updated_branch.name, "Main Showroom Renovated")

    def test_list_users_in_tenant(self):
        res = self.client.get(
            '/api/users/',
            HTTP_AUTHORIZATION=f'Bearer {self.owner_token}',
            HTTP_X_TENANT=self.tenant.schema_name
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        usernames = [u['username'] for u in data]
        self.assertIn("branch_owner", usernames)
        self.assertIn("branch_staff", usernames)
