import json
import urllib.parse
import logging
from asgiref.sync import sync_to_async
from django.conf import settings
try:
    from rest_framework_simplejwt.tokens import AccessToken
except ImportError:
    AccessToken = None
from .models import POSPairingSession
from .pairing import verify_mobile_token, resolve_and_record_scan
from .ws_hub import hub

logger = logging.getLogger("pos_sync")


def parse_query_string(query_string_bytes: bytes) -> dict[str, str]:
    query_str = query_string_bytes.decode('utf-8', errors='ignore')
    parsed = urllib.parse.parse_qs(query_str)
    return {k: v[0] for k, v in parsed.items()}


@sync_to_async
def get_active_session(session_id: str, tenant_schema: str = None):
    from django_tenants.utils import schema_context, get_tenant_model
    # 1. Targeted direct schema lookup (O(1))
    if tenant_schema and tenant_schema != 'public':
        try:
            with schema_context(tenant_schema):
                session = POSPairingSession.objects.filter(session_id=session_id, is_active=True).select_related('user', 'branch').first()
                if session:
                    return session
        except Exception:
            pass

    # 2. Try current active connection schema
    session = POSPairingSession.objects.filter(session_id=session_id, is_active=True).select_related('user', 'branch').first()
    if session:
        return session

    # 3. Graceful fallback search if tenant_schema was omitted
    try:
        tenant_model = get_tenant_model()
        for tenant in tenant_model.objects.exclude(schema_name='public'):
            with schema_context(tenant.schema_name):
                session = POSPairingSession.objects.filter(session_id=session_id, is_active=True).select_related('user', 'branch').first()
                if session:
                    return session
    except Exception:
        pass
    return None


@sync_to_async
def validate_jwt_user(token_str: str, user_id: int):
    # 1. Try SimpleJWT format
    try:
        token = AccessToken(token_str)
        token_user_id = token.payload.get('user_id')
        if str(token_user_id) == str(user_id):
            return True
    except Exception:
        pass

    # 2. Try Django Ninja / PyJWT format
    try:
        import jwt
        from django.conf import settings
        secret = getattr(settings, 'JWT_SECRET_KEY', settings.SECRET_KEY)
        payload = jwt.decode(token_str, secret, algorithms=['HS256'])
        token_user_id = payload.get('user_id')
        if str(token_user_id) == str(user_id):
            return True
    except Exception:
        pass

    return False



async def pos_websocket_app(scope, receive, send):
    """
    ASGI WebSocket endpoint for Laptop POS: /ws/pos/?session_id=...&token=...
    """
    params = parse_query_string(scope.get('query_string', b''))
    session_id = params.get('session_id')
    token = params.get('token')
    tenant_schema = params.get('tenant')

    if not session_id or not token:
        await send({"type": "websocket.close", "code": 4401})
        return

    if not tenant_schema and token:
        try:
            import jwt
            secret = getattr(settings, 'JWT_SECRET_KEY', settings.SECRET_KEY)
            tok_claims = jwt.decode(token, secret, algorithms=['HS256'], options={"verify_exp": False})
            tenant_schema = tok_claims.get('tenant_schema')
        except Exception:
            pass

    session = await get_active_session(session_id, tenant_schema=tenant_schema)
    if not session:
        await send({"type": "websocket.close", "code": 4404})
        return

    # Validate user auth
    is_valid_user = await validate_jwt_user(token, session.user_id)
    if not is_valid_user:
        await send({"type": "websocket.close", "code": 4403})
        return

    # Accept connection
    await send({"type": "websocket.accept"})

    async def send_json(data: dict):
        try:
            await send({"type": "websocket.send", "text": json.dumps(data)})
        except Exception as e:
            logger.warning(f"Error sending message to laptop: {e}")

    await hub.register_laptop(session_id, send_json)

    try:
        while True:
            msg = await receive()
            msg_type = msg.get("type")
            if msg_type == "websocket.receive":
                raw_text = msg.get("text", "")
                if not raw_text:
                    continue
                try:
                    data = json.loads(raw_text)
                    action = data.get("type")
                    if action == "ping":
                        await send_json({"type": "pong"})
                    elif action == "revoke":
                        session.is_active = False
                        await sync_to_async(session.save)(update_fields=['is_active'])
                        await hub.revoke_session(session_id)
                        await send_json({"type": "session_revoked"})
                except Exception as e:
                    logger.warning(f"Malformed laptop message: {e}")
            elif msg_type == "websocket.disconnect":
                break
    finally:
        await hub.unregister_laptop(session_id, send_json)


async def mobile_websocket_app(scope, receive, send):
    """
    ASGI WebSocket endpoint for Mobile Scanner: /ws/mobile/?session_id=...&token=...
    """
    params = parse_query_string(scope.get('query_string', b''))
    session_id = params.get('session_id')
    token = params.get('token')
    device_info = params.get('device_info', 'Mobile Browser')

    if not session_id or not token:
        await send({"type": "websocket.close", "code": 4401})
        return

    # Verify mobile token
    payload = verify_mobile_token(token)
    if not payload or payload.get("session_id") != session_id:
        await send({"type": "websocket.close", "code": 4403})
        return

    tenant_schema = params.get('tenant') or payload.get('tenant_schema')
    session = await get_active_session(session_id, tenant_schema=tenant_schema)
    if not session:
        await send({"type": "websocket.close", "code": 4404})
        return

    # Accept connection
    await send({"type": "websocket.accept"})

    async def send_json(data: dict):
        try:
            await send({"type": "websocket.send", "text": json.dumps(data)})
        except Exception as e:
            logger.warning(f"Error sending message to mobile: {e}")

    await hub.register_mobile(session_id, send_json, device_info)

    try:
        while True:
            msg = await receive()
            msg_type = msg.get("type")
            if msg_type == "websocket.receive":
                raw_text = msg.get("text", "")
                if not raw_text:
                    continue
                try:
                    data = json.loads(raw_text)
                    action = data.get("type")

                    if action == "ping":
                        await send_json({"type": "pong"})

                    elif action == "scan_event":
                        event_id = data.get("event_id")
                        qr_payload = data.get("qr_payload")
                        timestamp = data.get("timestamp")

                        if not event_id or not qr_payload:
                            await send_json({
                                "type": "scan_error",
                                "event_id": event_id,
                                "error": "Invalid scan event payload",
                            })
                            continue

                        # Payload size guard (max 4KB)
                        if len(qr_payload) > 4096:
                            await send_json({
                                "type": "scan_error",
                                "event_id": event_id,
                                "error": "Scan payload exceeds maximum allowable length",
                            })
                            continue

                        # Fast in-memory deduplication check
                        if hub.is_duplicate_event(session_id, event_id):
                            await send_json({
                                "type": "scan_ack",
                                "event_id": event_id,
                                "status": "duplicate",
                            })
                            continue

                        # Resolve against real inventory
                        prod_data, error_msg, is_dup = await sync_to_async(resolve_and_record_scan)(
                            session, event_id, qr_payload
                        )

                        if is_dup:
                            await send_json({
                                "type": "scan_ack",
                                "event_id": event_id,
                                "status": "duplicate",
                            })
                        elif prod_data:
                            # Push real-time to Laptop POS
                            await hub.broadcast_to_laptop(session_id, {
                                "type": "item_scanned",
                                "event_id": event_id,
                                "product": prod_data,
                                "timestamp": timestamp,
                            })
                            # Send success ack to phone
                            await send_json({
                                "type": "scan_ack",
                                "event_id": event_id,
                                "status": "success",
                                "item_name": prod_data["name"],
                                "sku": prod_data["sku"],
                                "purity": prod_data["purity_name"],
                                "net_weight": prod_data["net_weight"],
                            })
                        else:
                            # Not found or unauthorized
                            await send_json({
                                "type": "scan_error",
                                "event_id": event_id,
                                "error": error_msg,
                            })
                            # Send warning to laptop
                            await hub.broadcast_to_laptop(session_id, {
                                "type": "scan_warning",
                                "event_id": event_id,
                                "error": error_msg,
                            })
                except Exception as e:
                    logger.exception(f"Error processing mobile scan event: {e}")
                    await send_json({
                        "type": "scan_error",
                        "error": "Failed to process scan event",
                    })

            elif msg_type == "websocket.disconnect":
                break
    finally:
        await hub.unregister_mobile(session_id, send_json)
