from django.db import models


class ScoreReason(models.TextChoices):
    """Reasons for score changes (per SRS)."""

    JOURNEY_CREATED = "JOURNEY_CREATED", "Journey Created"
    UPDATE_ADDED = "UPDATE_ADDED", "Journey Update Added"
    SOLUTION_ACCEPTED = "SOLUTION_ACCEPTED", "Accepted Solution"
    COMMENT_RECEIVED = "COMMENT_RECEIVED", "Received Comment"
    LIKE_RECEIVED = "LIKE_RECEIVED", "Received Like"
    MILESTONE_COMPLETED = "MILESTONE_COMPLETED", "Milestone Completed"
    SAVED_JOURNEY = "SAVED_JOURNEY", "Saved a Journey"
    FOLLOWED = "FOLLOWED", "Followed by someone"
    DAILY_LOGIN = "DAILY_LOGIN", "Daily Login"
    BADGE_EARNED = "BADGE_EARNED", "Earned a Badge"
    STREAK_BONUS = "STREAK_BONUS", "Streak Bonus"

    JOURNEY_DELETED = "JOURNEY_DELETED", "Journey Deleted"
    UPDATE_DELETED = "UPDATE_DELETED", "Update Deleted"
    UNLIKED = "UNLIKED", "Unliked"
    COMMENT_REMOVED = "COMMENT_REMOVED", "Comment Removed"
    REPORTED = "REPORTED", "Reported"


class ScoreCategory(models.TextChoices):
    """Score categories per SRS."""

    CONSISTENCY = "CONSISTENCY", "Consistency"
    ENGAGEMENT = "ENGAGEMENT", "Engagement"
    MILESTONE = "MILESTONE", "Milestone"
    INFLUENCE = "INFLUENCE", "Influence"


class ScoreConstants:
    """Score point values and limits per SRS."""

    UPDATE_POSTED = 5
    MILESTONE_COMPLETED = 15
    JOURNEY_COMPLETED = 50
    COMMENT_GIVEN = 2
    ACCEPTED_SOLUTION = 25
    LIKE_RECEIVED = 1
    STREAK_BONUS = 10
    JOURNEY_CREATED = 10

    MAX_UPDATES_PER_DAY = 3
    MAX_COMMENTS_PER_DAY = 10
    MAX_LIKE_POINTS_PER_WEEK = 100

    STREAK_DAYS_REQUIRED = 7
