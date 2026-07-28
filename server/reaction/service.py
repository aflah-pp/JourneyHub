from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from accounts.models import User
from journey.models import Journey, JourneyUpdate

from .models import (
    AcceptedSolution,
    Comment,
    CommentReply,
    Like,
    Notification,
    SavedJourney,
    SavedUpdate,
)


class LikeService:
    """Handles creation and removal of likes on a JourneyUpdate."""

    @staticmethod
    @transaction.atomic
    def create_like(user: User, journey_update: JourneyUpdate) -> Like:
        """
        Create a like for a given user on a journey update.
        Raises ValidationError if the user has already liked this update.
        """
        if Like.objects.filter(user=user, journey_update=journey_update).exists():
            raise ValidationError("You have already liked this update.")

        like = Like.objects.create(user=user, journey_update=journey_update)
        return like

    @staticmethod
    @transaction.atomic
    def remove_like(user: User, journey_update: JourneyUpdate) -> None:
        """Remove a like (hard delete)."""
        deleted, _ = Like.objects.filter(
            user=user, journey_update=journey_update
        ).delete()
        if deleted == 0:
            raise ValidationError("You have not liked this update.")
        return None

    @staticmethod
    def is_liked(user: User, journey_update: JourneyUpdate) -> bool:
        """Check if a user has liked an update."""
        return Like.objects.filter(user=user, journey_update=journey_update).exists()


class CommentService:
    """Handles creation and soft-deletion of comments on a JourneyUpdate."""

    @staticmethod
    @transaction.atomic
    def create_comment(
        user: User, journey_update: JourneyUpdate, content: str
    ) -> Comment:
        """Create a new comment (non-deleted)."""
        if not journey_update.is_visible_to(user):
            raise ValidationError("You cannot comment on this update.")

        comment = Comment.objects.create(
            user=user,
            journey_update=journey_update,
            content=content.strip(),
        )
        return comment

    @staticmethod
    @transaction.atomic
    def soft_delete_comment(comment: Comment, deleted_by: User) -> None:
        """Soft-delete a comment (set is_deleted=True)."""
        if comment.is_deleted:
            raise ValidationError("This comment is already deleted.")
        comment.soft_delete(deleted_by)

    @staticmethod
    def get_comment_or_404(comment_id: str) -> Comment:
        """Retrieve a non-deleted comment or raise 404."""
        return get_object_or_404(Comment.objects, id=comment_id)

    @staticmethod
    def get_comment_with_replies(comment_id: str):
        """Retrieve a comment with its replies."""
        return get_object_or_404(
            Comment.objects.select_related("user", "user__profile").prefetch_related(
                "replies__user__profile"
            ),
            id=comment_id,
            is_deleted=False,
        )


class CommentReplyService:
    """Handles creation and soft-deletion of replies to a comment."""

    @staticmethod
    @transaction.atomic
    def create_reply(user: User, parent_comment: Comment, content: str) -> CommentReply:
        """Create a new reply to a comment."""
        if parent_comment.is_deleted:
            raise ValidationError("Cannot reply to a deleted comment.")

        if not parent_comment.journey_update.is_visible_to(user):
            raise ValidationError("You cannot reply to this comment.")

        reply = CommentReply.objects.create(
            user=user,
            comment=parent_comment,
            content=content.strip(),
        )
        return reply

    @staticmethod
    @transaction.atomic
    def soft_delete_reply(reply: CommentReply, deleted_by: User) -> None:
        """Soft-delete a reply."""
        if reply.is_deleted:
            raise ValidationError("This reply is already deleted.")
        reply.soft_delete(deleted_by)

    @staticmethod
    def get_reply_or_404(reply_id: str) -> CommentReply:
        """Retrieve a non-deleted reply or raise 404."""
        return get_object_or_404(CommentReply.objects, id=reply_id)


class SolutionService:
    """Handles accepting and removing solutions for journey updates."""

    @staticmethod
    @transaction.atomic
    def accept_solution(
        journey_update: JourneyUpdate, comment: Comment, accepted_by: User
    ) -> AcceptedSolution:
        """
        Accept a comment as the solution for a journey update.

        This will:
        1. Create the AcceptedSolution record
        2. Set help_needed=False on the update
        3. Create notification for the solution author
        """
        if AcceptedSolution.objects.filter(journey_update=journey_update).exists():
            raise ValidationError("A solution has already been accepted.")

        if comment.journey_update_id != journey_update.id:
            raise ValidationError("This comment does not belong to this update.")

        accepted = AcceptedSolution.objects.create(
            journey_update=journey_update,
            comment=comment,
            accepted_by=accepted_by,
        )

        journey_update.help_needed = False
        journey_update.save(update_fields=["help_needed"])

        from .signals import create_accepted_solution_notification

        create_accepted_solution_notification(
            update=journey_update, comment=comment, accepted_by=accepted_by
        )

        return accepted

    @staticmethod
    @transaction.atomic
    def remove_accepted_solution(journey_update: JourneyUpdate) -> None:
        """
        Remove the accepted solution for a journey update.

        This will:
        1. Delete the AcceptedSolution record
        2. Set help_needed=True on the update
        """
        if hasattr(journey_update, "accepted_solution"):
            journey_update.accepted_solution.delete()
            journey_update.help_needed = True
            journey_update.save(update_fields=["help_needed"])


class SavedUpdateService:
    """Handles saving/unsaving a JourneyUpdate for a user."""

    @staticmethod
    @transaction.atomic
    def save_update(user: User, update: JourneyUpdate) -> SavedUpdate:
        """
        Save an update for a user.
        Raises ValidationError if already saved.
        """
        if not update.is_visible_to(user):
            raise ValidationError("You cannot save this update.")

        if SavedUpdate.objects.filter(user=user, update=update).exists():
            raise ValidationError("You have already saved this update.")

        return SavedUpdate.objects.create(user=user, update=update)

    @staticmethod
    @transaction.atomic
    def unsave_update(user: User, update: JourneyUpdate) -> None:
        """Remove a saved update (hard delete)."""
        deleted, _ = SavedUpdate.objects.filter(user=user, update=update).delete()
        if deleted == 0:
            raise ValidationError("You have not saved this update.")

    @staticmethod
    def is_saved(user: User, update: JourneyUpdate) -> bool:
        """Check if an update is saved by a user."""
        return SavedUpdate.objects.filter(user=user, update=update).exists()


class SavedJourneyService:
    """Handles saving/unsaving a Journey for a user."""

    @staticmethod
    @transaction.atomic
    def save_journey(user: User, journey: Journey) -> SavedJourney:
        """
        Save a journey for a user.
        Raises ValidationError if already saved.
        """
        if not journey.is_visible_to(user):
            raise ValidationError("You cannot save this journey.")

        if SavedJourney.objects.filter(user=user, journey=journey).exists():
            raise ValidationError("You have already saved this journey.")

        return SavedJourney.objects.create(user=user, journey=journey)

    @staticmethod
    @transaction.atomic
    def unsave_journey(user: User, journey: Journey) -> None:
        """Remove a saved journey (hard delete)."""
        deleted, _ = SavedJourney.objects.filter(user=user, journey=journey).delete()
        if deleted == 0:
            raise ValidationError("You have not saved this journey.")

    @staticmethod
    def is_saved(user: User, journey: Journey) -> bool:
        """Check if a journey is saved by a user."""
        return SavedJourney.objects.filter(user=user, journey=journey).exists()


class NotificationService:
    """Handles creation and read status of in-app notifications."""

    @staticmethod
    @transaction.atomic
    def create_notification(
        recipient: User,
        actor: User,
        notification_type: str,
        target,
        title: str,
        body: str,
    ) -> Notification:
        """
        Create a notification.
        If recipient == actor, skip to avoid self-notifications.
        """
        if recipient == actor:
            return None

        from django.contrib.contenttypes.models import ContentType

        return Notification.objects.create(
            recipient=recipient,
            actor=actor,
            notification_type=notification_type,
            content_type=ContentType.objects.get_for_model(target),
            object_id=target.pk,
            title=title,
            body=body,
        )

    @staticmethod
    def mark_as_read(notification: Notification) -> None:
        """Mark a single notification as read."""
        notification.mark_as_read()

    @staticmethod
    @transaction.atomic
    def mark_all_as_read(user: User) -> int:
        """Mark all unread notifications for a user as read. Returns count."""
        now = timezone.now()
        updated = Notification.objects.filter(recipient=user, is_read=False).update(
            is_read=True, read_at=now
        )
        return updated

    @staticmethod
    def get_unread_count(user: User) -> int:
        """Return the number of unread notifications for a user."""
        return Notification.objects.filter(recipient=user, is_read=False).count()

    @staticmethod
    def get_notifications(user: User, limit: int = 20):
        """Get recent notifications for a user."""
        return (
            Notification.objects.filter(recipient=user)
            .select_related("actor", "actor__profile")
            .order_by("-created_at")[:limit]
        )
