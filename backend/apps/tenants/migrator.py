import logging
from typing import List, Dict, Any, Optional
from django.utils import timezone
from django.core.management import call_command
from django_tenants.utils import get_tenant_model, get_public_schema_name

logger = logging.getLogger(__name__)


class CanaryBatchMigrator:
    """
    Production-grade Tenant Migration Engine with Canary Validation & Failure Isolation.

    Pipeline:
    1. Public schema migration.
    2. Canary tenant validation (e.g. 'demo'). If canary fails, immediately halts.
    3. Batch migration of active production tenants.
    4. Per-tenant failure tracking and status recording.
    """

    @classmethod
    def run_migrations(
        cls,
        canary_schema: str = 'demo',
        batch_size: int = 5,
        interactive: bool = False
    ) -> Dict[str, Any]:
        tenant_model = get_tenant_model()
        public_schema = get_public_schema_name()

        results: Dict[str, Any] = {
            "public_success": False,
            "canary_success": False,
            "canary_schema": canary_schema,
            "total_tenants": 0,
            "migrated_tenants": [],
            "failed_tenants": [],
            "completed_at": None
        }

        # Step 1: Migrate Public Schema
        logger.info("MIGRATOR: Applying migrations to public schema...")
        try:
            call_command('migrate_schemas', schema_name=public_schema, interactive=interactive)
            results["public_success"] = True
            logger.info("MIGRATOR: Public schema migration complete.")
        except Exception as exc:
            logger.critical("MIGRATOR ERROR: Public schema migration failed: %s", exc, exc_info=True)
            results["public_error"] = str(exc)
            return results

        # Step 2: Canary Validation
        canary = tenant_model.objects.filter(schema_name=canary_schema, is_active=True).first()
        if canary:
            logger.info("MIGRATOR: Running canary migration validation on '%s'...", canary_schema)
            try:
                call_command('migrate_schemas', schema_name=canary_schema, interactive=interactive)
                canary.last_migrated_at = timezone.now()
                canary.last_migration_status = 'success'
                canary.save(update_fields=['last_migrated_at', 'last_migration_status'])
                results["canary_success"] = True
                logger.info("MIGRATOR: Canary validation PASSED for '%s'.", canary_schema)
            except Exception as exc:
                canary.last_migrated_at = timezone.now()
                canary.last_migration_status = 'failed'
                canary.save(update_fields=['last_migrated_at', 'last_migration_status'])
                results["canary_error"] = str(exc)
                logger.critical(
                    "MIGRATOR CANARY FAILURE: Aborting all production migrations! Error: %s",
                    exc, exc_info=True
                )
                return results
        else:
            logger.warning("MIGRATOR: Canary schema '%s' not found. Skipping canary pre-check.", canary_schema)
            results["canary_success"] = True

        # Step 3: Fetch remaining active tenants (excluding public and canary)
        tenants_to_migrate = list(
            tenant_model.objects
            .filter(is_active=True)
            .exclude(schema_name__in=[public_schema, canary_schema])
            .order_by('id')
        )
        results["total_tenants"] = len(tenants_to_migrate)

        # Step 4: Batch Migration Execution
        for i in range(0, len(tenants_to_migrate), batch_size):
            batch = tenants_to_migrate[i:i + batch_size]
            logger.info("MIGRATOR: Processing batch %d to %d...", i + 1, min(i + batch_size, len(tenants_to_migrate)))

            for t in batch:
                try:
                    logger.info("MIGRATOR: Migrating schema '%s' (Store: %s)...", t.schema_name, t.name)
                    call_command('migrate_schemas', schema_name=t.schema_name, interactive=interactive)
                    t.last_migrated_at = timezone.now()
                    t.last_migration_status = 'success'
                    t.save(update_fields=['last_migrated_at', 'last_migration_status'])
                    results["migrated_tenants"].append(t.schema_name)
                except Exception as exc:
                    logger.error("MIGRATOR: Migration failed for '%s': %s", t.schema_name, exc, exc_info=True)
                    t.last_migrated_at = timezone.now()
                    t.last_migration_status = 'failed'
                    t.save(update_fields=['last_migrated_at', 'last_migration_status'])
                    results["failed_tenants"].append({
                        "schema": t.schema_name,
                        "name": t.name,
                        "error": str(exc)
                    })

        results["completed_at"] = timezone.now().isoformat()
        logger.info(
            "MIGRATOR SUMMARY: Public: %s | Canary: %s | Total: %d | Succeeded: %d | Failed: %d",
            results["public_success"], results["canary_success"],
            results["total_tenants"], len(results["migrated_tenants"]), len(results["failed_tenants"])
        )
        return results
