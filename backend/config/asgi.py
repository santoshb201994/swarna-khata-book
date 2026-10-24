"""
ASGI config for swarna_khata_book project.

It exposes the ASGI callable as a module-level variable named `application`.
Enables high-concurrency async servers (Uvicorn, Daphne, Granian) alongside WSGI.
"""

import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Initialize Django ASGI application early to ensure the app registry is populated
django_http_app = get_asgi_application()

from apps.billing.websocket_handler import pos_websocket_app, mobile_websocket_app


async def application(scope, receive, send):
    """
    Unified ASGI router supporting HTTP (Django) and WebSockets (Mobile QR POS Sync).
    """
    scope_type = scope.get('type')
    if scope_type == 'websocket':
        path = scope.get('path', '')
        if path.startswith('/ws/pos') or path.startswith('/api/ws/pos'):
            await pos_websocket_app(scope, receive, send)
            return
        elif path.startswith('/ws/mobile') or path.startswith('/api/ws/mobile'):
            await mobile_websocket_app(scope, receive, send)
            return
        # Unknown websocket route
        await send({"type": "websocket.close", "code": 4404})
        return

    # HTTP / Lifespan requests
    await django_http_app(scope, receive, send)
