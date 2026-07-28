from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from accounts.models import User
from shared.models import TimeStampMixin, UUIDPrimaryKeyMixin

from .constants import ScoreCategory, ScoreReason


class BuilderScoreManager(models.Manager):
    """Custom manager for BuilderScore with optimized queries."""

    def get_queryset(self):
        return super().get_queryset().select_related("user", "user__profile")

    def get_leaderboard(self, limit=25):
        """Get top users by total_score."""
        return self.get_queryset().order_by("-total_score")[:limit]

    def get_by_user(self, user):
        """Get or create score for a user."""
        score, created = self.get_or_create(user=user)
        return score


class BuilderScore(UUIDPrimaryKeyMixin, TimeStampMixin):
    """
    Tracks a user's current gamification scores.
    One score record per user.
    Per SRS: consistency_score, engagement_score, milestone_score, total_score
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="builder_score",
        db_index=True,
    )

    consistency_score = models.PositiveIntegerField(
        default=0,
        help_text="Daily engagement & streak",
        db_index=True,
    )
    engagement_score = models.PositiveIntegerField(
        default=0,
        help_text="Interactions with others",
        db_index=True,
    )
    milestone_score = models.PositiveIntegerField(
        default=0,
        help_text="Completing journey milestones",
        db_index=True,
    )
    influence_score = models.PositiveIntegerField(
        default=0,
        help_text="Accepted solutions, follower count",
        db_index=True,
    )
    total_score = models.PositiveIntegerField(
        default=0,
        help_text="Sum of all category scores",
        db_index=True,
    )

    level = models.PositiveSmallIntegerField(
        default=1,
        db_index=True,
    )
    experience_points = models.PositiveIntegerField(
        default=0,
        help_text="XP for leveling",
    )
    next_level_xp = models.PositiveIntegerField(
        default=100,
        help_text="XP needed for next level",
    )

    rank = models.PositiveIntegerField(
        default=0,
        help_text="Global rank (updated periodically)",
        db_index=True,
    )

    current_streak = models.PositiveSmallIntegerField(
        default=0,
        help_text="Current consecutive days with activity",
    )
    longest_streak = models.PositiveSmallIntegerField(
        default=0,
        help_text="Longest streak achieved",
    )
    last_activity_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last activity timestamp for streak calculation",
    )

    last_update_date = models.DateField(
        null=True,
        blank=True,
        help_text="Last date for update count tracking",
    )
    updates_today = models.PositiveSmallIntegerField(
        default=0,
        help_text="Number of updates posted today",
    )
    last_comment_date = models.DateField(
        null=True,
        blank=True,
        help_text="Last date for comment count tracking",
    )
    comments_today = models.PositiveSmallIntegerField(
        default=0,
        help_text="Number of comments posted today",
    )

    objects = BuilderScoreManager()

    class Meta:
        db_table = "builder_scores"
        verbose_name = "Builder Score"
        verbose_name_plural = "Builder Scores"
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["total_score"]),
            models.Index(fields=["level"]),
            models.Index(fields=["rank"]),
            models.Index(fields=["consistency_score"]),
            models.Index(fields=["engagement_score"]),
            models.Index(fields=["milestone_score"]),
            models.Index(fields=["influence_score"]),
        ]

    def __str__(self):
        return f"{self.user.username} - Score: {self.total_score} (Lv.{self.level})"

    def recalculate_total(self):
        """Recalculate total score from category scores."""
        self.total_score = (
            self.consistency_score
            + self.engagement_score
            + self.milestone_score
            + self.influence_score
        )
        return self.total_score


class BuilderScoreHistory(UUIDPrimaryKeyMixin, TimeStampMixin):
    """
    Tracks every score change with reason and related object.
    Per SRS: full audit trail for consistency calculation.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="score_histories",
        db_index=True,
    )
    category = models.CharField(
        max_length=20,
        choices=ScoreCategory.choices,
        db_index=True,
    )
    delta = models.IntegerField(
        help_text="Change amount (positive or negative)",
    )
    old_value = models.PositiveIntegerField()
    new_value = models.PositiveIntegerField()
    reason = models.CharField(
        max_length=50,
        choices=ScoreReason.choices,
        db_index=True,
    )

    related_obj_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    related_obj_id = models.UUIDField(null=True, blank=True)
    related_obj = GenericForeignKey("related_obj_type", "related_obj_id")

    user_agent = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        default=None,
    )

    class Meta:
        db_table = "builder_score_histories"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["user", "category"]),
            models.Index(fields=["reason"]),
            models.Index(fields=["related_obj_type", "related_obj_id"]),
            models.Index(fields=["-created_at"]),
        ]
        verbose_name = "Builder Score History"
        verbose_name_plural = "Builder Score Histories"

    def __str__(self):
        return f"{self.user.username} {self.category} {self.delta:+} ({self.reason})"
