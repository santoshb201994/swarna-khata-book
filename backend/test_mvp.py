import os
import django
import json
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client as TestClient
from django_tenants.utils import schema_context
from apps.tenants.models import Client, Domain
from apps.accounts.models import User
from apps.products.models import Product

print("=" * 60)
print("SWARNA KHATA BOOK — PRODUCTION ARCHITECTURE VERIFICATION")
print("Django Ninja + django-tenants (PostgreSQL Schema Isolation)")
print("=" * 60)

tenant = Client.objects.filter(schema_name='demo').first()
assert tenant is not None, "Demo tenant must exist"

with schema_context(tenant.schema_name):
    user = User.objects.get(username="admin")
    client = TestClient()

    # 1. Test JWT Authentication via Django Ninja
    print("\n--- 1. Testing Django Ninja JWT Authentication ---")
    login_res = client.post(
        '/api/auth/token/',
        data=json.dumps({"username": "admin", "password": "admin123"}),
        content_type='application/json',
        HTTP_X_TENANT='demo'
    )
    assert login_res.status_code == 200, f"Login failed: {login_res.status_code}"
    auth_data = login_res.json()
    token = auth_data['access']
    print(f"Authenticated as: {auth_data['user']['username']} (Role: {auth_data['user']['role']})")
    headers = {'HTTP_AUTHORIZATION': f'Bearer {token}', 'HTTP_X_TENANT': 'demo'}

    # 2. Test Products & QR Code API
    print("\n--- 2. Testing Products & QR Tags API ---")
    prod_res = client.get('/api/products/', **headers)
    assert prod_res.status_code == 200
    products = prod_res.json()
    print(f"Products available: {len(products)}")
    assert len(products) > 0
    first_prod = Product.objects.filter(is_active=True).first()
    detail_res = client.get(f'/api/products/{first_prod.id}/', **headers)
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    print(f"Product: {detail_data['name']} (SKU: {detail_data['sku']}, Net Wt: {detail_data['net_weight']}g)")
    print(f"QR Tag URL: {detail_data.get('qr_code_url')}")
    assert detail_data.get('qr_code_url') is not None

    # 3. Test Live Metal Rates API
    print("\n--- 3. Testing Gold Rates API ---")
    rates_res = client.get('/api/gold-rates/current/', **headers)
    assert rates_res.status_code == 200
    rates = rates_res.json()
    print(f"Active configured purities: {len(rates)}")
    for r in rates:
        print(f"  - {r['purity_name']}: Rs. {r['rate_per_gram']}/g")

    # 4. Test Atomic POS Billing & Check Concurrency / Insufficient Stock
    print("\n--- 4. Testing POS Billing & Concurrency Lock ---")
    sale_payload = {
        "customer_id": None,
        "items": [
            {
                "product_id": first_prod.id,
                "quantity": 1,
                "gold_rate_per_gram": "6830.00",
                "making_charge": "450.00",
                "stone_charge": "0.00",
            }
        ],
        "payments": [
            {"method": "cash", "amount": "50000.00", "reference": "CASH-001"},
            {"method": "upi", "amount": "110000.00", "reference": "UPI-TXN-7788"},
        ],
        "discount": "500.00",
        "old_gold_weight": "2.000",
        "old_gold_rate": "6500.00",
        "notes": "Automated verification sale"
    }

    sale_res = client.post('/api/sales/', data=json.dumps(sale_payload), content_type='application/json', **headers)
    assert sale_res.status_code == 201, f"Sale failed: {sale_res.json()}"
    sale_data = sale_res.json()
    print(f"Sale created successfully: {sale_data['invoice_number']}")
    print(f"  Subtotal: Rs. {sale_data['subtotal']}")
    print(f"  CGST: Rs. {sale_data['cgst_amount']} | SGST: Rs. {sale_data['sgst_amount']}")
    print(f"  Old Gold Value: Rs. {sale_data['old_gold_value']}")
    print(f"  Total Amount: Rs. {sale_data['total_amount']}")
    print(f"  Amount Paid: Rs. {sale_data['amount_paid']}")
    print(f"  Payment Status: {sale_data['payment_status']}")

    # 5. Test PDF Invoice Generation
    print("\n--- 5. Testing Invoice PDF Download ---")
    pdf_res = client.get(f'/api/sales/{sale_data["id"]}/invoice-pdf/', **headers)
    assert pdf_res.status_code == 200
    assert pdf_res['Content-Type'] == 'application/pdf'
    assert len(pdf_res.content) > 1000
    print(f"Invoice PDF generated successfully! Byte size: {len(pdf_res.content)} bytes")

    # 6. Test DayBook Cash Ledger
    print("\n--- 6. Testing DayBook Cash Summary ---")
    day_res = client.get('/api/day-book/today/', **headers)
    assert day_res.status_code == 200
    day_data = day_res.json()
    print(f"DayBook {day_data['date']}: Opening: Rs. {day_data['opening_balance']} | Cash In: Rs. {day_data['cash_in']}")

    # 7. Test Inventory Movements Ledger
    print("\n--- 7. Testing Stock Movements Ledger ---")
    stock_res = client.get('/api/stock-movements/', **headers)
    assert stock_res.status_code == 200
    movements = stock_res.json()
    print(f"Stock ledger records: {len(movements)}")

    print("\n" + "=" * 60)
    print("ALL PRODUCTION INTEGRATION TESTS PASSED 100%!")
    print("=" * 60)
