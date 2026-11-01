import json
from django.core.management.base import BaseCommand
from apps.tenants.migrator import CanaryBatchMigrator


class Command(BaseCommand):
    help = "Execute safe, canary-validated, batch-based tenant migrations with failure tracking."

    def add_arguments(self, parser):
        parser.add_argument(
            '--canary',
            type=str,
            default='demo',
            help='Canary tenant schema to validate first before production tenants (default: demo).'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=5,
            help='Number of tenants to process in each migration batch (default: 5).'
        )

    def handle(self, *args, **options):
        canary = options['canary']
        batch_size = options['batch_size']

        self.stdout.write(self.style.NOTICE(
            f"Starting Canary Batch Migration (Canary: {canary}, Batch size: {batch_size})..."
        ))

        results = CanaryBatchMigrator.run_migrations(
            canary_schema=canary,
            batch_size=batch_size,
            interactive=False
        )

        if not results.get('public_success'):
            self.stdout.write(self.style.ERROR(f"Public migration failed: {results.get('public_error')}"))
            return

        if not results.get('canary_success'):
            self.stdout.write(self.style.ERROR(
                f"Canary validation on '{canary}' FAILED: {results.get('canary_error')}. All production migrations halted."
            ))
            return

        failed = results.get('failed_tenants', [])
        migrated = results.get('migrated_tenants', [])

        if failed:
            self.stdout.write(self.style.WARNING(
                f"Migrations completed with failures: {len(migrated)} succeeded, {len(failed)} failed."
            ))
            for f in failed:
                self.stdout.write(self.style.ERROR(f" - {f['schema']}: {f['error']}"))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"All tenant migrations completed successfully ({len(migrated)} tenants migrated)."
            ))
