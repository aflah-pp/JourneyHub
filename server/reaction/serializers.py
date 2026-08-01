from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.serializers import MiniUserSerializer
from journey.serializers import JourneyUpdateListSerializer
from shared.services.html_sanitizer import sanitize_html

from .models import (
    AcceptedSolution,
    Comment,
    CommentReply,
    Like,
    Notification,
    SavedJourney,
    SavedUpdate,
)
from .validator import validate_stripped_text

User = get_user_model()


class LikeSerializer(serializers.ModelSerializer):
    """Like representation."""

    user = MiniUserSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ("id", "user", "created_at")
        read_only_fields = fields


class LikeCreateSerializer(serializers.ModelSerializer):
    """Payload for creating a like."""

    class Meta:
        model = Like
        fields = ()

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        validated_data["journey_update"] = self.context["journey_update"]
        return super().create(validated_data)


class CommentReplySerializer(serializers.ModelSerializer):
    """Comment reply representation."""

    user = MiniUserSerializer(read_only=True)

    class Meta:
        model = CommentReply
        fields = ("id", "user", "content", "created_at", "updated_at")
        read_only_fields = fields


class CommentReplyCreateSerializer(serializers.ModelSerializer):
    """Payload for creating a comment reply."""

    class Meta:
        model = CommentReply
        fields = ("content",)

    def validate_content(self, value):
        value = validate_stripped_text(value, min_length=1, field_name="Reply")
        return sanitize_html(value)

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        validated_data["comment"] = self.context["comment"]
        return super().create(validated_data)


class CommentReplyUpdateSerializer(serializers.ModelSerializer):
    """Payload for updating a comment reply."""

    class Meta:
        model = CommentReply
        fields = ("content",)

    def validate_content(self, value):
        value = validate_stripped_text(value, min_length=1, field_name="Reply")
        return sanitize_html(value)


class CommentSerializer(serializers.ModelSerializer):
    """Comment representation with nested replies."""

    user = MiniUserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    reply_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Comment
        fields = (
            "id",
            "user",
            "content",
            "created_at",
            "updated_at",
            "reply_count",
            "replies",
        )
        read_only_fields = fields

    def get_replies(self, obj):
        """Get non-deleted replies for this comment."""
        replies = obj.replies.filter(is_deleted=False)
        return CommentReplySerializer(replies, many=True).data


class CommentCreateSerializer(serializers.ModelSerializer):
    """Payload for creating a comment."""

    class Meta:
        model = Comment
        fields = ("content",)

    def validate_content(self, value):
        value = validate_stripped_text(value, min_length=1, field_name="Comment")
        return sanitize_html(value)

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        validated_data["journey_update"] = self.context["journey_update"]
        return super().create(validated_data)


class CommentUpdateSerializer(serializers.ModelSerializer):
    """Payload for updating a comment."""

    class Meta:
        model = Comment
        fields = ("content",)

    def validate_content(self, value):
        value = validate_stripped_text(value, min_length=1, field_name="Comment")
        return sanitize_html(value)


class AcceptedSolutionSerializer(serializers.ModelSerializer):
    """
    Read-only representation of an accepted solution.
    """

    comment = CommentSerializer(read_only=True)
    accepted_by = MiniUserSerializer(read_only=True)
    journey_update_id = serializers.UUIDField(
        source="journey_update.id", read_only=True
    )

    class Meta:
        model = AcceptedSolution
        fields = (
            "id",
            "journey_update_id",
            "comment",
            "accepted_at",
            "accepted_by",
        )
        read_only_fields = fields


class AcceptedSolutionCreateSerializer(serializers.Serializer):
    """
    Payload for accepting a solution.
    """

    comment_id = serializers.UUIDField()

    def validate(self, attrs):
        update = self.context["update"]

        try:
            comment = Comment.objects.get(
                id=attrs["comment_id"],
                journey_update=update,
                is_deleted=False,
            )
        except Comment.DoesNotExist:
            raise serializers.ValidationError(
                {"comment_id": ("Comment not found or does not belong to this update.")}
            )

        if AcceptedSolution.objects.filter(journey_update=update).exists():
            raise serializers.ValidationError(
                "A solution has already been accepted for this update."
            )

        attrs["comment"] = comment
        return attrs


class AcceptedSolutionRemoveSerializer(serializers.Serializer):
    """
    Payload for removing an accepted solution.
    """


class SavedUpdateSerializer(serializers.ModelSerializer):
    """Saved update representation."""

    user = MiniUserSerializer(read_only=True)
    update = JourneyUpdateListSerializer(read_only=True)
    saved_at = serializers.DateTimeField(source="created_at", read_only=True)

    class Meta:
        model = SavedUpdate
        fields = (
            "id",
            "user",
            "update",
            "saved_at",
        )
        read_only_fields = fields


class SavedUpdateCreateSerializer(serializers.ModelSerializer):
    """Payload for saving an update."""

    class Meta:
        model = SavedUpdate
        fields = ()

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        validated_data["update"] = self.context["update"]
        return super().create(validated_data)


class SavedJourneySerializer(serializers.ModelSerializer):
    """Saved journey representation."""

    user = MiniUserSerializer(read_only=True)
    journey = serializers.PrimaryKeyRelatedField(read_only=True)
    journey_title = serializers.CharField(source="journey.title", read_only=True)
    journey_owner = MiniUserSerializer(source="journey.owner", read_only=True)

    class Meta:
        model = SavedJourney
        fields = (
            "id",
            "user",
            "journey",
            "journey_title",
            "journey_owner",
            "created_at",
        )
        read_only_fields = fields


class SavedJourneyCreateSerializer(serializers.ModelSerializer):
    """Payload for saving a journey."""

    class Meta:
        model = SavedJourney
        fields = ()

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        validated_data["journey"] = self.context["journey"]
        return super().create(validated_data)


class NotificationSerializer(serializers.ModelSerializer):
    """Notification representation with polymorphic target."""

    actor = MiniUserSerializer(read_only=True)
    target_type = serializers.SerializerMethodField()
    target_id = serializers.UUIDField(source="object_id", read_only=True)
    target_detail = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = (
            "id",
            "notification_type",
            "title",
            "body",
            "is_read",
            "read_at",
            "created_at",
            "actor",
            "target_type",
            "target_id",
            "target_detail",
        )
        read_only_fields = fields

    def get_target_type(self, obj):
        """Get the model name of the target."""
        return obj.content_type.model

    def get_target_detail(self, obj):
        """Get basic detail of the target object."""
        target = obj.target
        if not target:
            return None

        if hasattr(target, "title"):
            return {"title": target.title, "id": str(target.id)}
        if hasattr(target, "content"):
            return {"content": target.content[:100], "id": str(target.id)}
        return {"id": str(target.id)}


class NotificationUpdateSerializer(serializers.ModelSerializer):
    """Payload for updating notification (mark read/unread)."""

    class Meta:
        model = Notification
        fields = ("is_read",)

    def update(self, instance, validated_data):
        is_read = validated_data.get("is_read")
        if is_read and not instance.is_read:
            instance.mark_as_read()
        elif not is_read and instance.is_read:
            instance.is_read = False
            instance.read_at = None
            instance.save(update_fields=["is_read", "read_at"])
        return instance
