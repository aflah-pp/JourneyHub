from rest_framework import serializers

from .models import BuilderScore, BuilderScoreHistory


class BuilderScoreSerializer(serializers.ModelSerializer):
    """Full score details (owner/staff only)."""

    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = BuilderScore
        fields = (
            "user_username",
            "consistency_score",
            "engagement_score",
            "milestone_score",
            "influence_score",
            "total_score",
            "level",
            "experience_points",
            "next_level_xp",
            "rank",
            "current_streak",
            "longest_streak",
            "last_activity_at",
        )


class PublicBuilderScoreSerializer(serializers.ModelSerializer):
    """Public score details (safe for anyone)."""

    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = BuilderScore
        fields = (
            "user_username",
            "total_score",
            "level",
            "current_streak",
            "longest_streak",
        )


class LeaderboardEntrySerializer(serializers.ModelSerializer):
    """
    Serializer for leaderboard entries with rank.
    """

    user_username = serializers.CharField(source="user.username", read_only=True)
    rank = serializers.IntegerField(read_only=True)

    class Meta:
        model = BuilderScore
        fields = (
            "user_username",
            "total_score",
            "level",
            "rank",
            "current_streak",
        )


class BuilderScoreHistorySerializer(serializers.ModelSerializer):
    """Score history with human-readable fields."""

    category_label = serializers.CharField(
        source="get_category_display", read_only=True
    )
    reason_label = serializers.CharField(source="get_reason_display", read_only=True)

    class Meta:
        model = BuilderScoreHistory
        fields = (
            "id",
            "category",
            "category_label",
            "delta",
            "old_value",
            "new_value",
            "reason",
            "reason_label",
            "created_at",
            "ip_address",
        )
