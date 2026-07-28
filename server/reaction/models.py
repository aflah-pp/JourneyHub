from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from accounts.models import User
from shared.models import TimeStampMixin, UUIDPrimaryKeyMixin

from .manager import CommentManager, CommentReplyManager


class Like(UUIDPrimaryKeyMixin, TimeStampMixin):
    """
    Represents a "like" on a JourneyUpdate.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="journey_update_likes",
        db_index=True,
    )
    journey_update = models.ForeignKey(
        "journey.JourneyUpdate",
        on_delete=models.CASCADE,
        related_name="likes",
        db_index=True,
    )

    class Meta:
        db_table = "likes"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "journey_update"],
                name="unique_like_per_user",
            )
        ]
        indexes = [
            models.Index(fields=["journey_update"]),
            models.Index(fields=["user"]),
            models.Index(fields=["journey_update", "-created_at"]),
            models.Index(fields=["user", "journey_update"]),
        ]
        verbose_name = "Like"
        verbose_name_plural = "Likes"

    def __str__(self):
        return f"{self.user} liked {self.journey_update}"


class Comment(UUIDPrimaryKeyMixin, TimeStampMixin):
    """
    Comment on a journey update.
    Unified comment model - this is the ONLY comment model.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="journey_comments",
        db_index=True,
    )
    journey_update = models.ForeignKey(
        "journey.JourneyUpdate",
        on_delete=models.CASCADE,
        related_name="comments",
        db_index=True,
    )
    content = models.TextField(max_length=1000)

    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="deleted_comments",
    )

    objects = CommentManager()
    all_objects = models.Manager()

    class Meta:
        db_table = "comments"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["journey_update"]),
            models.Index(fields=["user"]),
            models.Index(fields=["is_deleted"]),
            models.Index(fields=["journey_update", "is_deleted"]),
            models.Index(fields=["journey_update", "-created_at"]),
        ]
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return f"Comment by {self.user} on {self.journey_update}"

    def soft_delete(self, deleted_by):
        """Soft delete the comment."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = deleted_by
        self.save(update_fields=["is_deleted", "deleted_at", "deleted_by"])


class CommentReply(UUIDPrimaryKeyMixin, TimeStampMixin):
    """
    Reply to a comment (one level deep per SRS).
    """

    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="replies",
        db_index=True,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comment_replies",
        db_index=True,
    )
    content = models.TextField(max_length=1000)

    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="deleted_comment_replies",
    )

    objects = CommentReplyManager()
    all_objects = models.Manager()

    class Meta:
        db_table = "comment_replies"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["comment"]),
            models.Index(fields=["user"]),
            models.Index(fields=["is_deleted"]),
            models.Index(fields=["comment", "is_deleted"]),
            models.Index(fields=["comment", "-created_at"]),
        ]
        verbose_name = "Comment Reply"
        verbose_name_plural = "Comment Replies"

    def __str__(self):
        return f"Reply by {self.user} on comment {self.comment.id}"

    def soft_delete(self, deleted_by):
        """Soft delete the reply."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = deleted_by
        self.save(update_fields=["is_deleted", "deleted_at", "deleted_by"])


class AcceptedSolution(UUIDPrimaryKeyMixin, TimeStampMixin):
    """
    Accepted solution for a journey update (per SRS).
    """

    journey_update = models.OneToOneField(
        "journey.JourneyUpdate",
        on_delete=models.CASCADE,
        related_name="accepted_solution",
        db_index=True,
    )
    comment = models.OneToOneField(
        Comment,
        on_delete=models.CASCADE,
        related_name="accepted_for",
        db_index=True,
        help_text="The comment that was accepted as the solution.",
    )
    accepted_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
    )
    accepted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accepted_solutions",
        db_index=True,
        help_text="The user who accepted the solution (should be journey owner).",
    )

    class Meta:
        db_table = "accepted_solutions"
        verbose_name = "Accepted Solution"
        verbose_name_plural = "Accepted Solutions"
        indexes = [
            models.Index(fields=["accepted_at"]),
            models.Index(fields=["accepted_by"]),
        ]

    def __str__(self):
        return f"Accepted solution for {self.journey_update.title}"


class SavedUpdate(UUIDPrimaryKeyMixin, TimeStampMixin):
    """
    Saved/bookmarked updates for a user.
    Per SRS: private bookmark list, unique constraint (user, update).
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="saved_updates",
        db_index=True,
    )
    update = models.ForeignKey(
        "journey.JourneyUpdate",
        on_delete=models.CASCADE,
        related_name="saved_by",
        db_index=True,
    )

    class Meta:
        db_table = "saved_updates"
        verbose_name = "Saved Update"
        verbose_name_plural = "Saved Updates"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "update"],
                name="unique_saved_update_per_user",
            )
        ]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["update"]),
            models.Index(fields=["user", "update"]),
        ]

    def __str__(self):
        return f"{self.user.username} saved {self.update.title}"


class SavedJourney(UUIDPrimaryKeyMixin, TimeStampMixin):
    """
    A user can save a Journey for later reference.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="saved_journeys",
        db_index=True,
    )
    journey = models.ForeignKey(
        "journey.Journey",
        on_delete=models.CASCADE,
        related_name="saved_by_users",
        db_index=True,
    )

    class Meta:
        db_table = "saved_journeys"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "journey"],
                name="unique_saved_journey_per_user",
            )
        ]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["journey"]),
            models.Index(fields=["user", "journey"]),
            models.Index(fields=["-created_at"]),
        ]
        verbose_name = "Saved Journey"
        verbose_name_plural = "Saved Journeys"

    def __str__(self):
        return f"{self.user} saved {self.journey}"


class Notification(UUIDPrimaryKeyMixin, TimeStampMixin):
    """
    In-app notification system using GenericForeignKey for flexible target objects.
    Per SRS: polymorphic target using target_type + target_id.
    """

    class Type(models.TextChoices):
        LIKE = "LIKE", "Like"
        COMMENT = "COMMENT", "Comment"
        COMMENT_REPLY = "COMMENT_REPLY", "Comment Reply"
        FOLLOW = "FOLLOW", "Follow"
        ACCEPTED_SOLUTION = "ACCEPTED_SOLUTION", "Accepted Solution"
        MILESTONE = "MILESTONE", "Milestone"

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        db_index=True,
    )
    actor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications_sent",
        db_index=True,
    )
    notification_type = models.CharField(
        max_length=30,
        choices=Type.choices,
        db_index=True,
    )

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
    )
    object_id = models.UUIDField()
    target = GenericForeignKey("content_type", "object_id")

    title = models.CharField(max_length=150)
    body = models.CharField(max_length=300)

    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["recipient", "is_read", "-created_at"]),
            models.Index(fields=["recipient", "notification_type"]),
        ]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"{self.actor} {self.notification_type.lower()} → {self.recipient}"

    def mark_as_read(self):
        """Mark this notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])
