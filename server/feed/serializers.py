from rest_framework import serializers

from accounts.serializers import MiniUserSerializer
from journey.models import JourneyUpdate
from journey.serializers import JourneyImageSerializer, TagSerializer
from reaction.models import Like, SavedUpdate


class FeedItemSerializer(serializers.ModelSerializer):
    """
    Serializer for feed items with all required fields.
    """

    author = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()
    is_liked_by_me = serializers.SerializerMethodField()
    is_saved_by_me = serializers.SerializerMethodField()

    milestone_badge = serializers.SerializerMethodField()
    help_needed_badge = serializers.SerializerMethodField()

    journey_title = serializers.CharField(source="journey.title", read_only=True)
    journey_id = serializers.UUIDField(source="journey.id", read_only=True)
    journey_visibility = serializers.CharField(
        source="journey.visibility", read_only=True
    )

    class Meta:
        model = JourneyUpdate
        fields = (
            "id",
            "title",
            "description",
            "progress_percentage",
            "milestone_status",
            "help_needed",
            "created_at",
            "updated_at",
            "author",
            "journey_id",
            "journey_title",
            "journey_visibility",
            "images",
            "tags",
            "milestone_badge",
            "help_needed_badge",
            "like_count",
            "comment_count",
            "is_liked_by_me",
            "is_saved_by_me",
        )
        read_only_fields = fields

    def get_author(self, obj):
        """Get author details with profile."""
        try:
            if obj.journey and obj.journey.owner:
                return MiniUserSerializer(obj.journey.owner).data
        except Exception:
            pass
        return None

    def get_images(self, obj):
        """Get images with safety check."""
        try:
            if hasattr(obj, "images") and obj.images.exists():
                return JourneyImageSerializer(obj.images.all(), many=True).data
        except Exception:
            pass
        return []

    def get_tags(self, obj):
        """Get tags from prefetched data."""
        try:
            if hasattr(obj, "tags_prefetched") and obj.tags_prefetched is not None:
                tags = []
                for tag_relation in obj.tags_prefetched:
                    if hasattr(tag_relation, "tag"):
                        tags.append(tag_relation.tag)
                return TagSerializer(tags, many=True).data
        except Exception:
            pass
        return []

    def get_is_liked_by_me(self, obj):
        """Check if the current user liked this update."""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False

        try:
            if hasattr(obj, "likes_prefetched") and obj.likes_prefetched is not None:
                return any(
                    like.user_id == request.user.id for like in obj.likes_prefetched
                )
            return Like.objects.filter(user=request.user, journey_update=obj).exists()
        except Exception:
            return False

    def get_is_saved_by_me(self, obj):
        """Check if the current user saved this update."""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False

        try:
            if hasattr(obj, "saved_prefetched") and obj.saved_prefetched is not None:
                return any(
                    save.user_id == request.user.id for save in obj.saved_prefetched
                )
            return SavedUpdate.objects.filter(user=request.user, update=obj).exists()
        except Exception:
            return False

    def get_milestone_badge(self, obj):
        """Get milestone badge info."""
        try:
            if obj.milestone_status == obj.MilestoneStatus.COMPLETED:
                return {
                    "type": "completed",
                    "label": "Completed",
                    "color": "green",
                }
            elif obj.milestone_status == obj.MilestoneStatus.MILESTONE:
                return {
                    "type": "milestone",
                    "label": "Milestone",
                    "color": "blue",
                }
        except Exception:
            pass
        return None

    def get_help_needed_badge(self, obj):
        """Get help needed badge info."""
        try:
            if obj.help_needed:
                return {
                    "type": "help_needed",
                    "label": "Help Needed",
                    "color": "orange",
                }
        except Exception:
            pass
        return None
