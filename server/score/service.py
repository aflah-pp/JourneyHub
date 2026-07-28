import math
from datetime import timedelta
from typing import Optional

from django.contrib.contenttypes.models import ContentType
from django.db import models, transaction
from django.db.models import F
from django.utils import timezone

from .constants import ScoreCategory, ScoreConstants, ScoreReason
from .models import BuilderScore, BuilderScoreHistory


class ScoreService:
    """
    Business logic for gamification scores.
    All score modifications go through this service.
    Per SRS: anti-spam guards, daily caps, streak bonuses.
    """

    MAX_UPDATES_PER_DAY = ScoreConstants.MAX_UPDATES_PER_DAY
    MAX_COMMENTS_PER_DAY = ScoreConstants.MAX_COMMENTS_PER_DAY
    MAX_LIKE_POINTS_PER_WEEK = ScoreConstants.MAX_LIKE_POINTS_PER_WEEK

    @staticmethod
    @transaction.atomic
    def add_score(
        user,
        category: str,
        amount: int,
        reason: str,
        related_obj=None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        skip_limits: bool = False,
    ) -> Optional[BuilderScoreHistory]:
        """
        Add (or subtract) points from a user's score category.
        Updates total, level, and creates a history entry.

        Args:
            user: The user receiving the score
            category: ScoreCategory value
            amount: Positive or negative integer
            reason: ScoreReason value
            related_obj: Optional related object
            ip_address: Optional IP for audit
            user_agent: Optional user agent for audit
            skip_limits: Bypass anti-spam limits (for admin/manual adjustments)

        Returns:
            BuilderScoreHistory instance or None if skipped
        """
        if amount == 0:
            return None

        score, created = BuilderScore.objects.get_or_create(user=user)

        if not skip_limits and amount > 0:
            if not ScoreService._check_limits(score, reason, category):
                return None

        field_name = f"{category.lower()}_score"
        old_value = getattr(score, field_name)
        new_value = max(0, old_value + amount)
        setattr(score, field_name, new_value)

        score.total_score = score.recalculate_total()

        ScoreService._recalculate_level(score)

        score.save(
            update_fields=[
                field_name,
                "total_score",
                "level",
                "experience_points",
                "next_level_xp",
            ]
        )

        history = BuilderScoreHistory.objects.create(
            user=user,
            category=category,
            delta=amount,
            old_value=old_value,
            new_value=new_value,
            reason=reason,
            related_obj_type=(
                ContentType.objects.get_for_model(related_obj) if related_obj else None
            ),
            related_obj_id=related_obj.pk if related_obj else None,
            ip_address=ip_address or "",
            user_agent=user_agent or "",
        )

        if amount > 0:
            ScoreService.update_streak(user)

        return history

    @staticmethod
    def _check_limits(score: BuilderScore, reason: str, category: str) -> bool:
        """
        Check anti-spam limits per SRS.
        Returns True if score should be awarded, False if limit reached.
        """
        today = timezone.now().date()

        if reason == ScoreReason.UPDATE_ADDED:
            if score.last_update_date != today:
                score.updates_today = 0
                score.last_update_date = today
            if score.updates_today >= ScoreService.MAX_UPDATES_PER_DAY:
                return False
            score.updates_today = F("updates_today") + 1
            score.save(update_fields=["updates_today", "last_update_date"])

        elif reason == ScoreReason.COMMENT_RECEIVED:
            if score.last_comment_date != today:
                score.comments_today = 0
                score.last_comment_date = today
            if score.comments_today >= ScoreService.MAX_COMMENTS_PER_DAY:
                return False
            score.comments_today = F("comments_today") + 1
            score.save(update_fields=["comments_today", "last_comment_date"])

        elif reason == ScoreReason.LIKE_RECEIVED:
            week_ago = timezone.now() - timedelta(days=7)
            weekly_likes = (
                BuilderScoreHistory.objects.filter(
                    user=score.user,
                    reason=ScoreReason.LIKE_RECEIVED,
                    created_at__gte=week_ago,
                ).aggregate(total=models.Sum("delta"))["total"]
                or 0
            )

            if weekly_likes >= ScoreService.MAX_LIKE_POINTS_PER_WEEK:
                return False

        return True

    @staticmethod
    def _recalculate_level(score: BuilderScore) -> None:
        """
        Update level based on total_score.
        Per SRS formula: level = floor(sqrt(total_score / 10)) + 1
        """
        if score.total_score == 0:
            score.level = 1
            score.experience_points = 0
            score.next_level_xp = 100
            return

        new_level = int(math.floor(math.sqrt(score.total_score / 10))) + 1
        if new_level != score.level:
            score.level = new_level
            score.experience_points = score.total_score % 100
            score.next_level_xp = 100

    @staticmethod
    @transaction.atomic
    def update_streak(user, activity_date=None) -> dict:
        """
        Update a user's current streak based on daily activity.
        Per SRS: bonus for posting in 7 of last 7 days.

        Returns:
            dict with streak info: {
                'current_streak': int,
                'longest_streak': int,
                'bonus_awarded': bool
            }
        """
        score, _ = BuilderScore.objects.get_or_create(user=user)
        today = timezone.now().date()

        if not activity_date:
            activity_date = today

        if score.last_activity_at and score.last_activity_at.date() == today:
            return {
                "current_streak": score.current_streak,
                "longest_streak": score.longest_streak,
                "bonus_awarded": False,
            }

        if score.last_activity_at:
            last_date = score.last_activity_at.date()
            diff = (today - last_date).days

            if diff == 1:

                score.current_streak += 1
                if score.current_streak > score.longest_streak:
                    score.longest_streak = score.current_streak
            elif diff > 1:

                score.current_streak = 1
            else:

                return {
                    "current_streak": score.current_streak,
                    "longest_streak": score.longest_streak,
                    "bonus_awarded": False,
                }
        else:

            score.current_streak = 1
            score.longest_streak = 1

        score.last_activity_at = timezone.now()
        score.save(
            update_fields=["current_streak", "longest_streak", "last_activity_at"]
        )

        bonus_awarded = False
        if score.current_streak >= ScoreConstants.STREAK_DAYS_REQUIRED:

            bonus_today = BuilderScoreHistory.objects.filter(
                user=user, reason=ScoreReason.STREAK_BONUS, created_at__date=today
            ).exists()

            if not bonus_today:
                ScoreService.add_score(
                    user=user,
                    category=ScoreCategory.CONSISTENCY,
                    amount=ScoreConstants.STREAK_BONUS,
                    reason=ScoreReason.STREAK_BONUS,
                    ip_address=None,
                    user_agent=None,
                    skip_limits=True,
                )
                bonus_awarded = True

        return {
            "current_streak": score.current_streak,
            "longest_streak": score.longest_streak,
            "bonus_awarded": bonus_awarded,
        }

    @staticmethod
    def get_score(user) -> BuilderScore:
        """Retrieve a user's score record, creating one if missing."""
        return BuilderScore.objects.get_by_user(user)

    @staticmethod
    def get_leaderboard(limit=25):
        """Get top users by total_score with rank."""
        return BuilderScore.objects.get_leaderboard(limit)

    @staticmethod
    def get_rank(user) -> int:
        """Get a user's current rank."""
        score = BuilderScore.objects.get_by_user(user)
        return (
            BuilderScore.objects.filter(total_score__gt=score.total_score).count() + 1
        )

    @staticmethod
    @transaction.atomic
    def add_milestone_bonus(user, journey_update, ip_address=None, user_agent=None):
        """
        Add milestone bonus when a milestone is completed.
        Per SRS: +15 for milestone, +50 for journey completion.
        """

        update = journey_update
        journey = update.journey

        if BuilderScoreHistory.objects.filter(
            user=user,
            reason=ScoreReason.MILESTONE_COMPLETED,
            related_obj_type=ContentType.objects.get_for_model(update),
            related_obj_id=update.pk,
        ).exists():
            return None

        ScoreService.add_score(
            user=user,
            category=ScoreCategory.MILESTONE,
            amount=ScoreConstants.MILESTONE_COMPLETED,
            reason=ScoreReason.MILESTONE_COMPLETED,
            related_obj=update,
            ip_address=ip_address,
            user_agent=user_agent,
            skip_limits=True,
        )

        if journey.status == journey.Status.COMPLETED:

            if not BuilderScoreHistory.objects.filter(
                user=user,
                reason=ScoreReason.JOURNEY_CREATED,
                related_obj_type=ContentType.objects.get_for_model(journey),
                related_obj_id=journey.pk,
            ).exists():
                ScoreService.add_score(
                    user=user,
                    category=ScoreCategory.MILESTONE,
                    amount=ScoreConstants.JOURNEY_COMPLETED,
                    reason=ScoreReason.JOURNEY_CREATED,
                    related_obj=journey,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    skip_limits=True,
                )
        return True

    @staticmethod
    @transaction.atomic
    def deduct_score_on_delete(user, reason: str, related_obj=None, amount: int = 5):
        """
        Deduct points when content is deleted.
        Per SRS: soft delete preserves referential integrity.
        """

        if related_obj:
            existing = BuilderScoreHistory.objects.filter(
                user=user,
                reason=reason,
                related_obj_type=ContentType.objects.get_for_model(related_obj),
                related_obj_id=related_obj.pk,
            ).exists()
            if existing:
                return None

        return ScoreService.add_score(
            user=user,
            category=ScoreCategory.CONSISTENCY,
            amount=-amount,
            reason=reason,
            related_obj=related_obj,
            ip_address=None,
            user_agent=None,
            skip_limits=True,
        )
