import time
from django.http import JsonResponse
from django.db import connection
from asgiref.sync import sync_to_async


async def health_check(request):
    """
    Asynchronous health check endpoint.
    Handles high-frequency health/liveness probes from Docker, Kubernetes,
    or reverse proxies without occupying synchronous worker threads.
    """
    db_status = "ok"
    try:
        # Non-blocking async check on db connection
        await sync_to_async(connection.ensure_connection)()
    except Exception as exc:
        db_status = f"unhealthy: {str(exc)}"

    is_healthy = db_status == "ok"
    return JsonResponse(
        {
            "status": "healthy" if is_healthy else "degraded",
            "database": db_status,
            "timestamp": time.time(),
            "service": "swarna-khata-erp",
        },
        status=200 if is_healthy else 503,
    )
