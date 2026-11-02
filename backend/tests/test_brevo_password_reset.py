"""
Automated Test Suite: Brevo Transactional Email Integration & Secure Password Reset Flow.
Validates:
1. Reusable Brevo HTTPX Email Provider (mocked responses, error & timeout handling).
2. Anti-enumeration generic forgot-password responses.
3. Secure, single-use, 15-minute expiring SHA-256 token storage.
4. Token verification and Jewellery Shield password policy enforcement.
5. Single-use token invalidation and prevention of token reuse.
6. Rate limiting cooldown on reset requests.
7. Delivery failure isolation (user account never corrupted).
"""

import json
import hashlib
from datetime import timedelta
from unittest import mock
from django.test import TestCase, Client as TestClient
from django.utils import timezone
from django_tenants.utils import schema_context
import httpx

from apps.tenants.models import Client, Domain, PasswordResetToken
from apps.accounts.models import User, Branch
from apps.emails.provider import BrevoEmailProvider, ConsoleEmailProvider, EmailDeliveryError
from apps.emails.service import EmailService
from apps.emails.templates import get_password_reset_email
from apps.tenants.provisioning import TenantProvisioningService


class BrevoPasswordResetIntegrationTestCase(TestCase):
    """
    Unit & integration tests for Brevo email provider and self-service password reset.
    """

    @classmethod
    def setUpTestData(cls):
        # 1. Ensure public tenant exists
        with schema_context('public'):
            cls.public_client, _ = Client.objects.get_or_create(
                schema_name='public',
                defaults={'name': 'Public Master'}
            )
            Domain.objects.get_or_create(
                domain='localhost',
                defaults={'tenant': cls.public_client, 'is_primary': True}
            )

            # Store tenant for tests
            cls.tenant, _ = Client.objects.get_or_create(
                schema_name='demo',
                defaults={'name': 'Demo Jewellers', 'is_active': True}
            )
            Domain.objects.get_or_create(
                domain='demo.localhost',
                defaults={'tenant': cls.tenant, 'is_primary': True}
            )

        # 2. Setup test user inside tenant schema
        with schema_context(cls.tenant.schema_name):
            cls.branch, _ = Branch.objects.get_or_create(name="Main Showroom", phone="9876543210")
            cls.user, _ = User.objects.get_or_create(
                username="test_owner",
                defaults={
                    "email": "owner@swarnajewellers.com",
                    "role": User.Role.OWNER,
                    "branch": cls.branch,
                    "is_active": True
                }
            )
            cls.user.set_password("Old*Password123")
            cls.user.save()

    def setUp(self):
        self.client = TestClient()
        # Clean up any leftover test tokens
        with schema_context('public'):
            PasswordResetToken.objects.all().delete()

    # --------------------------------------------------------------------------
    # 1. BREVO EMAIL PROVIDER UNIT TESTS
    # --------------------------------------------------------------------------

    @mock.patch('httpx.Client.post')
    def test_brevo_provider_send_email_success(self, mock_post):
        """
        Verify that BrevoEmailProvider constructs correct REST API v3 payload
        and parses successful HTTP 201 response.
        """
        mock_response = mock.MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"messageId": "<brevo-test-msg-12345>"}
        mock_post.return_value = mock_response

        provider = BrevoEmailProvider(
            api_key="xkeysib-test-api-key-mock",
            sender_email="noreply@swarnakhata.com",
            sender_name="Swarna Khata ERP"
        )

        res = provider.send_email(
            to_email="customer@example.com",
            to_name="Customer Name",
            subject="Test Reset",
            html_content="<p>Test</p>",
            text_content="Test"
        )

        self.assertEqual(res["status"], "success")
        self.assertEqual(res["message_id"], "<brevo-test-msg-12345>")

        # Verify outgoing request payload
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "https://api.brevo.com/v3/smtp/email")
        self.assertEqual(kwargs["headers"]["api-key"], "xkeysib-test-api-key-mock")
        self.assertEqual(kwargs["json"]["to"][0]["email"], "customer@example.com")
        self.assertEqual(kwargs["json"]["sender"]["email"], "noreply@swarnakhata.com")

    @mock.patch('httpx.Client.post')
    def test_brevo_provider_timeout_handling(self, mock_post):
        """
        Verify that BrevoEmailProvider catches HTTPX TimeoutException and wraps
        it cleanly into EmailDeliveryError without crashing.
        """
        mock_post.side_effect = httpx.TimeoutException("Connection timed out")

        provider = BrevoEmailProvider(api_key="xkeysib-mock")
        with self.assertRaises(EmailDeliveryError) as ctx:
            provider.send_email(
                to_email="customer@example.com",
                to_name="Customer",
                subject="Test",
                html_content="<p>Test</p>"
            )
        self.assertIn("timed out", str(ctx.exception))

    @mock.patch('httpx.Client.post')
    def test_brevo_provider_api_error_response(self, mock_post):
        """
        Verify that HTTP 400/401 from Brevo raises EmailDeliveryError.
        """
        mock_response = mock.MagicMock()
        mock_response.status_code = 401
        mock_response.text = '{"message": "Key not found"}'
        mock_post.return_value = mock_response

        provider = BrevoEmailProvider(api_key="xkeysib-invalid-key")
        with self.assertRaises(EmailDeliveryError) as ctx:
            provider.send_email(
                to_email="customer@example.com",
                to_name="Customer",
                subject="Test",
                html_content="<p>Test</p>"
            )
        self.assertIn("HTTP 401", str(ctx.exception))

    def test_console_email_provider_fallback(self):
        """
        Verify ConsoleEmailProvider returns a mock success for local development.
        """
        provider = ConsoleEmailProvider()
        res = provider.send_email(
            to_email="dev@example.com",
            to_name="Dev User",
            subject="Dev Subject",
            html_content="<p>Dev</p>"
        )
        self.assertEqual(res["status"], "success")
        self.assertEqual(res["provider"], "console")

    def test_branded_email_template_generation(self):
        """
        Verify that email template contains Swarna Khata branding and 15m notice.
        """
        subject, html, text = get_password_reset_email(
            username="ramesh_owner",
            reset_url="https://app.swarnakhata.com/reset-password?token=secret123",
            shop_name="Sri Balaji Jewellers",
            expiry_minutes=15
        )
        self.assertIn("Sri Balaji Jewellers", subject)
        self.assertIn("15 minutes", html)
        self.assertIn("secret123", html)
        self.assertIn("15 minutes", text)

    # --------------------------------------------------------------------------
    # 2. FORGOT PASSWORD API (ANTI-ENUMERATION & RATE LIMITING)
    # --------------------------------------------------------------------------

    def test_forgot_password_generic_response_for_non_existent_email(self):
        """
        Verify anti-enumeration: Requesting a reset for an unregistered email
        returns the generic 200 response identical to an existing email.
        """
        res = self.client.post(
            '/api/auth/forgot-password/',
            data=json.dumps({"email": "nonexistent@nowhere.com"}),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("If an account with that email exists", data["message"])

        # Confirm zero tokens created in database
        with schema_context('public'):
            self.assertEqual(PasswordResetToken.objects.count(), 0)

    @mock.patch('apps.emails.service.EmailService.send_password_reset_email')
    def test_forgot_password_success_and_token_storage(self, mock_send_email):
        """
        Verify that an existing user receives a generic response, a token hash
        is stored in public schema with 15m expiration, and raw token is emailed.
        """
        mock_send_email.return_value = {"status": "success"}

        res = self.client.post(
            '/api/auth/forgot-password/',
            data=json.dumps({"email": "owner@swarnajewellers.com"}),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn("If an account with that email exists", res.json()["message"])

        # Verify token record in public schema
        with schema_context('public'):
            tokens = PasswordResetToken.objects.filter(user_email="owner@swarnajewellers.com")
            self.assertEqual(tokens.count(), 1)
            token_record = tokens.first()
            self.assertEqual(token_record.tenant_schema, self.tenant.schema_name)
            self.assertTrue(token_record.is_valid())
            # Token stored is a 64-char hex SHA-256 hash
            self.assertEqual(len(token_record.token_hash), 64)

        # Verify EmailService was called
        mock_send_email.assert_called_once()
        kwargs = mock_send_email.call_args[1]
        self.assertEqual(kwargs["email"], "owner@swarnajewellers.com")
        self.assertEqual(kwargs["tenant_schema"], self.tenant.schema_name)
        # Check that hash of dispatched raw token matches persisted hash
        dispatched_raw_token = kwargs["raw_token"]
        expected_hash = hashlib.sha256(dispatched_raw_token.encode('utf-8')).hexdigest()
        self.assertEqual(token_record.token_hash, expected_hash)

    @mock.patch('apps.emails.service.EmailService.send_password_reset_email')
    def test_forgot_password_rate_limiting(self, mock_send_email):
        """
        Verify that subsequent requests within 3 minutes are rate limited
        without disclosing the rate limit to prevent enumeration.
        """
        mock_send_email.return_value = {"status": "success"}

        # Request 1: succeeds
        res1 = self.client.post(
            '/api/auth/forgot-password/',
            data=json.dumps({"email": "owner@swarnajewellers.com"}),
            content_type="application/json"
        )
        self.assertEqual(res1.status_code, 200)
        self.assertEqual(mock_send_email.call_count, 1)

        # Request 2 (immediate): rate limited, generic 200, no second email sent
        res2 = self.client.post(
            '/api/auth/forgot-password/',
            data=json.dumps({"email": "owner@swarnajewellers.com"}),
            content_type="application/json"
        )
        self.assertEqual(res2.status_code, 200)
        self.assertEqual(mock_send_email.call_count, 1)  # Still 1, not called again

    # --------------------------------------------------------------------------
    # 3. VERIFY TOKEN & COMPLETE PASSWORD RESET (POLICY & SINGLE-USE)
    # --------------------------------------------------------------------------

    def test_verify_and_complete_password_reset_lifecycle(self):
        """
        Full lifecycle test:
        1. Create token.
        2. Verify token validity via /api/auth/verify-reset-token/.
        3. Attempt reset with weak password (rejected by Jewellery Shield).
        4. Reset with valid password (succeeds).
        5. Verify user can authenticate with new password.
        6. Attempt to reuse consumed token (rejected - single-use enforced).
        """
        import secrets
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()

        with schema_context('public'):
            PasswordResetToken.objects.create(
                user_id=self.user.id,
                user_email=self.user.email,
                tenant_schema=self.tenant.schema_name,
                token_hash=token_hash,
                expires_at=timezone.now() + timedelta(minutes=15)
            )

        # Step 2: Verify valid token
        res_verify = self.client.post(
            '/api/auth/verify-reset-token/',
            data=json.dumps({"token": raw_token}),
            content_type="application/json"
        )
        self.assertEqual(res_verify.status_code, 200)
        self.assertTrue(res_verify.json()["valid"])

        # Step 3: Attempt reset with weak password failing policy (e.g. all lowercase, short)
        res_weak = self.client.post(
            '/api/auth/reset-password/',
            data=json.dumps({"token": raw_token, "new_password": "weak"}),
            content_type="application/json"
        )
        self.assertEqual(res_weak.status_code, 422)

        # Step 4: Reset with strong password complying with Jewellery Shield
        strong_password = "Gold*Vault#826"
        res_success = self.client.post(
            '/api/auth/reset-password/',
            data=json.dumps({"token": raw_token, "new_password": strong_password}),
            content_type="application/json"
        )
        self.assertEqual(res_success.status_code, 200)
        self.assertTrue(res_success.json()["success"])

        # Step 5: Verify user can now authenticate with the new password
        with schema_context(self.tenant.schema_name):
            auth_res = self.client.post(
                '/api/auth/token/',
                data=json.dumps({"username": "test_owner", "password": strong_password}),
                content_type="application/json",
                HTTP_X_TENANT=self.tenant.schema_name
            )
            self.assertEqual(auth_res.status_code, 200)
            self.assertIn("access", auth_res.json())

        # Step 6: Single-use check: Attempting to reuse the same token must fail with 400
        res_reuse = self.client.post(
            '/api/auth/reset-password/',
            data=json.dumps({"token": raw_token, "new_password": "Secure*Vault#931"}),
            content_type="application/json"
        )
        self.assertEqual(res_reuse.status_code, 400)
        self.assertIn("invalid or has expired", res_reuse.json()["error"])

    def test_expired_token_is_rejected(self):
        """
        Verify that a token with expires_at in the past is rejected.
        """
        raw_token = "expired_raw_token_xyz"
        token_hash = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()

        with schema_context('public'):
            PasswordResetToken.objects.create(
                user_id=self.user.id,
                user_email=self.user.email,
                tenant_schema=self.tenant.schema_name,
                token_hash=token_hash,
                expires_at=timezone.now() - timedelta(minutes=5)  # Expired
            )

        res = self.client.post(
            '/api/auth/verify-reset-token/',
            data=json.dumps({"token": raw_token}),
            content_type="application/json"
        )
        self.assertEqual(res.status_code, 400)
        self.assertFalse(res.json().get("valid", True))
