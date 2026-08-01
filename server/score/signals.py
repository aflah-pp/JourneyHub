from django.db.models import F
from django.db.models.functions import Greatest
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from journey.models import JourneyUpdate
from reaction.models import AcceptedSolution, Comment, CommentReply, Like, Notification
from reaction.service import NotificationService
from shared.middleware import get_current_request

from .constants import ScoreCategory, ScoreConstants, ScoreReason
from .service import ScoreService


def get_ip_user_agent():
    """Get IP and User-Agent from current request."""
    request = get_current_request()
    if request:
        ip = request.META.get("REMOTE_ADDR", "")
        ua = request.META.get("HTTP_USER_AGENT", "")
        return ip or "", ua or ""
    return "", ""


# ============================================================
# LIKE SIGNALS
# ============================================================


@receiver(post_save, sender=Like)
def increment_like_count(sender, instance, created, **kwargs):
    """Increment denormalized like_count on JourneyUpdate."""
    if created:
        JourneyUpdate.objects.filter(id=instance.journey_update_id).update(like_count=F("like_count") + 1)


@receiver(post_delete, sender=Like)
def decrement_like_count(sender, instance, **kwargs):
    """Decrement denormalized like_count on JourneyUpdate."""
    JourneyUpdate.objects.filter(id=instance.journey_update_id).update(like_count=Greatest(F("like_count") - 1, 0))


@receiver(post_save, sender=Like)
def like_notification(sender, instance, created, **kwargs):
    """Create notification when someone likes an update."""
    if created:
        journey_update = instance.journey_update
        owner = journey_update.journey.owner

        # Don't notify if user liked their own update
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


@receiver(post_save, sender=Like)
def add_score_on_like(sender, instance, created, **kwargs):
    """
    Add score when someone receives a like.
    Per SRS: +1 per like, capped at 100 points/week.
    Skip if user liked their own update.
    """
    if created:
        journey_update = instance.journey_update
        owner = journey_update.journey.owner

        # 🚫 Skip if the user liked their own update
        if instance.user == owner:
            return

        ip, ua = get_ip_user_agent()
        ScoreService.add_score(
            user=owner,
            category=ScoreCategory.ENGAGEMENT,
            amount=ScoreConstants.LIKE_RECEIVED,
            reason=ScoreReason.LIKE_RECEIVED,
            related_obj=instance,
            ip_address=ip,
            user_agent=ua,
        )


@receiver(post_delete, sender=Like)
def deduct_score_on_unlike(sender, instance, **kwargs):
    """Deduct score when a like is removed."""
    journey_update = instance.journey_update
    owner = journey_update.journey.owner

    if instance.user == owner:
        return

    ip, ua = get_ip_user_agent()
    ScoreService.deduct_score_on_delete(
        user=owner,
        reason=ScoreReason.UNLIKED,
        related_obj=instance,
        amount=1,
    )


# ============================================================
# COMMENT SIGNALS
# ============================================================


@receiver(post_save, sender=Comment)
def increment_comment_count_on_save(sender, instance, created, **kwargs):
    """Increment denormalized comment_count on JourneyUpdate."""
    if created and not instance.is_deleted:
        JourneyUpdate.objects.filter(id=instance.journey_update_id).update(comment_count=F("comment_count") + 1)


@receiver(pre_save, sender=Comment)
def comment_pre_save(sender, instance, **kwargs):
    """Handle comment soft-delete count update."""
    if instance.pk:
        try:
            old = Comment.all_objects.get(pk=instance.pk)
            # If comment was active and is now deleted, decrement count
            if not old.is_deleted and instance.is_deleted:
                JourneyUpdate.objects.filter(id=instance.journey_update_id).update(
                    comment_count=Greatest(F("comment_count") - 1, 0)
                )
            # If comment was deleted and is now active (restored), increment count
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


@receiver(post_save, sender=Comment)
def add_score_on_comment(sender, instance, created, **kwargs):
    """
    Add score when someone receives a comment.
    Per SRS: +2 per comment, max 10 counted per day.
    Skip if user commented on their own update.
    """
    if created and not instance.is_deleted:
        journey_update = instance.journey_update
        owner = journey_update.journey.owner

        # 🚫 Skip if the user commented on their own update
        if instance.user == owner:
            return

        ip, ua = get_ip_user_agent()
        ScoreService.add_score(
            user=owner,
            category=ScoreCategory.ENGAGEMENT,
            amount=ScoreConstants.COMMENT_GIVEN,
            reason=ScoreReason.COMMENT_RECEIVED,
            related_obj=instance,
            ip_address=ip,
            user_agent=ua,
        )


@receiver(post_delete, sender=Comment)
def deduct_score_on_comment_deleted(sender, instance, **kwargs):
    """Deduct score when a comment is deleted."""
    if instance.is_deleted and instance.deleted_at:
        journey_update = instance.journey_update
        owner = journey_update.journey.owner

        # 🚫 Skip if the comment was from the owner
        if instance.user == owner:
            return

        ip, ua = get_ip_user_agent()
        ScoreService.deduct_score_on_delete(
            user=owner,
            reason=ScoreReason.COMMENT_REMOVED,
            related_obj=instance,
            amount=2,
        )


# ============================================================
# COMMENT REPLY SIGNALS
# ============================================================


@receiver(post_save, sender=CommentReply)
def reply_notification(sender, instance, created, **kwargs):
    """Create notification when someone replies to a comment."""
    if created and not instance.is_deleted:
        parent_comment = instance.comment
        recipient = parent_comment.user

        # Don't notify if user replied to their own comment
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


@receiver(post_save, sender=CommentReply)
def add_score_on_comment_reply(sender, instance, created, **kwargs):
    """
    Add score when someone receives a comment reply.
    Per SRS: +2 per reply, max 10 counted per day.
    Skip if user replied to their own comment.
    """
    if created and not instance.is_deleted:
        parent_comment = instance.comment
        recipient = parent_comment.user

        if instance.user == recipient:
            return

        ip, ua = get_ip_user_agent()
        ScoreService.add_score(
            user=recipient,
            category=ScoreCategory.ENGAGEMENT,
            amount=ScoreConstants.COMMENT_GIVEN,
            reason=ScoreReason.COMMENT_RECEIVED,
            related_obj=instance,
            ip_address=ip,
            user_agent=ua,
        )


@receiver(post_delete, sender=CommentReply)
def deduct_score_on_reply_deleted(sender, instance, **kwargs):
    """Deduct score when a reply is deleted."""
    if instance.is_deleted and instance.deleted_at:
        parent_comment = instance.comment
        recipient = parent_comment.user

        # 🚫 Skip if the reply was from the recipient
        if instance.user == recipient:
            return

        ip, ua = get_ip_user_agent()
        ScoreService.deduct_score_on_delete(
            user=recipient,
            reason=ScoreReason.COMMENT_REMOVED,
            related_obj=instance,
            amount=2,
        )


@receiver(post_save, sender=AcceptedSolution)
def add_score_on_accepted_solution(sender, instance, created, **kwargs):
    """
    Add score when a solution is accepted.
    Per SRS: +25 for accepted solution.
    """
    if created:
        ip, ua = get_ip_user_agent()
        journey_update = instance.journey_update
        owner = journey_update.journey.owner

        if instance.comment.user == owner:
            return

        comment_author = instance.comment.user
        ScoreService.add_score(
            user=comment_author,
            category=ScoreCategory.INFLUENCE,
            amount=ScoreConstants.ACCEPTED_SOLUTION,
            reason=ScoreReason.SOLUTION_ACCEPTED,
            related_obj=instance,
            ip_address=ip,
            user_agent=ua,
            skip_limits=True,
        )


@receiver(post_delete, sender=AcceptedSolution)
def deduct_score_on_accepted_removed(sender, instance, **kwargs):
    """Deduct score when an accepted solution is removed."""
    ip, ua = get_ip_user_agent()
    comment_author = instance.comment.user
    ScoreService.deduct_score_on_delete(
        user=comment_author,
        reason=ScoreReason.SOLUTION_ACCEPTED,
        related_obj=instance,
        amount=25,
    )


# ============================================================
# FOLLOW SIGNALS (Called from accounts app)
# ============================================================


def add_score_on_follow(follower, following):
    """Add influence points when someone is followed."""
    ip, ua = get_ip_user_agent()
    ScoreService.add_score(
        user=following,
        category=ScoreCategory.INFLUENCE,
        amount=1,
        reason=ScoreReason.FOLLOWED,
        related_obj=None,
        ip_address=ip,
        user_agent=ua,
        skip_limits=True,
    )
