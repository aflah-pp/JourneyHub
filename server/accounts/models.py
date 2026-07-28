from cloudinary.models import CloudinaryField
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from shared.models import TimeStampMixin, UUIDPrimaryKeyMixin

from .managers import UserManager
from .validators import validate_count, validate_username


class User(TimeStampMixin, UUIDPrimaryKeyMixin, AbstractUser):
    """
    Base User model with extended fields for JourneyHub.
    """

    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[validate_username],
        db_index=True,
    )
    email = models.EmailField(
        unique=True,
        db_index=True,
    )
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    is_verified = models.BooleanField(
        default=False,
        help_text="Designates whether the user has verified their email.",
    )
    is_suspended = models.BooleanField(
        default=False,
        help_text="Designates whether the user has been suspended by admin.",
    )
    suspension_reason = models.TextField(
        blank=True,
        null=True,
        help_text="Reason for user suspension.",
    )
    suspended_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Timestamp when user was suspended.",
    )

    last_login_ip = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text="IP address of last login.",
    )
    failed_login_attempts = models.IntegerField(
        default=0,
        help_text="Number of consecutive failed login attempts.",
    )
    locked_until = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Account lockout until this timestamp.",
    )

    objects = UserManager()

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["username"]),
            models.Index(fields=["-created_at"]),
            models.Index(fields=["is_verified", "is_active"]),
        ]

    def __str__(self):
        return self.username

    @property
    def is_fully_active(self):
        """Check if user is active, verified, and not suspended."""
        return self.is_active and self.is_verified and not self.is_suspended


class Profile(UUIDPrimaryKeyMixin, TimeStampMixin):
    """
    User profile with extended metadata and denormalized counters.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    bio = models.CharField(
        max_length=250,
        blank=True,
    )

    avatar = CloudinaryField(
        "avatar",
        folder="journeyhub/avatars",
        blank=True,
        null=True,
        transformation={
            "width": 200,
            "height": 200,
            "crop": "fill",
            "quality": "auto",
            "fetch_format": "auto",
        },
    )

    location = models.CharField(
        max_length=100,
        blank=True,
    )
    website = models.URLField(
        blank=True,
        null=True,
    )
    what_i_do = models.CharField(
        max_length=100,
        blank=True,
    )

    following_count = models.IntegerField(
        default=0,
        validators=[validate_count],
    )
    follower_count = models.IntegerField(
        default=0,
        validators=[validate_count],
    )
    journey_count = models.IntegerField(
        default=0,
        validators=[validate_count],
    )

    class Meta:
        db_table = "user_profiles"
        ordering = ["user__username"]

    def __str__(self):
        return self.user.username


class Follower(TimeStampMixin):
    """
    Directed follow graph with self-follow prevention.
    """

    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Follower",
        on_delete=models.CASCADE,
        related_name="following_relations",
        db_index=True,
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="Following",
        on_delete=models.CASCADE,
        related_name="follower_relations",
        db_index=True,
    )

    class Meta:
        db_table = "user_followers"
        unique_together = ("follower", "following")
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["follower"]),
            models.Index(fields=["following"]),
            models.Index(fields=["follower", "following"]),
        ]

    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"


class UserPreference(UUIDPrimaryKeyMixin, TimeStampMixin):
    """
    User privacy and notification preferences.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="settings",
    )
    show_email = models.BooleanField(
        default=False,
        help_text="Display email on public profile.",
    )
    show_full_name = models.BooleanField(
        default=True,
        help_text="Display full name on public profile.",
    )
    email_notifications = models.BooleanField(
        default=True,
        help_text="Receive email notifications.",
    )

    show_activity_status = models.BooleanField(
        default=True,
        help_text="Show when user is online.",
    )
    allow_direct_messages = models.BooleanField(
        default=True,
        help_text="Allow users to send direct messages.",
    )

    class Meta:
        db_table = "user_preferences"
        ordering = ["-created_at"]

    def __str__(self):
        return self.user.username
