import re

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_username(value):
    if len(value) < 3:
        raise ValidationError(_("Username must be at least 3 characters long."))

    if len(value) > 30:
        raise ValidationError(_("Username must be at most 30 characters long."))

    pattern = r"^[a-zA-Z0-9_]+$"
    if not re.match(pattern, value):
        raise ValidationError(
            _("Username can only contain letters, numbers, and underscores.")
        )


def validate_password_strength(password):
    if len(password) < 10:
        raise ValidationError(_("Password must contain at least 10 characters."))

    if not re.search(r"[A-Z]", password):
        raise ValidationError(_("Password must contain at least one uppercase letter."))

    if not re.search(r"[a-z]", password):
        raise ValidationError(_("Password must contain at least one lowercase letter."))

    if not re.search(r"[0-9]", password):
        raise ValidationError(_("Password must contain at least one digit."))

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValidationError(
            _("Password must contain at least one special character.")
        )


def validate_count(value):
    if value < 0:
        raise ValidationError(_("Count must be 0 or higher."))


def validate_email_domain(value):
    """Block disposable email domains."""
    blocked_domains = [
        "tempmail.com",
        "throwaway.com",
        "guerrillamail.com",
        "mailinator.com",
        "10minutemail.com",
    ]

    domain = value.split("@")[-1].lower()
    if domain in blocked_domains:
        raise ValidationError(
            _("Email domain not allowed. Please use a permanent email address.")
        )
