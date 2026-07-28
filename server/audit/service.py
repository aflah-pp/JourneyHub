from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from accounts.models import User

from .models import ActivityLog, ReportedItem, ReportStatus


class ReportService:
    """Handles creation and moderation of reports."""

    MAX_REPORTS_PER_DAY = 10

    @staticmethod
    @transaction.atomic
    def create_report(
        reporter: User,
        target,
        reason: str,
        description: str = "",
        ip_address: str = None,
        user_agent: str = "",
    ) -> ReportedItem:
        """
        Create a new report for a given target object.
        Per SRS: rate-limited: max 10 reports/user/day.
        """

        today = timezone.now().date()
        daily_reports = ReportedItem.objects.filter(
            reporter=reporter,
            created_at__date=today,
        ).count()

        if daily_reports >= ReportService.MAX_REPORTS_PER_DAY:
            raise ValidationError(
                f"Rate limit exceeded. You can only submit {ReportService.MAX_REPORTS_PER_DAY} reports per day."
            )

        content_type = ContentType.objects.get_for_model(target)
        existing_report = ReportedItem.objects.filter(
            reporter=reporter,
            content_type=content_type,
            object_id=target.pk,
            status__in=[ReportStatus.PENDING, ReportStatus.UNDER_REVIEW],
        ).exists()

        if existing_report:
            raise ValidationError({"report": "You have already reported this item."})

        report = ReportedItem.objects.create(
            reporter=reporter,
            content_type=content_type,
            object_id=target.pk,
            reason=reason,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        return report

    @staticmethod
    @transaction.atomic
    def resolve_report(
        report_id: str,
        moderator: User,
        resolution_status: str,
        resolution_note: str = "",
    ) -> ReportedItem:
        """
        Resolve a report (either RESOLVED or DISMISSED).
        """
        try:
            report = ReportedItem.objects.select_related("reporter").get(id=report_id)
        except ReportedItem.DoesNotExist:
            raise ValidationError("Report not found.")

        if report.status in [ReportStatus.RESOLVED, ReportStatus.DISMISSED]:
            raise ValidationError("This report is already resolved.")

        if resolution_status not in [ReportStatus.RESOLVED, ReportStatus.DISMISSED]:
            raise ValidationError("Invalid resolution status.")

        report.resolve(moderator, resolution_status, resolution_note)
        return report

    @staticmethod
    @transaction.atomic
    def update_report_status(
        report_id: str,
        moderator: User,
        new_status: str,
        note: str = "",
    ) -> ReportedItem:
        """
        Update report status (for under_review, needs_info).
        """
        try:
            report = ReportedItem.objects.get(id=report_id)
        except ReportedItem.DoesNotExist:
            raise ValidationError("Report not found.")

        if report.status in [ReportStatus.RESOLVED, ReportStatus.DISMISSED]:
            raise ValidationError("Cannot update status of resolved report.")

        valid_transitions = [ReportStatus.UNDER_REVIEW, ReportStatus.NEEDS_INFO]
        if new_status not in valid_transitions:
            raise ValidationError(f"Status must be one of: {valid_transitions}")

        report.update_status(new_status)

        if not report.moderator:
            report.moderator = moderator
            report.save(update_fields=["moderator"])

        return report

    @staticmethod
    def get_pending_reports():
        """Return all pending reports with related data."""
        return ReportedItem.objects.pending().select_related("reporter", "moderator")

    @staticmethod
    def get_reports_by_status(status):
        """Get reports filtered by status."""
        return ReportedItem.objects.filter(status=status).select_related(
            "reporter", "moderator"
        )


class ActivityLogService:
    """Handles logging of user actions."""

    @staticmethod
    @transaction.atomic
    def log_activity(
        user,
        action_type: str,
        target=None,
        ip_address=None,
        user_agent=None,
        request_path=None,
        request_method=None,
        metadata=None,
    ) -> ActivityLog:
        """
        Create an immutable activity log entry.
        """
        content_type = None
        object_id = None

        if target:
            content_type = ContentType.objects.get_for_model(target)
            object_id = target.pk

        return ActivityLog.objects.create(
            user=user,
            action_type=action_type,
            content_type=content_type,
            object_id=object_id,
            ip_address=ip_address,
            user_agent=user_agent,
            request_path=request_path,
            request_method=request_method,
            metadata=metadata or {},
        )

    @staticmethod
    def get_user_logs(user, limit=50):
        """Get recent activity logs for a user."""
        return ActivityLog.objects.for_user(user)[:limit]

    @staticmethod
    def get_action_logs(action_type, limit=50):
        """Get recent activity logs by action type."""
        return ActivityLog.objects.for_action(action_type)[:limit]
