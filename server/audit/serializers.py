from rest_framework import serializers

from accounts.serializers import MiniUserSerializer
from shared.services.html_sanitizer import sanitize_html

from .models import ActivityLog, ContentType, ReportedItem, ReportReason, ReportStatus


class ReportedItemSerializer(serializers.ModelSerializer):
    """Full detail of a report."""

    reporter = MiniUserSerializer(read_only=True)
    moderator = MiniUserSerializer(read_only=True)
    target_type = serializers.SerializerMethodField()
    target_id = serializers.UUIDField(source="object_id", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    reason_label = serializers.CharField(source="get_reason_display", read_only=True)

    class Meta:
        model = ReportedItem
        fields = (
            "id",
            "reporter",
            "target_type",
            "target_id",
            "reason",
            "reason_label",
            "description",
            "status",
            "status_label",
            "moderator",
            "resolved_at",
            "resolution_note",
            "ip_address",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields

    def get_target_type(self, obj):
        return obj.content_type.model


class ReportCreateSerializer(serializers.ModelSerializer):
    """Payload for creating a report."""

    reason = serializers.ChoiceField(choices=ReportReason.choices)
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )
    content_type = serializers.CharField(write_only=True)
    object_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = ReportedItem
        fields = ("reason", "description", "content_type", "object_id")

    def validate_description(self, value):
        """Sanitize description to prevent XSS."""
        if value:
            return sanitize_html(value.strip())
        return value

    def validate(self, attrs):
        """Validate that the target exists."""
        content_type_key = attrs.get("content_type")
        object_id = attrs.get("object_id")

        model_map = {
            "user": "accounts.User",
            "journey": "journey.Journey",
            "journeyupdate": "journey.JourneyUpdate",
            "comment": "reaction.Comment",
            "commentreply": "reaction.CommentReply",
        }

        model_path = model_map.get(content_type_key)
        if not model_path:
            raise serializers.ValidationError(
                f"Invalid content_type. Allowed: {list(model_map.keys())}"
            )

        from django.apps import apps

        try:
            model = apps.get_model(model_path)
        except LookupError:
            raise serializers.ValidationError("Content type not found.")

        try:
            target = model.objects.get(id=object_id)
        except model.DoesNotExist:
            raise serializers.ValidationError("Target object does not exist.")

        attrs["_target"] = target
        return attrs

    def create(self, validated_data):
        validated_data["reporter"] = self.context["request"].user
        target = validated_data.pop("_target")
        validated_data["content_type"] = ContentType.objects.get_for_model(target)
        validated_data["object_id"] = target.pk
        return super().create(validated_data)


class ReportResolveSerializer(serializers.Serializer):
    """Payload for resolving a report."""

    status = serializers.ChoiceField(
        choices=[ReportStatus.RESOLVED, ReportStatus.DISMISSED]
    )
    note = serializers.CharField(
        required=False,
        allow_blank=True,
    )

    def validate_note(self, value):
        """Sanitize note to prevent XSS."""
        if value:
            return sanitize_html(value.strip())
        return value


class ReportUpdateStatusSerializer(serializers.Serializer):
    """Payload for updating report status."""

    status = serializers.ChoiceField(
        choices=[ReportStatus.UNDER_REVIEW, ReportStatus.NEEDS_INFO]
    )
    note = serializers.CharField(
        required=False,
        allow_blank=True,
    )


class ActivityLogSerializer(serializers.ModelSerializer):
    """Read-only representation of an activity log."""

    user = MiniUserSerializer(read_only=True)
    target_type = serializers.SerializerMethodField()
    target_id = serializers.UUIDField(source="object_id", read_only=True)
    action_label = serializers.CharField(
        source="get_action_type_display",
        read_only=True,
    )

    class Meta:
        model = ActivityLog
        fields = (
            "id",
            "user",
            "action_type",
            "action_label",
            "target_type",
            "target_id",
            "ip_address",
            "user_agent",
            "request_path",
            "request_method",
            "metadata",
            "created_at",
        )
        read_only_fields = fields

    def get_target_type(self, obj):
        return obj.content_type.model if obj.content_type else None
