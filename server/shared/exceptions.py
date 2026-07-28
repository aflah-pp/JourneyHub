import logging
from typing import Dict, Optional

from django.conf import settings
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

from shared.responses import APIResponse

logger = logging.getLogger(__name__)


class ServiceException(Exception):
    """Base exception for service layer errors."""

    def __init__(
        self,
        message: str,
        code: str = "SERVICE_ERROR",
        status_code: int = status.HTTP_400_BAD_REQUEST,
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


class BusinessRuleViolation(ServiceException):
    """Exception for business rule violations."""

    def __init__(
        self,
        message: str,
        code: str = "BUSINESS_RULE_VIOLATION",
    ):
        super().__init__(
            message,
            code,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


def custom_exception_handler(
    exc: Exception,
    context: Dict,
) -> Optional[Response]:
    """
    Convert all DRF exceptions into the project's standard APIResponse format.
    """
    response = exception_handler(exc, context)

    if response is not None:
        return _format_drf_exception_to_api_response(response)

    return _handle_unhandled_exception_to_api_response(exc)


def _format_drf_exception_to_api_response(response: Response) -> Response:
    """
    Convert DRF exception responses into clean APIResponse.

    Example output:

    {
        "status": "error",
        "message": "Account locked. Try again in 20 minutes.",
        "data": {
            "login": [
                "Account locked. Try again in 20 minutes."
            ]
        }
    }
    """

    data = response.data
    error_message = "An error occurred."
    error_fields = None

    if isinstance(data, dict):

        if "detail" in data:
            error_message = str(data["detail"])

        else:
            error_fields = {}

            for field, errors in data.items():

                if not isinstance(errors, list):
                    errors = [errors]

                cleaned_errors = [str(error) for error in errors]

                error_fields[field] = cleaned_errors

            if error_fields:
                first_field = next(iter(error_fields))
                error_message = error_fields[first_field][0]

    else:
        error_message = str(data)

    return APIResponse(
        data=error_fields,
        message=error_message,
        status_code=response.status_code,
        is_success=False,
    )


def _handle_unhandled_exception_to_api_response(exc: Exception) -> Response:
    """
    Handle exceptions that DRF does not process.
    """

    logger.exception(
        "Unhandled Exception",
        exc_info=exc,
    )

    if isinstance(exc, DjangoValidationError):

        if hasattr(exc, "message_dict"):

            error_fields = {
                field: (
                    [str(error) for error in errors]
                    if isinstance(errors, list)
                    else [str(errors)]
                )
                for field, errors in exc.message_dict.items()
            }

            first_field = next(iter(error_fields))
            error_message = error_fields[first_field][0]

            return APIResponse(
                data=error_fields,
                message=error_message,
                status_code=status.HTTP_400_BAD_REQUEST,
                is_success=False,
            )

        if hasattr(exc, "messages"):

            return APIResponse(
                data=None,
                message=exc.messages[0],
                status_code=status.HTTP_400_BAD_REQUEST,
                is_success=False,
            )

    if isinstance(exc, Http404):

        return APIResponse(
            data=None,
            message="The requested resource was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            is_success=False,
        )

    if isinstance(exc, ServiceException):

        return APIResponse(
            data=None,
            message=exc.message,
            status_code=exc.status_code,
            is_success=False,
        )

    if isinstance(exc, PermissionError):

        return APIResponse(
            data=None,
            message="You do not have permission to perform this action.",
            status_code=status.HTTP_403_FORBIDDEN,
            is_success=False,
        )

    error_message = "An unexpected server error occurred."

    if settings.DEBUG:
        error_message = str(exc)

    return APIResponse(
        data=None,
        message=error_message,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        is_success=False,
    )
