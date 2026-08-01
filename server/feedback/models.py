from django.db import models
from django.utils import timezone

from accounts.models import User
from shared.models import TimeStampMixin, UUIDPrimaryKeyMixin


class FeedbackStatus(models.TextChoices):
    NEW = "NEW", "New"
    REVIEWING = "REVIEWING", "Reviewing"
    RESOLVED = "RESOLVED", "Resolved"
    CLOSED = "CLOSED", "Closed"


class FeedbackType(models.TextChoices):
    BUG = "BUG", "Bug Report"
    FEATURE = "FEATURE", "Feature Request"
    IMPROVEMENT = "IMPROVEMENT", "Improvement"
    GENERAL = "GENERAL", "General Feedback"
    OTHER = "OTHER", "Other"


class Feedback(UUIDPrimaryKeyMixin, TimeStampMixin):
    """
    User feedback model with Telegram integration.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="feedbacks",
        db_index=True,
    )
    feedback_type = models.CharField(
        max_length=30,
        choices=FeedbackType.choices,
        default=FeedbackType.GENERAL,
        db_index=True,
    )
    subject = models.CharField(max_length=200)
    message = models.TextField()
    rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Rating from 1 to 5",
    )
    status = models.CharField(
        max_length=20,
        choices=FeedbackStatus.choices,
        default=FeedbackStatus.NEW,
        db_index=True,
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_feedbacks",
    )
    resolution_note = models.TextField(blank=True)
    is_anonymous = models.BooleanField(
        default=False,
        help_text="If true, hides user identity from public view",
    )
    admin_notes = models.TextField(blank=True)

    class Meta:
        db_table = "feedbacks"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["feedback_type"]),
            models.Index(fields=["-created_at"]),
        ]
        verbose_name = "Feedback"
        verbose_name_plural = "Feedbacks"

    def __str__(self):
        return f"{self.subject} - {self.user.username}"

    def resolve(self, resolved_by, resolution_note=""):
        """Mark feedback as resolved."""
        self.status = FeedbackStatus.RESOLVED
        self.resolved_at = timezone.now()
        self.resolved_by = resolved_by
        if resolution_note:
            self.resolution_note = resolution_note
        self.save(
            update_fields=["status", "resolved_at", "resolved_by", "resolution_note"]
        )

    @property
    def display_username(self):
        """Return username or 'Anonymous' if is_anonymous is True."""
        return "Anonymous" if self.is_anonymous else self.user.username
