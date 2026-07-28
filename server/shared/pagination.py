import base64
import json

from django.db.models import Q
from rest_framework.pagination import BasePagination, PageNumberPagination

from shared.responses import APIResponse


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for list views across all modules."""

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def get_paginated_response(self, data):
        return APIResponse(
            data={
                "count": self.page.paginator.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            },
            message="Data retrieved successfully.",
        )


class CursorPagination(BasePagination):
    """
    Cursor-based pagination for feed-style endpoints.

    Uses a (created_at, id) tuple encoded as base64.
    This ensures stable ordering even with concurrent writes.
    """

    page_size = 20
    max_page_size = 50
    cursor_query_param = "cursor"
    page_size_query_param = "page_size"
    ordering = "-created_at"
    ordering_fields = ["created_at", "id"]

    def __init__(self):
        self.cursor = None
        self.request = None
        self.queryset = None
        self.results = []
        self.has_next = False
        self.next_cursor_value = None

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginate the queryset using cursor-based navigation.
        """
        self.request = request
        self.queryset = queryset
        self.page_size = self.get_page_size(request)
        self.next_cursor_value = None

        cursor_string = request.query_params.get(self.cursor_query_param)
        self.cursor = self.decode_cursor(cursor_string) if cursor_string else None

        if self.cursor:
            created_at = self.cursor.get("created_at")
            obj_id = self.cursor.get("id")

            if created_at and obj_id:
                queryset = queryset.filter(
                    Q(created_at__lt=created_at)
                    | Q(created_at=created_at, id__lt=obj_id)
                )

        results_list = list(queryset[: self.page_size + 1])

        self.has_next = len(results_list) > self.page_size

        if self.has_next:
            self.results = results_list[: self.page_size]
            last_item = self.results[-1]
            self.next_cursor_value = self.encode_cursor(
                {
                    "created_at": last_item.created_at.isoformat(),
                    "id": str(last_item.id),
                }
            )
        else:
            self.results = results_list
            self.next_cursor_value = None

        return self.results

    def get_next_cursor(self):
        """Return the next cursor value."""
        return self.next_cursor_value

    def get_page_size(self, request):
        page_size = request.query_params.get(self.page_size_query_param)

        if page_size:
            try:
                page_size = int(page_size)
                return min(max(page_size, 1), self.max_page_size)
            except ValueError:
                pass

        return type(self).page_size

    def encode_cursor(self, cursor_dict):
        """
        Encode cursor dictionary to base64 string.
        """
        cursor_json = json.dumps(cursor_dict)
        return base64.b64encode(cursor_json.encode()).decode()

    def decode_cursor(self, cursor_string):
        """
        Decode base64 cursor string to dictionary.
        """
        try:
            cursor_json = base64.b64decode(cursor_string.encode()).decode()
            return json.loads(cursor_json)
        except (base64.binascii.Error, json.JSONDecodeError, UnicodeDecodeError):
            return None


class FeedCursorPagination(CursorPagination):
    """
    Feed-specific cursor pagination with larger page size.
    Used only by feed module.
    """

    page_size = 30
    max_page_size = 100


class StandardCursorPagination(CursorPagination):
    """
    Standard cursor pagination with default page size of 20.
    """

    page_size = 20
    max_page_size = 50
