import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_stripped_text(value, min_length=1, field_name="This field"):
    """
    Strip whitespace and enforce minimum length.
    This prevents "   " from passing validation.
    """
    if not value:
        raise ValidationError(_(f"{field_name} cannot be empty."))

    value = value.strip()
    if len(value) < min_length:
        raise ValidationError(
            _(f"{field_name} must contain at least {min_length} character(s).")
        )
    return value


def validate_cloudinary_public_id(value):
    """Ensure the public_id is valid Cloudinary format."""
    if not value or not value.strip():
        raise ValidationError(_("Cloudinary public ID cannot be empty."))

    pattern = r"^[a-zA-Z0-9_\-/]+$"
    if not re.match(pattern, value):
        raise ValidationError(_("Cloudinary public ID contains invalid characters."))
    return value


def validate_image_order(order_list, max_count=None):
    """
    Ensure order indices are a sequence of unique integers starting from 0.
    """
    if not order_list:
        return

    unique = set(order_list)
    if len(unique) != len(order_list):
        raise ValidationError(_("Duplicate order indices are not allowed."))

    expected = list(range(len(order_list)))
    if sorted(order_list) != expected:
        raise ValidationError(_(f"Order indices must be a permutation of {expected}."))


def validate_tag_limit(tags, max_tags=5):
    """Enforce maximum number of tags per update."""
    if len(tags) > max_tags:
        raise ValidationError(_(f"You cannot assign more than {max_tags} tags."))


def validate_tag_name(value):
    """Validate tag name format."""
    value = value.strip().lower()
    if not value:
        raise ValidationError(_("Tag name cannot be empty."))

    if len(value) > 50:
        raise ValidationError(_("Tag name cannot exceed 50 characters."))

    reserved = ["delete", "update", "all", "admin", "system"]
    if value in reserved:
        raise ValidationError(_(f"'{value}' is a reserved tag name."))

    if not re.match(r"^[a-zA-Z0-9\s\-]+$", value):
        raise ValidationError(
            _("Tag name can only contain letters, numbers, spaces, and hyphens.")
        )

    return value


def validate_cover_image(image):
    """Validate cover image size and format."""
    if image.size > 5 * 1024 * 1024:  # 5MB
        raise ValidationError(_("Cover image size cannot exceed 5 MB."))

    allowed = ["image/jpeg", "image/png", "image/webp"]
    if image.content_type not in allowed:
        raise ValidationError(_("Only JPEG, PNG, and WEBP images are allowed."))


def validate_progress_percentage(value):
    """Validate progress is between 0 and 100."""
    if value < 0 or value > 100:
        raise ValidationError(_("Progress must be between 0 and 100."))
    return value
