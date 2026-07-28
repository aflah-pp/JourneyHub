from django.core.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, serializers, status
from rest_framework.permissions import IsAuthenticated

from shared.pagination import StandardResultsSetPagination
from shared.permissions import IsModerator, IsReporterOrModerator
from shared.responses import APIResponse
from shared.throttles import ReportThrottle

from .models import ActivityLog, ReportedItem, ReportReason, ReportStatus
from .serializers import (
    ActivityLogSerializer,
    ReportCreateSerializer,
    ReportedItemSerializer,
    ReportResolveSerializer,
    ReportUpdateStatusSerializer,
)
from .service import ActivityLogService, ReportService


class ReportCreateView(generics.CreateAPIView):
    """
    Create a report against any model.
    POST /api/v1/reports/

    Request body:
    {
        "content_type": "journey",      # or "journeyupdate", "comment", "commentreply"
        "object_id": "uuid",
        "reason": "SPAM",
        "description": "optional extra info"
    }
    """

    serializer_class = ReportCreateSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ReportThrottle]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def perform_create(self, serializer):
        target = serializer.validated_data.get("_target")

        if not target:
            raise serializers.ValidationError("Target object not found.")

        report = ReportService.create_report(
            reporter=self.request.user,
            target=target,
            reason=serializer.validated_data["reason"],
            description=serializer.validated_data.get("description", ""),
            ip_address=self.request.META.get("REMOTE_ADDR"),
            user_agent=self.request.META.get("HTTP_USER_AGENT", ""),
        )
        serializer.instance = report

        ActivityLogService.log_activity(
            user=self.request.user,
            action_type=ActivityLog.ActionType.REPORT,
            target=target,
            ip_address=self.request.META.get("REMOTE_ADDR"),
            user_agent=self.request.META.get("HTTP_USER_AGENT", ""),
            request_path=self.request.path,
            request_method=self.request.method,
            metadata={
                "report_id": str(report.id),
                "reason": report.reason,
            },
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(
            data=ReportedItemSerializer(serializer.instance).data,
            message="Report submitted successfully.",
            status_code=status.HTTP_201_CREATED,
        )


class ReportListView(generics.ListAPIView):
    """
    List reports.
    GET /api/v1/reports/

    - Regular users see only their own reports.
    - Moderators (staff) see all reports.
    """

    serializer_class = ReportedItemSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated, IsReporterOrModerator]
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["status", "reason"]
    search_fields = ["description", "resolution_note"]
    ordering_fields = ["created_at", "status", "resolved_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        qs = ReportedItem.objects.select_related("reporter", "moderator")

        if user.is_staff:
            return qs

        return qs.filter(reporter=user)


class ReportDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or resolve a report.
    GET /api/v1/reports/{id}/
    PATCH /api/v1/reports/{id}/

    - Retrieve: users can see only their own reports; moderators see any.
    - Resolve: only moderators can update (resolve) reports.
    """

    serializer_class = ReportedItemSerializer
    permission_classes = [IsAuthenticated, IsReporterOrModerator]
    lookup_field = "id"

    def get_queryset(self):
        user = self.request.user
        qs = ReportedItem.objects.select_related("reporter", "moderator")

        if user.is_staff:
            return qs

        return qs.filter(reporter=user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse(
            data=serializer.data,
            message="Report retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        """
        Update (resolve) a report.
        Only moderators can resolve reports.
        """
        if not request.user.is_staff:
            raise PermissionDenied("Only moderators can resolve reports.")

        instance = self.get_object()

        data = request.data

        if "status" in data:
            status_value = data["status"]

            if status_value in [ReportStatus.RESOLVED, ReportStatus.DISMISSED]:

                resolve_serializer = ReportResolveSerializer(data=data)
                resolve_serializer.is_valid(raise_exception=True)

                report = ReportService.resolve_report(
                    report_id=instance.id,
                    moderator=request.user,
                    resolution_status=resolve_serializer.validated_data["status"],
                    resolution_note=resolve_serializer.validated_data.get("note", ""),
                )

                ActivityLogService.log_activity(
                    user=request.user,
                    action_type=ActivityLog.ActionType.RESOLVE,
                    target=report.target,
                    ip_address=request.META.get("REMOTE_ADDR"),
                    user_agent=request.META.get("HTTP_USER_AGENT", ""),
                    request_path=request.path,
                    request_method=request.method,
                    metadata={
                        "report_id": str(report.id),
                        "resolution_status": report.status,
                        "resolution_note": report.resolution_note,
                    },
                )

                serializer = self.get_serializer(report)
                return APIResponse(
                    data=serializer.data,
                    message="Report resolved successfully.",
                    status_code=status.HTTP_200_OK,
                )

            else:

                status_serializer = ReportUpdateStatusSerializer(data=data)
                status_serializer.is_valid(raise_exception=True)

                report = ReportService.update_report_status(
                    report_id=instance.id,
                    moderator=request.user,
                    new_status=status_serializer.validated_data["status"],
                    note=status_serializer.validated_data.get("note", ""),
                )

                serializer = self.get_serializer(report)
                return APIResponse(
                    data=serializer.data,
                    message="Report status updated successfully.",
                    status_code=status.HTTP_200_OK,
                )

        return APIResponse(
            message="Only 'status' field can be updated.",
            status_code=status.HTTP_400_BAD_REQUEST,
            is_success=False,
        )


class ReportStatsView(generics.RetrieveAPIView):
    """
    Get report statistics.
    GET /api/v1/reports/stats/
    Only moderators can access.
    """

    permission_classes = [IsAuthenticated, IsModerator]

    def get(self, request, *args, **kwargs):
        stats = {
            "total": ReportedItem.objects.count(),
            "pending": ReportedItem.objects.pending().count(),
            "under_review": ReportedItem.objects.under_review().count(),
            "resolved": ReportedItem.objects.resolved().count(),
            "dismissed": ReportedItem.objects.dismissed().count(),
            "by_reason": {},
        }

        for reason in ReportReason.values:
            stats["by_reason"][reason] = ReportedItem.objects.filter(
                reason=reason
            ).count()

        return APIResponse(
            data=stats,
            message="Report statistics retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )


class ActivityLogListView(generics.ListAPIView):
    """
    List activity logs.
    GET /api/v1/activity-logs/

    - Users see only their own logs.
    - Staff see all logs.
    """

    serializer_class = ActivityLogSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
    ]
    filterset_fields = ["action_type", "user"]
    search_fields = ["metadata", "user_agent", "request_path"]
    ordering_fields = ["created_at", "action_type"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        qs = ActivityLog.objects.select_related("user")

        if not user.is_staff:
            qs = qs.filter(user=user)

        return qs


class ActivityLogDetailView(generics.RetrieveAPIView):
    """
    Retrieve a specific activity log.
    GET /api/v1/activity-logs/{id}/

    Only the user who owns it or staff can view.
    """

    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        user = self.request.user
        qs = ActivityLog.objects.select_related("user")

        if not user.is_staff:
            qs = qs.filter(user=user)

        return qs

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse(
            data=serializer.data,
            message="Activity log retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )


class ActivityLogStatsView(generics.RetrieveAPIView):
    """
    Get activity log statistics for the authenticated user.
    GET /api/v1/activity-logs/stats/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        action_counts = {}
        for action in ActivityLog.ActionType.values:
            action_counts[action] = ActivityLog.objects.filter(
                user=user, action_type=action
            ).count()

        stats = {
            "total": ActivityLog.objects.filter(user=user).count(),
            "by_action": action_counts,
            "recent_actions": ActivityLogService.get_user_logs(user, limit=10),
        }

        recent_serializer = ActivityLogSerializer(stats["recent_actions"], many=True)
        stats["recent_actions"] = recent_serializer.data

        return APIResponse(
            data=stats,
            message="Activity statistics retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )
