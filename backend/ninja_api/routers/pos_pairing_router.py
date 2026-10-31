from django.shortcuts import get_object_or_404
from ninja import Router
from asgiref.sync import async_to_sync

from apps.billing.pairing import (
    start_pairing_session,
    redeem_pairing_code,
    revoke_pairing_session,
    verify_mobile_token,
    resolve_and_record_scan,
)
from apps.billing.ws_hub import hub
from apps.billing.models import POSPairingSession
from ninja_api.auth import jwt_auth
from ninja_api.schemas import (
    StartPairingIn, StartPairingOut,
    RedeemPairingIn, RedeemPairingOut,
    RevokePairingIn, MobileScanIn
)

router = Router(tags=["POS Mobile Scanner Pairing Engine"])


@router.post("/pos-pairing/start/", response={201: StartPairingOut}, auth=jwt_auth)
@router.post("/pos/pairing/start/", response={201: StartPairingOut}, auth=jwt_auth, include_in_schema=False)
def start_pos_pairing_session(request, payload: StartPairingIn):
    """
    Laptop POS operator starts a 5-minute single-use pairing session to connect a smartphone scanner.
    """
    base_url = payload.base_url
    if not base_url:
        host = request.get_host()
        proto = "https" if request.is_secure() else "http"
        base_url = f"{proto}://{host}"

    data = start_pairing_session(request.auth, base_url)
    data['pairing_url'] = data.get('scanner_url')
    data['qr_code_base64'] = data.get('qr_data_url')
    return 201, data


@router.post("/pos-pairing/redeem/", response={200: RedeemPairingOut, 400: dict}, auth=None)
@router.post("/pos/pairing/redeem/", response={200: RedeemPairingOut, 400: dict}, auth=None, include_in_schema=False)
def redeem_pos_pairing_token(request, payload: RedeemPairingIn):
    """
    Mobile scanner device redeems the short-lived pairing code from the QR scan.
    """
    try:
        tenant = getattr(request, 'tenant', None)
        schema_name = payload.tenant_schema or (tenant.schema_name if tenant else None)
        res = redeem_pairing_code(
            payload.session_id,
            payload.pairing_code,
            payload.device_info or '',
            tenant_schema=schema_name
        )
        return 200, res
    except ValueError as e:
        return 400, {"error": str(e)}
    except Exception:
        return 400, {"error": "Failed to redeem pairing code."}


@router.post("/pos-pairing/revoke/", response={200: dict, 404: dict}, auth=jwt_auth)
@router.post("/pos/pairing/revoke/", response={200: dict, 404: dict}, auth=jwt_auth, include_in_schema=False)
def revoke_pos_pairing_token(request, payload: RevokePairingIn):
    """Revoke active phone scanner pairing from laptop screen."""
    success = revoke_pairing_session(payload.session_id, request.auth)
    if success:
        async_to_sync(hub.revoke_session)(payload.session_id)
        return 200, {"status": "revoked"}
    return 404, {"error": "Session not found or unauthorized"}


@router.post("/pos-pairing/scan-fallback/", response={200: dict, 400: dict, 401: dict, 404: dict}, auth=None)
@router.post("/pos/pairing/scan/", response={200: dict, 400: dict, 401: dict, 404: dict}, auth=None, include_in_schema=False)
def mobile_scan_fallback(request, payload: MobileScanIn):
    """
    HTTP POST fallback for mobile QR scans in case WebSocket is unavailable.
    """
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return 401, {"error": "Missing or invalid mobile authentication token"}

    token = auth_header.split(' ', 1)[1]
    claims = verify_mobile_token(token)
    if not claims:
        return 401, {"error": "Expired or invalid mobile session token"}

    session_id = claims.get('session_id')
    tenant_schema = claims.get('tenant_schema')

    from django_tenants.utils import schema_context
    def _execute_scan():
        session = POSPairingSession.objects.filter(session_id=session_id, is_active=True).first()
        if not session:
            return 404, {"error": "Pairing session is no longer active"}

        prod_data, error_msg, is_dup = resolve_and_record_scan(session, payload.event_id, payload.qr_payload)

        if is_dup:
            return 200, {"status": "duplicate", "event_id": payload.event_id}

        if not prod_data:
            return 404, {"error": error_msg}

        # Broadcast to laptop POS WebSocket
        if prod_data.get('is_tray'):
            async_to_sync(hub.broadcast_to_laptop)(session_id, {
                "type": "tray_scanned",
                "event_id": payload.event_id,
                "tray": prod_data,
                "timestamp": payload.timestamp,
            })
        else:
            async_to_sync(hub.broadcast_to_laptop)(session_id, {
                "type": "item_scanned",
                "event_id": payload.event_id,
                "product": prod_data,
                "timestamp": payload.timestamp,
            })

        return 200, {
            "status": "success",
            "event_id": payload.event_id,
            "product": prod_data,
        }

    if tenant_schema and tenant_schema != 'public':
        with schema_context(tenant_schema):
            return _execute_scan()
    return _execute_scan()
