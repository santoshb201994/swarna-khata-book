import time
from django.http import JsonResponse


async def health_check(request):
    """
    Asynchronous health check endpoint.
    Handles high-frequency health/liveness probes from Docker, Kubernetes,
    or reverse proxies without occupying synchronous worker threads.
    """
    db_status = "ok"
    try:
        # Use a simple raw async SQL query via asgiref
        from django.db import connection
        from asgiref.sync import sync_to_async

        @sync_to_async
        def _check_db():
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return cursor.fetchone()

        result = await _check_db()
        if result != (1,):
            db_status = "unhealthy: unexpected result from database ping"
    except Exception as exc:
        db_status = f"unhealthy: {str(exc)}"

    is_healthy = db_status == "ok"
    import os
    return JsonResponse(
        {
            "status": "healthy" if is_healthy else "degraded",
            "database": db_status,
            "timestamp": time.time(),
            "service": "swarna-khata-erp",
            "commit": os.getenv("RENDER_GIT_COMMIT", "dev")[:7],
        },
        status=200 if is_healthy else 503,
    )
