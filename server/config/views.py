from django.db import connection
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view

from shared.responses import APIResponse


@api_view(["GET"])
@extend_schema(tags="server status")
def server_status(request):
    system_status = {
        "database": "healthy",
    }

    try:
        connection.ensure_connection()
    except Exception:
        system_status["database"] = "unhealthy"
        return APIResponse(
            data=system_status,
            message="Database connection failure.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            is_success=False,
        )

    return APIResponse(
        data=system_status,
        message="All systems operational.",
        status_code=status.HTTP_200_OK,
        is_success=True,
    )
