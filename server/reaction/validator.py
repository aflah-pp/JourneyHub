from rest_framework import serializers


def validate_stripped_text(value, min_length=1, field_name="This field"):
    """Strip whitespace and enforce minimum length."""
    if not value:
        raise serializers.ValidationError(f"{field_name} cannot be empty.")

    value = value.strip()
    if len(value) < min_length:
        raise serializers.ValidationError(
            f"{field_name} must contain at least {min_length} character(s)."
        )
    return value


def validate_comment_content(value):
    """
    Validate comment content with additional checks.
    - Strip whitespace
    - Min length check
    - Max length check (already at model level)
    - Optional: Block spam patterns
    """
    value = validate_stripped_text(value, min_length=1, field_name="Comment")

    if len(value) > 0 and value.count(value[0]) / len(value) > 0.8:
        raise serializers.ValidationError(
            "Comment contains too many repetitive characters."
        )

    return value


def validate_notification_type(value):
    """Validate notification type against allowed types."""
    from .models import Notification

    allowed_types = [choice[0] for choice in Notification.Type.choices]
    if value not in allowed_types:
        raise serializers.ValidationError(
            f"Invalid notification type. Allowed: {', '.join(allowed_types)}"
        )
    return value
