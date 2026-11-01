import uuid
import secrets
import json
import base64
import io
import socket
from datetime import timedelta
import jwt
from django.conf import settings
from django.utils import timezone
from django.db import transaction
import qrcode
from .models import POSPairingSession, ScannedItemAudit
from apps.products.models import Product
from apps.stock.models import StockSummary


PAIRING_TOKEN_LIFETIME_MINUTES = 15
MOBILE_TOKEN_LIFETIME_HOURS = 12


def get_lan_ip() -> str:
    """Detects the primary LAN IP address of this machine (e.g. 192.168.x.x)"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'


def generate_pairing_qr_data_url(url: str) -> str:
    """Generate a high-contrast base64 Data URL for a pairing URL"""
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=3,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0f172a", back_color="#ffffff")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode('utf-8')
    return f"data:image/png;base64,{encoded}"


def start_pairing_session(user, base_url: str = None) -> dict:
    """Creates a short-lived single-use pairing session for the authenticated POS laptop user"""
    session_id = str(uuid.uuid4())
    pairing_code = secrets.token_urlsafe(16)
    expires_at = timezone.now() + timedelta(minutes=PAIRING_TOKEN_LIFETIME_MINUTES)
    from django.db import connection
    current_schema = getattr(user, 'tenant_schema', None) or getattr(connection, 'schema_name', 'public')

    session = POSPairingSession.objects.create(
        session_id=session_id,
        pairing_code=pairing_code,
        user=user,
        branch=getattr(user, 'branch', None),
        expires_at=expires_at,
    )

    lan_ip = get_lan_ip()

    # If base_url contains localhost or 127.0.0.1, replace with the machine's actual Wi-Fi LAN IP
    # so mobile phones scanning the QR code reach the laptop over Wi-Fi instead of their own device!
    raw_base_url = (base_url or f"https://{lan_ip}:5173").rstrip('/')
    if 'localhost' in raw_base_url or '127.0.0.1' in raw_base_url:
        clean_base_url = raw_base_url.replace('localhost', lan_ip).replace('127.0.0.1', lan_ip)
    else:
        clean_base_url = raw_base_url

    # Ensure mobile scanner uses https so mobile browsers unlock camera access via secure context
    if clean_base_url.startswith('http://') and ':5173' in clean_base_url:
        clean_base_url = 'https://' + clean_base_url[len('http://'):]

    scanner_url = f"{clean_base_url}/scanner?session_id={session_id}&code={pairing_code}&tenant={current_schema}"
    qr_data_url = generate_pairing_qr_data_url(scanner_url)

    return {
        "session_id": session_id,
        "pairing_code": pairing_code,
        "scanner_url": scanner_url,
        "qr_data_url": qr_data_url,
        "detected_lan_ip": lan_ip,
        "tenant_schema": current_schema,
        "expires_at": expires_at.isoformat(),
        "expires_in_seconds": PAIRING_TOKEN_LIFETIME_MINUTES * 60,
        "branch_name": session.branch.name if session.branch else "Main Store",
    }


def redeem_pairing_code(session_id: str, pairing_code: str, device_info: str = "", tenant_schema: str = None) -> dict:
    """Atomically redeems a single-use pairing code and returns a scoped mobile session token"""
    from django_tenants.utils import schema_context
    from django.db import connection
    current_schema = tenant_schema or getattr(connection, 'schema_name', 'public')

    def _execute_redeem():
        with transaction.atomic():
            session = (
                POSPairingSession.objects.select_for_update()
                .filter(
                    session_id=session_id,
                    pairing_code=pairing_code,
                    is_active=True,
                    is_redeemed=False,
                    expires_at__gt=timezone.now(),
                )
                .first()
            )

            if not session:
                # Check if already redeemed
                already_redeemed = POSPairingSession.objects.filter(
                    session_id=session_id, pairing_code=pairing_code, is_redeemed=True
                ).exists()
                if already_redeemed:
                    raise ValueError("This pairing code has already been used.")
                raise ValueError("Invalid or expired pairing code.")

            # Consume code atomically on first redemption and extend session for 12 hours
            session.is_redeemed = True
            session.redeemed_at = timezone.now()
            session.expires_at = timezone.now() + timedelta(hours=MOBILE_TOKEN_LIFETIME_HOURS)
            session.mobile_device_info = (device_info or "Mobile Browser")[:255]
            session.save(update_fields=['is_redeemed', 'redeemed_at', 'expires_at', 'mobile_device_info'])

            # Issue scoped temporary mobile token
            exp = timezone.now() + timedelta(hours=MOBILE_TOKEN_LIFETIME_HOURS)
            payload = {
                "sub": f"mobile_scanner_{session.session_id}",
                "session_id": session.session_id,
                "user_id": session.user_id,
                "branch_id": session.branch_id,
                "role": "mobile_scanner",
                "tenant_schema": current_schema,
                "exp": int(exp.timestamp()),
                "iat": int(timezone.now().timestamp()),
            }
            jwt_secret = getattr(settings, 'JWT_SECRET_KEY', settings.SECRET_KEY)
            mobile_token = jwt.encode(payload, jwt_secret, algorithm="HS256")

            return {
                "status": "paired",
                "session_id": session.session_id,
                "mobile_token": mobile_token,
                "tenant_schema": current_schema,
                "user_name": session.user.get_full_name() or session.user.username,
                "branch_name": session.branch.name if session.branch else "Main Store",
                "expires_at": exp.isoformat(),
            }

    if tenant_schema and tenant_schema != 'public':
        with schema_context(tenant_schema):
            return _execute_redeem()
    return _execute_redeem()


def revoke_pairing_session(session_id: str, user) -> bool:
    """Revokes an active pairing session owned by the authenticated user"""
    session = POSPairingSession.objects.filter(session_id=session_id, user=user).first()
    if not session:
        return False
    session.is_active = False
    session.save(update_fields=['is_active'])
    return True


def verify_mobile_token(token: str) -> dict:
    """Verifies and decodes a mobile scanner JWT token"""
    try:
        jwt_secret = getattr(settings, 'JWT_SECRET_KEY', settings.SECRET_KEY)
        payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        if payload.get("role") != "mobile_scanner":
            return None
        return payload
    except Exception:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            if payload.get("role") != "mobile_scanner":
                return None
            return payload
        except Exception:
            return None


def resolve_and_record_scan(session: POSPairingSession, event_id: str, qr_payload: str) -> tuple[dict | None, str | None, bool]:
    """
    Validates scan event, deduplicates against event_id, resolves item against Product model,
    enforces branch permissions, records audit log, and returns (product_dict, error_message, is_duplicate).
    """
    # 1. Event deduplication check
    if ScannedItemAudit.objects.filter(event_id=event_id).exists():
        return None, "Event already processed (duplicate)", True

    if not session.is_active:
        return None, "Pairing session has been revoked or expired", False

    # 2. Parse QR payload
    target_id = None
    target_sku = None
    target_huid = None
    target_uuid = None
    data = None

    trimmed_payload = qr_payload.strip()
    if trimmed_payload.upper().startswith('SKB:'):
        candidate = trimmed_payload[4:].strip()
        try:
            target_uuid = uuid.UUID(candidate)
        except (ValueError, TypeError):
            target_sku = candidate
    else:
        try:
            target_uuid = uuid.UUID(trimmed_payload)
        except (ValueError, TypeError):
            pass

    if not target_uuid and not target_sku:
        try:
            data = json.loads(trimmed_payload)
            if isinstance(data, dict):
                target_id = data.get('id')
                target_sku = data.get('sku')
                target_huid = data.get('huid')
                if data.get('qr_token'):
                    try:
                        target_uuid = uuid.UUID(str(data.get('qr_token')))
                    except Exception:
                        pass
            else:
                target_sku = str(data)
        except (json.JSONDecodeError, ValueError):
            # Plain string payload (SKU or HUID)
            target_sku = trimmed_payload

    # 2b. Check if this is a Tray / Group QR code
    tray_obj = None
    if isinstance(data, dict) and (data.get('type') == 'tray' or data.get('tray_id') or (data.get('code') and str(data.get('code')).upper().startswith('TRAY-'))):
        from apps.qr_tags.models import Tray
        t_id = data.get('tray_id')
        t_code = data.get('code')
        if t_id:
            tray_obj = Tray.objects.filter(id=t_id).prefetch_related('items').first()
        if not tray_obj and t_code:
            tray_obj = Tray.objects.filter(code__iexact=t_code).prefetch_related('items').first()
    elif target_sku and target_sku.upper().startswith('TRAY-'):
        from apps.qr_tags.models import Tray
        tray_obj = Tray.objects.filter(code__iexact=target_sku).prefetch_related('items').first()

    if tray_obj:
        ScannedItemAudit.objects.create(
            event_id=event_id,
            session=session,
            product=None,
            qr_payload=qr_payload[:500],
            is_successful=True,
        )
        tray_items_data = []
        for p in tray_obj.items.filter(is_active=True).select_related('category', 'purity'):
            tray_items_data.append({
                "id": p.id,
                "name": p.name,
                "sku": p.sku,
                "category": p.category_id,
                "category_name": p.category.name if p.category else "Jewellery",
                "purity": p.purity_id,
                "purity_name": p.purity.name if p.purity else "22KT",
                "gross_weight": str(p.gross_weight),
                "stone_weight": str(p.stone_weight),
                "other_weight": str(p.other_weight),
                "net_weight": str(p.net_weight),
                "making_charge_type": p.making_charge_type,
                "making_charge_value": str(p.making_charge_value),
                "hsn_code": p.hsn_code,
                "huid": p.huid,
                "photo_url": p.photo.url if p.photo else None,
                "is_active": p.is_active,
                "in_stock": True,
                "quantity_on_hand": 1,
            })
        return {
            "is_tray": True,
            "tray_id": tray_obj.id,
            "tray_code": tray_obj.code,
            "tray_name": tray_obj.name,
            "total_items": len(tray_items_data),
            "items": tray_items_data,
        }, None, False

    # 3. Resolve Product in DB
    query = Product.objects.filter(is_active=True).select_related('category', 'purity', 'branch')
    product = None

    if target_uuid:
        from apps.billing.models import Item
        item_obj = (
            Item.objects.select_related('product', 'product__category', 'product__purity', 'product__branch')
            .filter(qr_token=target_uuid)
            .first()
        )
        if item_obj and item_obj.product and item_obj.product.is_active:
            product = item_obj.product

    if not product and target_id:
        product = query.filter(id=target_id).first()
    if not product and target_sku:
        product = query.filter(sku__iexact=target_sku).first()
    if not product and target_huid:
        product = query.filter(huid__iexact=target_huid).first()
    if not product and target_sku:
        # Fallback check if scanned string matches HUID
        product = query.filter(huid__iexact=target_sku).first()

    if not product:
        ScannedItemAudit.objects.create(
            event_id=event_id,
            session=session,
            product=None,
            qr_payload=qr_payload[:500],
            is_successful=False,
            error_message=f"Product not found for: {qr_payload[:100]}",
        )
        return None, f"Item not found in inventory ({target_sku or qr_payload[:30]})", False

    # 4. Enforce Branch Isolation
    if session.branch and product.branch and product.branch_id != session.branch_id:
        error = f"Item belongs to branch '{product.branch.name}', not your authorized branch."
        ScannedItemAudit.objects.create(
            event_id=event_id,
            session=session,
            product=product,
            qr_payload=qr_payload[:500],
            is_successful=False,
            error_message=error,
        )
        return None, error, False

    # 5. Stock availability check
    stock_summary = StockSummary.objects.filter(product=product).first()
    quantity_on_hand = stock_summary.quantity_on_hand if stock_summary else 1
    in_stock = quantity_on_hand > 0

    # 6. Record successful audit
    ScannedItemAudit.objects.create(
        event_id=event_id,
        session=session,
        product=product,
        qr_payload=qr_payload[:500],
        is_successful=True,
    )

    photo_url = None
    if product.photo:
        photo_url = product.photo.url

    product_data = {
        "id": product.id,
        "name": product.name,
        "sku": product.sku,
        "category": product.category_id,
        "category_name": product.category.name if product.category else "Jewellery",
        "purity": product.purity_id,
        "purity_name": product.purity.name if product.purity else "22KT",
        "gross_weight": str(product.gross_weight),
        "stone_weight": str(product.stone_weight),
        "other_weight": str(product.other_weight),
        "net_weight": str(product.net_weight),
        "making_charge_type": product.making_charge_type,
        "making_charge_value": str(product.making_charge_value),
        "hsn_code": product.hsn_code,
        "huid": product.huid,
        "photo_url": photo_url,
        "is_active": product.is_active,
        "in_stock": in_stock,
        "quantity_on_hand": quantity_on_hand,
    }

    return product_data, None, False
