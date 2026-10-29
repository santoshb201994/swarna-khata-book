import os
import django
import json
import uuid

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIClient
from apps.accounts.models import User, Branch
from apps.products.models import Product, Category, Purity
from apps.billing.models import POSPairingSession, ScannedItemAudit
from apps.billing.pairing import (
    start_pairing_session,
    redeem_pairing_code,
    revoke_pairing_session,
    verify_mobile_token,
    resolve_and_record_scan,
)

print("\n========================================================")
print("  Running Mobile QR Scanner & POS Sync Integration Tests")
print("========================================================")

client = APIClient()
user = User.objects.get(username="admin")
client.force_authenticate(user=user)

# 1. Test Pairing Start
print("\n--- 1. Testing Laptop POS Pairing Start ---")
start_res = client.post('/api/pos/pairing/start/', data={'base_url': 'http://192.168.1.50:5173'}, format='json')
assert start_res.status_code == 201, f"Pairing start failed: {start_res.data}"
pairing_data = start_res.data
assert 'session_id' in pairing_data
assert 'pairing_code' in pairing_data
assert 'qr_data_url' in pairing_data
assert pairing_data['qr_data_url'].startswith('data:image/png;base64,')
assert 'https://192.168.1.50:5173/scanner' in pairing_data['scanner_url']
print(f"Created pairing session: {pairing_data['session_id']}")
print(f"Generated QR Code Data URL length: {len(pairing_data['qr_data_url'])} characters")

session_id = pairing_data['session_id']
pairing_code = pairing_data['pairing_code']

# 2. Test Mobile Code Redemption (Public Endpoint)
print("\n--- 2. Testing Mobile Code Redemption ---")
mobile_client = APIClient()  # Unauthenticated phone
redeem_res = mobile_client.post('/api/pos/pairing/redeem/', data={
    'session_id': session_id,
    'pairing_code': pairing_code,
    'device_info': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)',
}, format='json')
assert redeem_res.status_code == 200, f"Redemption failed: {redeem_res.data}"
redeem_data = redeem_res.data
assert redeem_data['status'] == 'paired'
assert 'mobile_token' in redeem_data
mobile_token = redeem_data['mobile_token']

token_claims = verify_mobile_token(mobile_token)
assert token_claims is not None
assert token_claims['session_id'] == session_id
assert token_claims['role'] == 'mobile_scanner'
print(f"Redeemed code successfully! Mobile token issued for user: {redeem_data['user_name']}")

# 3. Test Single-Use Code Enforcement (Re-redemption must fail)
print("\n--- 3. Testing Single-Use Code Enforcement ---")
replay_res = mobile_client.post('/api/pos/pairing/redeem/', data={
    'session_id': session_id,
    'pairing_code': pairing_code,
}, format='json')
assert replay_res.status_code == 400, "Replay attack was not prevented!"
print(f"Re-redemption correctly rejected with error: {replay_res.data['error']}")

# 4. Test Invalid / Expired Code
print("\n--- 4. Testing Invalid Code Rejection ---")
fake_res = mobile_client.post('/api/pos/pairing/redeem/', data={
    'session_id': session_id,
    'pairing_code': 'FAKE_CODE_12345',
}, format='json')
assert fake_res.status_code == 400
print(f"Invalid code correctly rejected with error: {fake_res.data['error']}")

# 5. Test Real Inventory Item Resolution
print("\n--- 5. Testing QR Scan Inventory Resolution ---")
product = Product.objects.filter(is_active=True).first()
assert product is not None

# JSON QR payload as generated on physical jewelry tags
qr_json_payload = json.dumps({
    'id': product.id,
    'sku': product.sku,
    'name': product.name,
    'purity': product.purity.name,
    'gross_wt': str(product.gross_weight),
    'net_wt': str(product.net_weight),
    'huid': product.huid,
})

event_id_1 = str(uuid.uuid4())
scan_res = mobile_client.post(
    '/api/pos/pairing/scan/',
    data={'event_id': event_id_1, 'qr_payload': qr_json_payload, 'timestamp': 1700000000},
    format='json',
    HTTP_AUTHORIZATION=f'Bearer {mobile_token}'
)
assert scan_res.status_code == 200, f"Scan resolution failed: {scan_res.data}"
assert scan_res.data['status'] == 'success'
assert scan_res.data['product']['id'] == product.id
assert scan_res.data['product']['sku'] == product.sku
print(f"Scanned item resolved: {scan_res.data['product']['name']} ({scan_res.data['product']['sku']})")

# 6. Test Event Deduplication / Idempotency
print("\n--- 6. Testing Idempotent Event Deduplication ---")
dup_res = mobile_client.post(
    '/api/pos/pairing/scan/',
    data={'event_id': event_id_1, 'qr_payload': qr_json_payload},
    format='json',
    HTTP_AUTHORIZATION=f'Bearer {mobile_token}'
)
assert dup_res.status_code == 200
assert dup_res.data['status'] == 'duplicate'
print("Duplicate scan event suppressed successfully (no duplicate item entry).")

# 7. Test Raw SKU / HUID Scan String Fallback
print("\n--- 7. Testing Raw SKU / HUID String Scan ---")
event_id_2 = str(uuid.uuid4())
raw_res = mobile_client.post(
    '/api/pos/pairing/scan/',
    data={'event_id': event_id_2, 'qr_payload': product.sku},
    format='json',
    HTTP_AUTHORIZATION=f'Bearer {mobile_token}'
)
assert raw_res.status_code == 200
assert raw_res.data['product']['id'] == product.id
print(f"Raw SKU string successfully resolved: {product.sku}")

# 8. Test Unknown / Nonexistent Item
print("\n--- 8. Testing Unknown Item Rejection ---")
event_id_3 = str(uuid.uuid4())
unknown_res = mobile_client.post(
    '/api/pos/pairing/scan/',
    data={'event_id': event_id_3, 'qr_payload': 'NONEXISTENT-SKU-9999'},
    format='json',
    HTTP_AUTHORIZATION=f'Bearer {mobile_token}'
)
assert unknown_res.status_code == 404
print(f"Unknown item correctly rejected with message: {unknown_res.data['error']}")

# 9. Test Branch Isolation
print("\n--- 9. Testing Branch Isolation Security ---")
other_branch, _ = Branch.objects.get_or_create(
    name="Branch 2 Mall",
    defaults={'address': '45 Avenue', 'phone': '9876543299', 'gstin': '29ABCDE1234F1Z5'}
)
cat = Category.objects.first()
pur = Purity.objects.first()
foreign_product = Product.objects.create(
    name="Branch 2 Restricted Gold Bracelet",
    sku=f"BR2-TEST-{uuid.uuid4().hex[:6].upper()}",
    category=cat,
    purity=pur,
    gross_weight=10.0,
    is_active=True,
    branch=other_branch,
)

# Start a session for user bound to Main Showroom
main_branch, _ = Branch.objects.get_or_create(name="Main Showroom")
user.branch = main_branch
user.save()

branch_start = client.post('/api/pos/pairing/start/', data={}, format='json')
b_session_id = branch_start.data['session_id']
b_pairing_code = branch_start.data['pairing_code']

b_redeem = mobile_client.post('/api/pos/pairing/redeem/', data={
    'session_id': b_session_id,
    'pairing_code': b_pairing_code,
}, format='json')
b_mobile_token = b_redeem.data['mobile_token']

# Attempt to scan product belonging to other branch
event_id_4 = str(uuid.uuid4())
cross_branch_res = mobile_client.post(
    '/api/pos/pairing/scan/',
    data={'event_id': event_id_4, 'qr_payload': foreign_product.sku},
    format='json',
    HTTP_AUTHORIZATION=f'Bearer {b_mobile_token}'
)
assert cross_branch_res.status_code == 404
assert 'branch' in cross_branch_res.data['error'].lower()
print(f"Cross-branch scan correctly blocked: {cross_branch_res.data['error']}")

# 10. Test Laptop Revocation
print("\n--- 10. Testing Pairing Revocation by Laptop ---")
revoke_res = client.post('/api/pos/pairing/revoke/', data={'session_id': b_session_id}, format='json')
assert revoke_res.status_code == 200
assert revoke_res.data['status'] == 'revoked'

# Scan after revocation must fail
event_id_5 = str(uuid.uuid4())
post_revoke_res = mobile_client.post(
    '/api/pos/pairing/scan/',
    data={'event_id': event_id_5, 'qr_payload': product.sku},
    format='json',
    HTTP_AUTHORIZATION=f'Bearer {b_mobile_token}'
)
assert post_revoke_res.status_code == 404
print("Post-revocation scan correctly rejected.")

# Cleanup temporary foreign test product
foreign_product.delete()

print("\nALL MOBILE QR SCANNER & PAIRING INTEGRATION TESTS PASSED 100%!")
