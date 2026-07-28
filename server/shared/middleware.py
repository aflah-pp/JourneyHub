from threading import local

from django.conf import settings
from django.template.response import TemplateResponse

from shared.responses import APIResponse

_thread_locals = local()


def get_current_request():
    return getattr(_thread_locals, "request", None)


class RequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        _thread_locals.request = request
        return self.get_response(request)


class EnforceStandardResponseMiddleware:
    """
    Middleware that enforces architectural standards for API responses.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if isinstance(response, TemplateResponse):
            return response

        if (
            not settings.DEBUG
            or not request.path.startswith("/api/")
            or request.path.startswith("/api/schema/")
            or request.path.startswith("/api/docs/")
            or request.path.startswith("/api/swagger/")
            or request.path.startswith("/api/redoc/")
        ):
            return response

        if isinstance(response, APIResponse):
            return response

        if hasattr(response, "data") and isinstance(response.data, dict):
            data = response.data
            required_keys = {"status", "message", "data"}
            if required_keys.issubset(data.keys()):
                return response

            if "error" in data:
                error_data = data.get("error", {})
                if isinstance(error_data, dict):
                    message = error_data.get("message", "An error occurred")
                    fields = error_data.get("fields", {})
                else:
                    message = str(error_data)
                    fields = {}

                return APIResponse(
                    data=fields if fields else None,
                    message=message,
                    status_code=response.status_code,
                    is_success=False,
                )

            return APIResponse(
                data=data,
                message="Request processed successfully.",
                status_code=response.status_code,
                is_success=response.status_code < 400,
            )

        return response
