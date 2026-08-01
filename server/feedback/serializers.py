from rest_framework import serializers

from accounts.serializers import MiniUserSerializer

from .models import Feedback, FeedbackStatus, FeedbackType
from .service import FeedbackService


class FeedbackSerializer(serializers.ModelSerializer):
    """Full feedback representation."""

    user = MiniUserSerializer(read_only=True)
    display_username = serializers.CharField(read_only=True)
    feedback_type_label = serializers.CharField(source="get_feedback_type_display", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Feedback
        fields = (
            "id",
            "user",
            "display_username",
            "feedback_type",
            "feedback_type_label",
            "subject",
            "message",
            "rating",
            "status",
            "status_label",
            "is_anonymous",
            "created_at",
            "updated_at",
            "resolved_at",
            "resolved_by",
            "resolution_note",
            "admin_notes",
        )
        read_only_fields = (
            "id",
            "user",
            "created_at",
            "updated_at",
            "resolved_at",
            "resolved_by",
            "status",
        )


class FeedbackCreateSerializer(serializers.ModelSerializer):
    """Payload for creating feedback."""

    feedback_type = serializers.ChoiceField(choices=FeedbackType.choices)
    subject = serializers.CharField(max_length=200)
    message = serializers.CharField()
    rating = serializers.IntegerField(min_value=1, max_value=5, required=False, allow_null=True)
    is_anonymous = serializers.BooleanField(default=False, required=False)

    class Meta:
        model = Feedback
        fields = ("feedback_type", "subject", "message", "rating", "is_anonymous")

    def create(self, validated_data):

        user = self.context["request"].user
        return FeedbackService.create_feedback(user=user, **validated_data)


class FeedbackUpdateSerializer(serializers.ModelSerializer):
    """Payload for updating feedback (admin only)."""

    status = serializers.ChoiceField(choices=FeedbackStatus.choices, required=False)
    admin_notes = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Feedback
        fields = ("status", "admin_notes")
