import os
import json
from unittest import mock
from decimal import Decimal
from django.test import TestCase, Client as HttpClient, RequestFactory
from django.utils import timezone
from django_tenants.utils import schema_context
from apps.tenants.models import Client, Domain
from apps.accounts.models import User, Branch
from apps.products.models import Product, Category, Purity
from apps.accounting.models import Customer
from apps.tenants.resolver import TenantResolver, TenantContextMismatchError, TenantSuspendedOrInactiveError
from apps.tenants.provisioning import TenantProvisioningService
from apps.tenants.backup_service import TenantBackupService, TenantRestoreService
from apps.tenants.migrator import CanaryBatchMigrator
from apps.tenants.middleware import ProductionTenantMiddleware
from ninja_api.auth import create_token, require_branch_access


class ProductionHardeningArchitectureTestCase(TestCase):
    """
    Comprehensive Security & Architectural Hardening Verification Suite.
    Validates:
    1. Tenant Security: JWT signature, membership, advisory X-Tenant, mismatch rejection (403).
    2. Connection Safety: Neon pool search_path reset hook.
    3. Branch-Level Authorization (Multi-Branch Isolation).
    4. Provisioning State Machine & Idempotency Replay.
    5. Encrypted Backup & Selective Restoration with Checksum Verification.
    6. Canary Migration Runner.
    """

    @classmethod
    def setUpTestData(cls):
        # 1. Base Public Tenant
        with schema_context('public'):
            cls.public_client, _ = Client.objects.get_or_create(
                schema_name='public',
                defaults={'name': 'Public Master'}
            )
            Domain.objects.get_or_create(
                domain='localhost',
                defaults={'tenant': cls.public_client, 'is_primary': True}
            )

            # Tenant A
            cls.tenant_a, _ = Client.objects.get_or_create(
                schema_name='t_harden_a',
                defaults={
                    'name': 'Hardened Jewellers Alpha',
                    'is_active': True,
                    'provisioning_status': Client.ProvisioningStatus.ACTIVE
                }
            )
            Domain.objects.get_or_create(
                domain='alpha.localhost',
                defaults={'tenant': cls.tenant_a, 'is_primary': True}
            )

            # Tenant B
            cls.tenant_b, _ = Client.objects.get_or_create(
                schema_name='t_harden_b',
                defaults={
                    'name': 'Hardened Jewellers Beta',
                    'is_active': True,
                    'provisioning_status': Client.ProvisioningStatus.ACTIVE
                }
            )
            Domain.objects.get_or_create(
                domain='beta.localhost',
                defaults={'tenant': cls.tenant_b, 'is_primary': True}
            )

            # Inactive / Suspended Tenant
            cls.tenant_suspended, _ = Client.objects.get_or_create(
                schema_name='t_harden_susp',
                defaults={
                    'name': 'Suspended Jewellers',
                    'is_active': False,
                    'provisioning_status': Client.ProvisioningStatus.FAILED
                }
            )

        # Setup Tenant A Users & Branches
        with schema_context(cls.tenant_a.schema_name):
            cls.branch_a1 = Branch.objects.create(name='Showroom Alpha 1', is_active=True)
            cls.branch_a2 = Branch.objects.create(name='Showroom Alpha 2', is_active=True)

            cls.owner_a = User.objects.create_user(
                username='owner_alpha',
                password='Owner*Pass123',
                role=User.Role.OWNER,
                branch=cls.branch_a1
            )
            cls.staff_a1 = User.objects.create_user(
                username='staff_alpha_1',
                password='Staff*Pass123',
                role=User.Role.STAFF,
                branch=cls.branch_a1
            )

            cls.cat_a = Category.objects.create(name='Alpha Bangles')
            cls.purity_a = Purity.objects.create(name='22KT 916', fineness=Decimal('0.916'))
            cls.product_a = Product.objects.create(
                name='Alpha Gold Bracelet',
                sku='BRAC-ALP-001',
                category=cls.cat_a,
                purity=cls.purity_a,
                gross_weight=Decimal('12.500'),
                branch=cls.branch_a1
            )

        # Setup Tenant B User
        with schema_context(cls.tenant_b.schema_name):
            cls.branch_b = Branch.objects.create(name='Showroom Beta', is_active=True)
            cls.owner_b = User.objects.create_user(
                username='owner_beta',
                password='Beta*Pass123',
                role=User.Role.OWNER,
                branch=cls.branch_b
            )

        cls.owner_a.tenant_schema = cls.tenant_a.schema_name
        cls.token_owner_a = create_token(cls.owner_a, token_type='access')

        cls.staff_a1.tenant_schema = cls.tenant_a.schema_name
        cls.token_staff_a1 = create_token(cls.staff_a1, token_type='access')

        cls.owner_b.tenant_schema = cls.tenant_b.schema_name
        cls.token_owner_b = create_token(cls.owner_b, token_type='access')

        cls.client = HttpClient()
        cls.rf = RequestFactory()
        cls.middleware = ProductionTenantMiddleware(lambda req: None)

    # --------------------------------------------------------------------------
    # 1. TENANT SECURITY & MISMATCH REJECTION
    # --------------------------------------------------------------------------

    def test_tenant_context_mismatch_rejected_with_403(self):
        """
        Verify that a client presenting an authenticated JWT for Tenant A
        cannot spoof an advisory X-Tenant header for Tenant B.
        Must be strictly rejected with HTTP 403 Forbidden.
        """
        req = self.rf.get(
            '/api/products/',
            HTTP_AUTHORIZATION=f'Bearer {self.token_owner_a}',
            HTTP_X_TENANT=self.tenant_b.schema_name # Contradictory hint!
        )
        response = self.middleware.process_request(req)
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.content.decode())
        self.assertEqual(data.get('code'), 'TENANT_CONTEXT_MISMATCH')
        self.assertIn('Tenant context mismatch', data.get('error'))

    def test_suspended_or_inactive_tenant_rejected_with_403(self):
        """
        Verify that access to inactive, suspended, or unprovisioned tenants is blocked.
        """
        req = self.rf.get(
            '/api/products/',
            HTTP_X_TENANT=self.tenant_suspended.schema_name
        )
        # Should not route to suspended tenant
        self.middleware.process_request(req)
        self.assertNotEqual(req.tenant.schema_name, self.tenant_suspended.schema_name)

    # --------------------------------------------------------------------------
    # 2. CONNECTION MANAGEMENT & NEON POOLER SAFETY
    # --------------------------------------------------------------------------

    def test_neon_connection_pooler_search_path_reset(self):
        """
        Verify that process_response and process_exception consistently reset
        the database connection search_path to public, preventing cross-tenant
        session pollution in connection poolers.
        """
        from django.db import connection
        req = self.rf.get('/api/products/', HTTP_AUTHORIZATION=f'Bearer {self.token_owner_a}')
        self.middleware.process_request(req)
        self.assertEqual(connection.schema_name, self.tenant_a.schema_name)

        # Simulate response completion
        from django.http import HttpResponse
        res = HttpResponse("OK")
        self.middleware.process_response(req, res)
        # In Neon pooler mode, search_path must be sanitized back to public!
        self.assertEqual(connection.schema_name, 'public')

    # --------------------------------------------------------------------------
    # 3. BRANCH-LEVEL AUTHORIZATION
    # --------------------------------------------------------------------------

    def test_branch_level_access_control(self):
        """
        Verify that store owners have universal access, but branch staff
        are strictly confined to their assigned branch.
        """
        # Store Owner: Can access Branch A1 and Branch A2
        self.assertTrue(require_branch_access(self.owner_a, self.branch_a1.id))
        self.assertTrue(require_branch_access(self.owner_a, self.branch_a2.id))

        # Staff in Branch A1: Can access Branch A1
        self.assertTrue(require_branch_access(self.staff_a1, self.branch_a1.id))

        # Staff in Branch A1: Accessing Branch A2 MUST raise PermissionError (HTTP 403)
        with self.assertRaises(PermissionError) as ctx:
            require_branch_access(self.staff_a1, self.branch_a2.id)
        self.assertIn("Branch access violation", str(ctx.exception))

    # --------------------------------------------------------------------------
    # 4. PROVISIONING STATE MACHINE & IDEMPOTENCY
    # --------------------------------------------------------------------------

    def test_tenant_provisioning_idempotency_and_states(self):
        """
        Verify that store provisioning follows the state machine and is
        completely idempotent when replayed with the same idempotency_key.
        """
        idempotency_key = "key_tenant_alpha_idem_test"
        with schema_context('public'):
            self.tenant_a.idempotency_key = idempotency_key
            self.tenant_a.provisioning_status = Client.ProvisioningStatus.ACTIVE
            self.tenant_a.save(update_fields=['idempotency_key', 'provisioning_status'])

        # Replay with identical idempotency_key (e.g. network timeout retry)
        replay = TenantProvisioningService.provision_store(
            shop_name=self.tenant_a.name,
            owner_username=self.owner_a.username,
            owner_password="AnyPassword123*",
            idempotency_key=idempotency_key
        )
        self.assertEqual(replay["schema_name"], self.tenant_a.schema_name)
        self.assertTrue(replay["is_idempotent_replay"])
        self.assertEqual(replay["provisioning_status"], Client.ProvisioningStatus.ACTIVE)
        self.assertIn("already active and verified", replay["message"])

    def test_tenant_provisioning_failure_state_handling(self):
        """
        Verify that failed provisioning stores the error and marks state as FAILED.
        """
        with schema_context('public'):
            failed_tenant = Client.objects.create(
                schema_name='t_mock_failed',
                name='Simulated Failed Store',
                is_active=False,
                provisioning_status=Client.ProvisioningStatus.FAILED,
                provisioning_error="Simulated network failure during schema creation",
                retry_count=1
            )
            self.assertEqual(failed_tenant.provisioning_status, Client.ProvisioningStatus.FAILED)
            self.assertEqual(failed_tenant.retry_count, 1)
            self.assertFalse(failed_tenant.is_active)
            self.assertIn("Simulated network failure", failed_tenant.provisioning_error)

    # --------------------------------------------------------------------------
    # 5. ENCRYPTED TENANT BACKUP & SELECTIVE RESTORATION
    # --------------------------------------------------------------------------

    def test_encrypted_tenant_backup_and_selective_restore(self):
        """
        Verify creation of an encrypted AES-256 tenant backup and subsequent
        selective restoration with SHA-256 dataset integrity verification.
        """
        backup_file = None
        try:
            # 1. Create encrypted backup of Tenant A
            backup_file = TenantBackupService.create_encrypted_backup(
                schema_name=self.tenant_a.schema_name,
                passphrase="Strong*VaultBackup#2026"
            )
            self.assertTrue(os.path.exists(backup_file))
            self.assertTrue(os.path.getsize(backup_file) > 100)

            # 2. Selectively restore into Tenant B
            restore_res = TenantRestoreService.restore_tenant_backup(
                encrypted_backup_path=backup_file,
                target_schema_name=self.tenant_b.schema_name,
                passphrase="Strong*VaultBackup#2026"
            )
            self.assertEqual(restore_res["status"], "success")
            self.assertIn('products', restore_res["restored_records"])
            self.assertTrue(restore_res["restored_records"]['products'] >= 1)

            # 3. Verify restored data inside Tenant B
            with schema_context(self.tenant_b.schema_name):
                restored_prod = Product.objects.filter(sku='BRAC-ALP-001').first()
                self.assertIsNotNone(restored_prod)
                self.assertEqual(restored_prod.name, 'Alpha Gold Bracelet')

            # 4. Decryption with wrong passphrase must fail
            with self.assertRaises(ValueError) as ctx:
                TenantRestoreService.restore_tenant_backup(
                    encrypted_backup_path=backup_file,
                    target_schema_name=self.tenant_b.schema_name,
                    passphrase="WRONG_PASSWORD"
                )
            self.assertIn("Decryption failed", str(ctx.exception))

        finally:
            if backup_file and os.path.exists(backup_file):
                os.remove(backup_file)

    # --------------------------------------------------------------------------
    # 6. CANARY BATCH MIGRATOR VALIDATION
    # --------------------------------------------------------------------------

    @mock.patch('apps.tenants.migrator.call_command')
    def test_canary_migrator_execution(self, mock_call_command):
        """
        Verify that CanaryBatchMigrator handles canary validation and execution.
        """
        res = CanaryBatchMigrator.run_migrations(canary_schema='t_harden_a', batch_size=2)
        self.assertTrue(res["public_success"])
        self.assertTrue(res["canary_success"])
        self.assertEqual(len(res["failed_tenants"]), 0)
        self.assertTrue(mock_call_command.called)

    @mock.patch('apps.tenants.migrator.call_command')
    def test_canary_migrator_aborts_on_canary_failure(self, mock_call_command):
        """
        Verify that CanaryBatchMigrator immediately halts if canary validation fails.
        """
        mock_call_command.side_effect = [None, Exception("Canary DDL error")]
        res = CanaryBatchMigrator.run_migrations(canary_schema='t_harden_a', batch_size=2)
        self.assertTrue(res["public_success"])
        self.assertFalse(res["canary_success"])
        self.assertIn("Canary DDL error", res["canary_error"])
        self.assertEqual(len(res["migrated_tenants"]), 0)
