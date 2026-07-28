from rest_framework import status
from rest_framework.response import Response


class APIResponse(Response):
    """
    Standard API response.

    Success:
    {
        "status": "success",
        "message": "...",
        "data": {...}
    }

    Error:
    {
        "status": "error",
        "message": "...",
        "data": {...}
    }
    """

    def __init__(
        self,
        data=None,
        message="Success",
        status_code=status.HTTP_200_OK,
        is_success=True,
        headers=None,
        content_type=None,
        **kwargs,
    ):
        super().__init__(
            data={
                "status": "success" if is_success else "error",
                "message": message,
                "data": data,
            },
            status=status_code,
            headers=headers,
            content_type=content_type,
            **kwargs,
        )
