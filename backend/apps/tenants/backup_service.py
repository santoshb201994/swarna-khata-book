import os
import io
import json
import base64
import hashlib
import zipfile
import tempfile
import logging
from decimal import Decimal
from typing import Dict, Any, Optional
from datetime import datetime, date

from django.conf import settings
from django.utils import timezone
from django.db import transaction
from django_tenants.utils import schema_context, get_tenant_model

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

from apps.accounts.models import User, Branch
from apps.products.models import Product, Category, Purity
from apps.stock.models import StockMovement
from apps.billing.models import Sale, SaleItem, Payment, InvoiceSetting, Item
from apps.accounting.models import Customer, DayBook, GoldRate

logger = logging.getLogger(__name__)


def _get_encryption_key(passphrase: Optional[str] = None, salt: Optional[bytes] = None) -> tuple[bytes, bytes]:
    """
    Derives an AES-256 Fernet key from the provided passphrase or settings.SECRET_KEY.
    Returns: (key_bytes, salt_bytes)
    """
    raw_pass = passphrase or getattr(settings, 'BACKUP_ENCRYPTION_KEY', settings.SECRET_KEY)
    if salt is None:
        salt = os.urandom(16)
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    derived = base64.urlsafe_b64encode(kdf.derive(raw_pass.encode('utf-8')))
    return derived, salt


import uuid

class DecimalJsonEncoder(json.JSONEncoder):
    """Encodes Decimals, dates, datetimes, and UUIDs into serializable formats."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, uuid.UUID):
            return str(obj)
        return super().default(obj)


class TenantBackupService:
    """
    Generates cryptographically encrypted, tenant-isolated backup archives.
    Retains independent tenant snapshots for selective recovery without full cluster rewind.
    """

    @classmethod
    def create_encrypted_backup(
        cls,
        schema_name: str,
        passphrase: Optional[str] = None
    ) -> str:
        """
        Exports all tenant business tables into JSON datasets, signs checksums,
        and encrypts the archive using AES-256 Fernet.
        Returns the path to the encrypted (.skb_enc) backup file.
        """
        logger.info("BACKUP_INITIATED: schema='%s'", schema_name)
        tenant_model = get_tenant_model()
        tenant = tenant_model.objects.filter(schema_name=schema_name).first()
        if not tenant:
            raise ValueError(f"Tenant schema '{schema_name}' does not exist.")

        raw_zip_buffer = io.BytesIO()

        with schema_context(schema_name):
            backup_data: Dict[str, list] = {}

            # 1. Branches & Users
            backup_data['branches'] = list(Branch.objects.values())
            backup_data['users'] = list(
                User.objects.values(
                    'id', 'username', 'first_name', 'last_name', 'email', 'phone',
                    'role', 'branch_id', 'is_staff', 'is_active', 'date_joined'
                )
            )

            # 2. Master Catalog
            backup_data['categories'] = list(Category.objects.values())
            backup_data['purities'] = list(Purity.objects.values())
            backup_data['products'] = list(Product.objects.values())
            backup_data['billing_items'] = list(Item.objects.values())

            # 3. Stock Movements
            backup_data['stock_movements'] = list(StockMovement.objects.values())

            # 4. Invoices & Sales
            backup_data['invoice_settings'] = list(InvoiceSetting.objects.values())
            backup_data['sales'] = list(Sale.objects.values())
            backup_data['sale_items'] = list(SaleItem.objects.values())
            backup_data['payments'] = list(Payment.objects.values())

            # 5. Customers & Accounting
            backup_data['customers'] = list(Customer.objects.values())
            backup_data['daybook'] = list(DayBook.objects.values())
            backup_data['gold_rates'] = list(GoldRate.objects.values())

            # Checksums and table records
            checksums = {}
            for table_name, records in backup_data.items():
                content = json.dumps(records, cls=DecimalJsonEncoder, indent=2).encode('utf-8')
                checksums[table_name] = {
                    'count': len(records),
                    'sha256': hashlib.sha256(content).hexdigest()
                }

            manifest = {
                'schema_name': schema_name,
                'tenant_name': tenant.name,
                'backup_version': '2.0',
                'created_at': timezone.now().isoformat(),
                'checksums': checksums
            }

            with zipfile.ZipFile(raw_zip_buffer, 'w', compression=zipfile.ZIP_DEFLATED) as zip_arch:
                zip_arch.writestr('manifest.json', json.dumps(manifest, indent=2).encode('utf-8'))
                for table_name, records in backup_data.items():
                    zip_arch.writestr(
                        f'{table_name}.json',
                        json.dumps(records, cls=DecimalJsonEncoder, indent=2).encode('utf-8')
                    )

        raw_zip_bytes = raw_zip_buffer.getvalue()

        # Encrypt the raw zip bytes with salt-derived key
        key, salt = _get_encryption_key(passphrase=passphrase)
        fernet = Fernet(key)
        encrypted_payload = fernet.encrypt(raw_zip_bytes)

        # Store salt (16 bytes) + encrypted payload
        final_backup_file = tempfile.NamedTemporaryFile(suffix='.skb_enc', delete=False)
        final_backup_file.write(salt + encrypted_payload)
        final_backup_file.close()

        logger.info(
            "BACKUP_COMPLETED: schema='%s' output='%s' size=%d bytes",
            schema_name, final_backup_file.name, len(salt + encrypted_payload)
        )
        return final_backup_file.name


class TenantRestoreService:
    """
    Selective Tenant Restoration Engine.
    Enables selective restoration of an individual tenant into an existing or staging schema
    without affecting any other tenant in the Neon PostgreSQL cluster.
    """

    @classmethod
    def restore_tenant_backup(
        cls,
        encrypted_backup_path: str,
        target_schema_name: str,
        passphrase: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Decrypts an encrypted backup file, validates checksums, and restores tables
        inside an atomic database transaction.
        """
        logger.info("RESTORE_INITIATED: file='%s' target_schema='%s'", encrypted_backup_path, target_schema_name)
        if not os.path.exists(encrypted_backup_path):
            raise FileNotFoundError(f"Backup file not found at: {encrypted_backup_path}")

        with open(encrypted_backup_path, 'rb') as f:
            file_data = f.read()

        if len(file_data) < 17:
            raise ValueError("Corrupt or invalid backup file format.")

        salt = file_data[:16]
        encrypted_payload = file_data[16:]

        key, _ = _get_encryption_key(passphrase=passphrase, salt=salt)
        fernet = Fernet(key)

        try:
            decrypted_zip_bytes = fernet.decrypt(encrypted_payload)
        except Exception as exc:
            raise ValueError(f"Decryption failed: Invalid passphrase or corrupted backup file ({exc})")

        zip_buffer = io.BytesIO(decrypted_zip_bytes)
        restored_counts = {}

        with zipfile.ZipFile(zip_buffer, 'r') as zip_arch:
            manifest_data = json.loads(zip_arch.read('manifest.json').decode('utf-8'))
            expected_checksums = manifest_data.get('checksums', {})

            # Validate all checksums prior to database insertion
            for table_name, meta in expected_checksums.items():
                table_bytes = zip_arch.read(f'{table_name}.json')
                actual_sha = hashlib.sha256(table_bytes).hexdigest()
                if actual_sha != meta['sha256']:
                    raise ValueError(f"Checksum mismatch on {table_name}! Expected {meta['sha256']}, got {actual_sha}")

            # Execute transactional restoration inside target schema
            with schema_context(target_schema_name):
                with transaction.atomic():
                    # 1. Restore Categories
                    cat_data = json.loads(zip_arch.read('categories.json').decode('utf-8'))
                    for c in cat_data:
                        Category.objects.update_or_create(id=c['id'], defaults={'name': c['name']})
                    restored_counts['categories'] = len(cat_data)

                    # 2. Restore Purities
                    purity_data = json.loads(zip_arch.read('purities.json').decode('utf-8'))
                    for p in purity_data:
                        Purity.objects.update_or_create(
                            id=p['id'],
                            defaults={'name': p['name'], 'fineness': Decimal(str(p['fineness']))}
                        )
                    restored_counts['purities'] = len(purity_data)

                    # 3. Restore Branches
                    branch_data = json.loads(zip_arch.read('branches.json').decode('utf-8'))
                    for b in branch_data:
                        Branch.objects.update_or_create(
                            id=b['id'],
                            defaults={
                                'name': b['name'],
                                'address': b.get('address', ''),
                                'phone': b.get('phone', ''),
                                'gstin': b.get('gstin', ''),
                                'is_active': b.get('is_active', True)
                            }
                        )
                    restored_counts['branches'] = len(branch_data)

                    # 4. Restore Products
                    prod_data = json.loads(zip_arch.read('products.json').decode('utf-8'))
                    for pr in prod_data:
                        Product.objects.update_or_create(
                            id=pr['id'],
                            defaults={
                                'sku': pr['sku'],
                                'name': pr['name'],
                                'category_id': pr.get('category_id'),
                                'purity_id': pr.get('purity_id'),
                                'gross_weight': Decimal(str(pr['gross_weight'])),
                                'stone_weight': Decimal(str(pr.get('stone_weight', '0.000'))),
                                'other_weight': Decimal(str(pr.get('other_weight', '0.000'))),
                                'making_charge_type': pr.get('making_charge_type', 'per_gram'),
                                'making_charge_value': Decimal(str(pr.get('making_charge_value', '0.00'))),
                                'huid': pr.get('huid', ''),
                                'is_active': pr.get('is_active', True)
                            }
                        )
                    restored_counts['products'] = len(prod_data)

                    # 5. Restore Customers
                    cust_data = json.loads(zip_arch.read('customers.json').decode('utf-8'))
                    for cu in cust_data:
                        Customer.objects.update_or_create(
                            id=cu['id'],
                            defaults={
                                'name': cu['name'],
                                'phone': cu.get('phone', ''),
                                'email': cu.get('email', ''),
                                'address': cu.get('address', ''),
                                'pan': cu.get('pan', ''),
                                'aadhaar': cu.get('aadhaar', ''),
                                'credit_limit': Decimal(str(cu.get('credit_limit', '0.00'))),
                                'current_balance': Decimal(str(cu.get('current_balance', '0.00'))),
                                'is_active': cu.get('is_active', True)
                            }
                        )
                    restored_counts['customers'] = len(cust_data)

        logger.info(
            "RESTORE_COMPLETED: target_schema='%s' restored_counts=%s",
            target_schema_name, restored_counts
        )
        return {
            "target_schema": target_schema_name,
            "manifest": manifest_data,
            "restored_records": restored_counts,
            "status": "success",
            "restored_at": timezone.now().isoformat()
        }
