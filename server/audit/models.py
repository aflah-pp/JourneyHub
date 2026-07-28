from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from accounts.models import User
from shared.models import TimeStampMixin, UUIDPrimaryKeyMixin


class ReportStatus(models.TextChoices):
    """Status of a report."""

    PENDING = "PENDING", "Pending"
    UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
    RESOLVED = "RESOLVED", "Resolved"
    DISMISSED = "DISMISSED", "Dismissed"
    NEEDS_INFO = "NEEDS_INFO", "Needs More Info"


class ReportReason(models.TextChoices):
    """Reasons for reporting content."""

    SPAM = "SPAM", "Spam"
    HARASSMENT = "HARASSMENT", "Harassment"
    INAPPROPRIATE = "INAPPROPRIATE", "Inappropriate Content"
    COPYRIGHT = "COPYRIGHT", "Copyright Infringement"
    PRIVACY = "PRIVACY", "Privacy Violation"
    OTHER = "OTHER", "Other"


class ReportedItemManager(models.Manager):
    """Custom manager for ReportedItem with common filters."""

    def get_queryset(self):
        return super().get_queryset().select_related("reporter", "moderator")

    def pending(self):
        return self.get_queryset().filter(status=ReportStatus.PENDING)

    def under_review(self):
        return self.get_queryset().filter(status=ReportStatus.UNDER_REVIEW)

    def resolved(self):
        return self.get_queryset().filter(status=ReportStatus.RESOLVED)

    def dismissed(self):
        return self.get_queryset().filter(status=ReportStatus.DISMISSED)

    def for_target(self, target):
        """Return all reports for a specific target object."""
        content_type = ContentType.objects.get_for_model(target)
        return self.get_queryset().filter(
            content_type=content_type, object_id=target.pk
        )

    def by_reporter(self, user):
        """Return all reports by a specific reporter."""
        return self.get_queryset().filter(reporter=user)


class ReportedItem(UUIDPrimaryKeyMixin, TimeStampMixin):
    """
    Tracks user reports against any model (Journey, Update, Comment, Reply).
    Per SRS: polymorphic report target.
    """

    reporter = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="reports_made",
        db_index=True,
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={
            "model__in": ["journey", "journeyupdate", "comment", "commentreply"]
        },
    )
    object_id = models.UUIDField()
    target = GenericForeignKey("content_type", "object_id")

    reason = models.CharField(
        max_length=30,
        choices=ReportReason.choices,
        db_index=True,
    )
    description = models.TextField(
        blank=True,
        help_text="Additional details from the reporter",
    )

    status = models.CharField(
        max_length=20,
        choices=ReportStatus.choices,
        default=ReportStatus.PENDING,
        db_index=True,
    )

    moderator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="moderated_reports",
        db_index=True,
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
    )
    resolution_note = models.TextField(
        blank=True,
        help_text="Moderator's note on the resolution",
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the reporter",
    )
    user_agent = models.CharField(
        max_length=255,
        blank=True,
        help_text="User agent of the reporter",
    )

    objects = ReportedItemManager()

    class Meta:
        db_table = "reported_items"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["status"]),
            models.Index(fields=["reporter"]),
            models.Index(fields=["-created_at"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["reporter", "status"]),
        ]
        verbose_name = "Reported Item"
        verbose_name_plural = "Reported Items"

    def __str__(self):
        return f"Report #{str(self.id)[:8]} by {self.reporter.username} on {self.content_type.model}"

    def resolve(self, moderator, resolution_status, note=""):
        """
        Resolve a report (either RESOLVED or DISMISSED).
        Per SRS: status pipeline.
        """
        if self.status in [ReportStatus.RESOLVED, ReportStatus.DISMISSED]:
            raise ValueError("This report is already resolved.")

        if resolution_status not in [ReportStatus.RESOLVED, ReportStatus.DISMISSED]:
            raise ValueError("Resolution status must be RESOLVED or DISMISSED.")

        self.status = resolution_status
        self.moderator = moderator
        self.resolved_at = timezone.now()
        self.resolution_note = note
        self.save(
            update_fields=["status", "moderator", "resolved_at", "resolution_note"]
        )

    def update_status(self, new_status):
        """Update report status (for under_review, needs_info)."""
        if self.status in [ReportStatus.RESOLVED, ReportStatus.DISMISSED]:
            raise ValueError("Cannot update status of resolved report.")

        valid_transitions = [ReportStatus.UNDER_REVIEW, ReportStatus.NEEDS_INFO]
        if new_status not in valid_transitions:
            raise ValueError(f"Status must be one of: {valid_transitions}")

        self.status = new_status
        self.save(update_fields=["status"])


class ActivityLogManager(models.Manager):
    """Custom manager for ActivityLog."""

    def get_queryset(self):
        return super().get_queryset().select_related("user")

    def for_user(self, user):
        return self.get_queryset().filter(user=user)

    def for_action(self, action_type):
        return self.get_queryset().filter(action_type=action_type)


class ActivityLog(UUIDPrimaryKeyMixin, TimeStampMixin):
    """
    Immutable log of user actions for auditing.
    Per SRS: audit logs for auth events, moderation actions, report resolutions.
    """

    class ActionType(models.TextChoices):

        LOGIN = "LOGIN", "Login"
        LOGOUT = "LOGOUT", "Logout"
        REGISTER = "REGISTER", "Register"
        VERIFY_EMAIL = "VERIFY_EMAIL", "Verify Email"
        PASSWORD_RESET = "PASSWORD_RESET", "Password Reset"
        PASSWORD_CHANGE = "PASSWORD_CHANGE", "Password Change"

        CREATE = "CREATE", "Create"
        UPDATE = "UPDATE", "Update"
        DELETE = "DELETE", "Delete"
        VIEW = "VIEW", "View"

        LIKE = "LIKE", "Like"
        UNLIKE = "UNLIKE", "Unlike"
        COMMENT = "COMMENT", "Comment"
        REPLY = "REPLY", "Reply"

        FOLLOW = "FOLLOW", "Follow"
        UNFOLLOW = "UNFOLLOW", "Unfollow"
        SAVE = "SAVE", "Save"
        UNSAVE = "UNSAVE", "Unsave"

        REPORT = "REPORT", "Report"
        RESOLVE = "RESOLVE", "Resolve"
        SUSPEND = "SUSPEND", "Suspend"
        UNSUSPEND = "UNSUSPEND", "Unsuspend"
        BAN = "BAN", "Ban"
        UNBAN = "UNBAN", "Unban"

        ACCEPT = "ACCEPT", "Accept"
        REJECT = "REJECT", "Reject"

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="activity_logs",
        db_index=True,
    )
    action_type = models.CharField(
        max_length=30,
        choices=ActionType.choices,
        db_index=True,
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    object_id = models.UUIDField(null=True, blank=True)
    target = GenericForeignKey("content_type", "object_id")

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )
    user_agent = models.CharField(
        max_length=255,
        blank=True,
    )
    request_path = models.CharField(
        max_length=255,
        blank=True,
    )
    request_method = models.CharField(
        max_length=10,
        blank=True,
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional context as JSON",
    )

    objects = ActivityLogManager()

    class Meta:
        db_table = "activity_logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["action_type"]),
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["user", "action_type"]),
        ]
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"

    def __str__(self):
        return f"{self.user} {self.action_type} at {self.created_at}"

    def save(self, *args, **kwargs):
        """Make ActivityLog entries immutable."""
        if self.pk is not None:

            if ActivityLog.objects.filter(pk=self.pk).exists():
                raise ValueError(
                    "ActivityLog entries are immutable and cannot be updated."
                )
        super().save(*args, **kwargs)
