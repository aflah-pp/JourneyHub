from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from accounts.models import User
from journey.models import Journey, JourneyUpdate
from reaction.models import AcceptedSolution, Comment, CommentReply, Like
from shared.middleware import get_current_request

from .constants import ScoreCategory, ScoreConstants, ScoreReason
from .models import BuilderScore
from .service import ScoreService


def get_ip_user_agent():
    """Get IP and User-Agent from current request."""
    request = get_current_request()
    if request:
        ip = request.META.get("REMOTE_ADDR", "")
        ua = request.META.get("HTTP_USER_AGENT", "")
        return ip or "", ua or ""
    return "", ""


@receiver(post_save, sender=User)
def create_user_score(sender, instance, created, **kwargs):
    """Create BuilderScore when a new user registers."""
    if created:
        BuilderScore.objects.create(user=instance)


@receiver(post_save, sender=Journey)
def add_score_on_journey_created(sender, instance, created, **kwargs):
    """Add score when a journey is created."""
    if created:
        ip, ua = get_ip_user_agent()
        ScoreService.add_score(
            user=instance.owner,
            category=ScoreCategory.MILESTONE,
            amount=ScoreConstants.JOURNEY_CREATED,
            reason=ScoreReason.JOURNEY_CREATED,
            related_obj=instance,
            ip_address=ip,
            user_agent=ua,
            skip_limits=True,
        )


@receiver(post_delete, sender=Journey)
def deduct_score_on_journey_deleted(sender, instance, **kwargs):
    """Deduct score when a journey is deleted (soft delete)."""
    if instance.is_deleted and instance.deleted_at:
        ip, ua = get_ip_user_agent()
        ScoreService.deduct_score_on_delete(
            user=instance.owner,
            reason=ScoreReason.JOURNEY_DELETED,
            related_obj=instance,
            amount=10,
        )


@receiver(post_save, sender=JourneyUpdate)
def add_score_on_update_created(sender, instance, created, **kwargs):
    """
    Add score when an update is created.
    Per SRS: +5 per update, max 3 counted per day.
    """
    if created:
        ip, ua = get_ip_user_agent()
        ScoreService.add_score(
            user=instance.journey.owner,
            category=ScoreCategory.CONSISTENCY,
            amount=ScoreConstants.UPDATE_POSTED,
            reason=ScoreReason.UPDATE_ADDED,
            related_obj=instance,
            ip_address=ip,
            user_agent=ua,
        )

        if instance.milestone_status == instance.MilestoneStatus.COMPLETED:
            ScoreService.add_milestone_bonus(
                user=instance.journey.owner,
                journey_update=instance,
                ip_address=ip,
                user_agent=ua,
            )


@receiver(post_delete, sender=JourneyUpdate)
def deduct_score_on_update_deleted(sender, instance, **kwargs):
    """Deduct score when an update is deleted (soft delete)."""
    if instance.is_deleted and instance.deleted_at:
        ip, ua = get_ip_user_agent()
        ScoreService.deduct_score_on_delete(
            user=instance.journey.owner,
            reason=ScoreReason.UPDATE_DELETED,
            related_obj=instance,
            amount=5,
        )


@receiver(post_save, sender=Like)
def add_score_on_like(sender, instance, created, **kwargs):
    """
    Add score when someone receives a like.
    Per SRS: +1 per like, capped at 100 points/week.
    """
    if created:
        ip, ua = get_ip_user_agent()
        owner = instance.journey_update.journey.owner
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
    ip, ua = get_ip_user_agent()
    owner = instance.journey_update.journey.owner
    ScoreService.deduct_score_on_delete(
        user=owner,
        reason=ScoreReason.UNLIKED,
        related_obj=instance,
        amount=1,
    )


@receiver(post_save, sender=Comment)
def add_score_on_comment(sender, instance, created, **kwargs):
    """
    Add score when someone receives a comment.
    Per SRS: +2 per comment, max 10 counted per day.
    """
    if created and not instance.is_deleted:
        ip, ua = get_ip_user_agent()
        owner = instance.journey_update.journey.owner
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
        ip, ua = get_ip_user_agent()
        owner = instance.journey_update.journey.owner
        ScoreService.deduct_score_on_delete(
            user=owner,
            reason=ScoreReason.COMMENT_REMOVED,
            related_obj=instance,
            amount=2,
        )


@receiver(post_save, sender=CommentReply)
def add_score_on_comment_reply(sender, instance, created, **kwargs):
    """
    Add score when someone receives a comment reply.
    Per SRS: +2 per reply, max 10 counted per day.
    """
    if created and not instance.is_deleted:
        ip, ua = get_ip_user_agent()
        owner = instance.comment.user
        ScoreService.add_score(
            user=owner,
            category=ScoreCategory.ENGAGEMENT,
            amount=ScoreConstants.COMMENT_GIVEN,
            reason=ScoreReason.COMMENT_RECEIVED,
            related_obj=instance,
            ip_address=ip,
            user_agent=ua,
        )


@receiver(post_save, sender=AcceptedSolution)
def add_score_on_accepted_solution(sender, instance, created, **kwargs):
    """
    Add score when a solution is accepted.
    Per SRS: +25 for accepted solution.
    """
    if created:
        ip, ua = get_ip_user_agent()
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
