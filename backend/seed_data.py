import os
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django_tenants.utils import schema_context
from apps.tenants.models import Client, Domain
from apps.accounts.models import User, Branch
from apps.products.models import Category, Purity, Product
from apps.accounting.models import GoldRate, Customer
from apps.qr_tags.services import generate_qr_for_product
from apps.stock.services import record_stock_movement
from apps.stock.models import StockMovement

print("Seeding initial multi-tenant data...")

# 0. Ensure Public Tenant & Demo Tenant Exist
public_tenant = Client.objects.filter(schema_name='public').first()
if not public_tenant:
    public_tenant = Client(schema_name='public', name='Public Platform')
    public_tenant.auto_create_schema = False
    public_tenant.save()
    Domain.objects.create(domain='localhost', tenant=public_tenant, is_primary=True)
    print("Created public tenant.")

demo_tenant = Client.objects.filter(schema_name='demo').first()
if not demo_tenant:
    demo_tenant = Client(schema_name='demo', name='Swarna Jewellers Flagship')
    demo_tenant.save()
    Domain.objects.create(domain='demo.localhost', tenant=demo_tenant, is_primary=True)
    print("Created demo tenant (swarna jewellers).")

# Seed inside Demo Tenant Schema
with schema_context(demo_tenant.schema_name):
    # 1. Default Branch
    branch, _ = Branch.objects.get_or_create(
        name="Main Showroom",
        defaults={
            "address": "108 Jewel Bazaar, Gold Market",
            "phone": "+91 9876543210",
            "gstin": "29AABCU9603R1Z7"
        }
    )
    print(f"Branch: {branch.name}")

    # 2. Admin User
    admin_user, created = User.objects.get_or_create(
        username="admin",
        defaults={
            "email": "admin@swarnakhata.com",
            "first_name": "Store",
            "last_name": "Admin",
            "role": User.Role.OWNER,
            "branch": branch,
            "is_staff": True,
            "is_superuser": True,
        }
    )
    admin_user.set_password("admin123")
    admin_user.branch = branch
    admin_user.save()
    print("Configured admin user: admin / admin123")

    # 3. Purities
    purities = [
        ("24KT (999)", Decimal("0.999")),
        ("22KT (916)", Decimal("0.916")),
        ("18KT (750)", Decimal("0.750")),
        ("14KT (585)", Decimal("0.585")),
        ("Silver (925)", Decimal("0.925")),
    ]
    purity_objs = {}
    for name, fineness in purities:
        p, _ = Purity.objects.get_or_create(name=name, defaults={"fineness": fineness})
        purity_objs[name] = p
    print(f"Created/verified {len(purities)} purities.")

    # 4. Gold Rates (today's live rate)
    from django.utils import timezone
    today = timezone.localdate()
    default_rates = {
        "24KT (999)": Decimal("7450.00"),
        "22KT (916)": Decimal("6830.00"),
        "18KT (750)": Decimal("5590.00"),
        "14KT (585)": Decimal("4350.00"),
        "Silver (925)": Decimal("92.00"),
    }
    for pname, rate in default_rates.items():
        p = purity_objs.get(pname)
        if p:
            GoldRate.objects.get_or_create(
                purity=p,
                effective_date=today,
                branch=branch,
                defaults={"rate_per_gram": rate, "is_current": True, "entered_by": admin_user}
            )
    print("Configured live metal rates.")

    # 5. Categories
    categories = [
        "Necklace",
        "Bangles & Kadas",
        "Rings",
        "Earrings",
        "Chains",
        "Coins & Bars",
        "Mangalsutra",
    ]
    cat_objs = {}
    for c in categories:
        cat, _ = Category.objects.get_or_create(name=c)
        cat_objs[c] = cat
    print(f"Created/verified {len(categories)} categories.")

    # 6. Sample Initial Products with QR codes & initial stock
    sample_items = [
        {
            "name": "Classic Traditional Gold Necklace 22KT",
            "sku": "NCK-22K-001",
            "category": cat_objs["Necklace"],
            "purity": purity_objs["22KT (916)"],
            "gross_weight": Decimal("24.500"),
            "stone_weight": Decimal("1.200"),
            "other_weight": Decimal("0.000"),
            "making_charge_type": "per_gram",
            "making_charge_value": Decimal("450.00"),
            "huid": "HD916A01",
            "hsn_code": "7113",
        },
        {
            "name": "Floral Design Gold Ring 22KT",
            "sku": "RNG-22K-002",
            "category": cat_objs["Rings"],
            "purity": purity_objs["22KT (916)"],
            "gross_weight": Decimal("4.850"),
            "stone_weight": Decimal("0.350"),
            "other_weight": Decimal("0.000"),
            "making_charge_type": "per_gram",
            "making_charge_value": Decimal("500.00"),
            "huid": "HD916A02",
            "hsn_code": "7113",
        },
        {
            "name": "Solid Gold Kada 22KT",
            "sku": "BNG-22K-003",
            "category": cat_objs["Bangles & Kadas"],
            "purity": purity_objs["22KT (916)"],
            "gross_weight": Decimal("32.100"),
            "stone_weight": Decimal("0.000"),
            "other_weight": Decimal("0.000"),
            "making_charge_type": "per_gram",
            "making_charge_value": Decimal("400.00"),
            "huid": "HD916A03",
            "hsn_code": "7113",
        },
        {
            "name": "Diamond-Look Stud Earrings 18KT",
            "sku": "EAR-18K-004",
            "category": cat_objs["Earrings"],
            "purity": purity_objs["18KT (750)"],
            "gross_weight": Decimal("5.200"),
            "stone_weight": Decimal("0.800"),
            "other_weight": Decimal("0.000"),
            "making_charge_type": "fixed",
            "making_charge_value": Decimal("2500.00"),
            "huid": "HD750B01",
            "hsn_code": "7113",
        },
    ]

    for item_data in sample_items:
        sku = item_data.pop("sku")
        prod, created = Product.objects.get_or_create(
            sku=sku,
            defaults={**item_data, "branch": branch}
        )
        # Generate QR Code
        generate_qr_for_product(prod)
        # Initial stock IN
        if created:
            record_stock_movement(
                product=prod,
                movement_type=StockMovement.MovementType.IN,
                quantity=5,
                reference_type="initial_stock",
                note="Opening inventory count",
                user=admin_user,
                branch=branch,
            )

    # 7. Sample Customer
    Customer.objects.get_or_create(
        phone="9845012345",
        defaults={
            "name": "Ramesh Kumar Sharma",
            "email": "ramesh.sharma@example.com",
            "address": "42 MG Road, Bangalore",
            "pan_number": "ABCDE1234F"
        }
    )

print("Seed data completed successfully in demo tenant schema!")
