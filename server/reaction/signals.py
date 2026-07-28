from django.db.models import F
from django.db.models.functions import Greatest
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from journey.models import JourneyUpdate

from .models import Comment, CommentReply, Like, Notification
from .service import NotificationService


@receiver(post_save, sender=Like)
def increment_like_count(sender, instance, created, **kwargs):
    """Increment denormalized like_count on JourneyUpdate."""
    if created:
        JourneyUpdate.objects.filter(id=instance.journey_update_id).update(
            like_count=F("like_count") + 1
        )


@receiver(post_delete, sender=Like)
def decrement_like_count(sender, instance, **kwargs):
    """Decrement denormalized like_count on JourneyUpdate."""
    JourneyUpdate.objects.filter(id=instance.journey_update_id).update(
        like_count=Greatest(F("like_count") - 1, 0)
    )


@receiver(post_save, sender=Like)
def like_notification(sender, instance, created, **kwargs):
    """Create notification when someone likes an update."""
    if created:
        journey_update = instance.journey_update
        owner = journey_update.journey.owner

        if instance.user == owner:
            return

        NotificationService.create_notification(
            recipient=owner,
            actor=instance.user,
            notification_type=Notification.Type.LIKE,
            target=journey_update,
            title=f"{instance.user.username} liked your update",
            body=f"{instance.user.username} liked '{journey_update.title}'",
        )


@receiver(post_save, sender=Comment)
def increment_comment_count_on_save(sender, instance, created, **kwargs):
    """Increment denormalized comment_count on JourneyUpdate."""
    if created and not instance.is_deleted:
        JourneyUpdate.objects.filter(id=instance.journey_update_id).update(
            comment_count=F("comment_count") + 1
        )


@receiver(pre_save, sender=Comment)
def comment_pre_save(sender, instance, **kwargs):
    """Handle comment soft-delete count update."""
    if instance.pk:
        try:
            old = Comment.all_objects.get(pk=instance.pk)

            if not old.is_deleted and instance.is_deleted:
                JourneyUpdate.objects.filter(id=instance.journey_update_id).update(
                    comment_count=Greatest(F("comment_count") - 1, 0)
                )
            elif old.is_deleted and not instance.is_deleted:
                JourneyUpdate.objects.filter(id=instance.journey_update_id).update(
                    comment_count=F("comment_count") + 1
                )
        except Comment.DoesNotExist:
            pass


@receiver(post_save, sender=Comment)
def comment_notification(sender, instance, created, **kwargs):
    """Create notification when someone comments on an update."""
    if created and not instance.is_deleted:
        journey_update = instance.journey_update
        owner = journey_update.journey.owner

        if instance.user == owner:
            return

        NotificationService.create_notification(
            recipient=owner,
            actor=instance.user,
            notification_type=Notification.Type.COMMENT,
            target=journey_update,
            title=f"{instance.user.username} commented on your update",
            body=f"{instance.user.username}: {instance.content[:50]}...",
        )


@receiver(post_save, sender=CommentReply)
def reply_notification(sender, instance, created, **kwargs):
    """Create notification when someone replies to a comment."""
    if created and not instance.is_deleted:
        parent_comment = instance.comment
        recipient = parent_comment.user

        if instance.user == recipient:
            return

        NotificationService.create_notification(
            recipient=recipient,
            actor=instance.user,
            notification_type=Notification.Type.COMMENT_REPLY,
            target=parent_comment,
            title=f"{instance.user.username} replied to your comment",
            body=f"{instance.user.username}: {instance.content[:50]}...",
        )


def create_milestone_notification(update, journey):
    """
    Create notification when a milestone is completed.
    Called from journey service when milestone_status changes to COMPLETED.
    """
    owner = journey.owner
    followers = owner.follower_relations.all()

    for follower in followers:
        NotificationService.create_notification(
            recipient=follower.follower,
            actor=owner,
            notification_type=Notification.Type.MILESTONE,
            target=update,
            title=f"{owner.username} reached a milestone!",
            body=f"{owner.username} completed milestone: {update.title}",
        )


def create_accepted_solution_notification(update, comment, accepted_by):
    """
    Create notification when a solution is accepted.
    Called from journey service when accepting a solution.
    """
    NotificationService.create_notification(
        recipient=comment.user,
        actor=accepted_by,
        notification_type=Notification.Type.ACCEPTED_SOLUTION,
        target=update,
        title=f"{accepted_by.username} accepted your solution!",
        body=f"Your solution was accepted for: {update.title}",
    )
