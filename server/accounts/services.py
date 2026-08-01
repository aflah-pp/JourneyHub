import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.exceptions import ValidationError

from audit.models import ReportedItem
from journey.models import Journey
from reaction.models import (
    Comment,
    CommentReply,
    Like,
    Notification,
    SavedJourney,
    SavedUpdate,
)
from score.models import BuilderScore, BuilderScoreHistory
from shared.services.email import EmailService
from shared.services.jwt import JWTService

from .models import Follower, Profile, User

logger = logging.getLogger(__name__)


class AccountService:
    """Handles authentication and account management."""

    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION = timedelta(minutes=30)

    @staticmethod
    def login(login, password, ip_address=None):
        """Authenticate user with rate limiting and lockout."""
        user = User.objects.filter(username__iexact=login).first()
        if not user:
            user = User.objects.filter(email__iexact=login).first()

        if not user:
            logger.warning(f"Login attempt with non-existent user: {login}")
            raise ValidationError({"login": "Invalid credentials."})

        if user.locked_until and user.locked_until > timezone.now():
            remaining = user.locked_until - timezone.now()
            raise ValidationError(
                {
                    "login": f"Account locked. Try again in {remaining.seconds // 60} minutes."
                }
            )

        if not user.is_active:
            raise ValidationError({"login": "Account is deactivated."})

        if user.is_suspended:
            raise ValidationError(
                {
                    "login": f"Account suspended. Reason: {user.suspension_reason or 'Contact support.'}"
                }
            )

        authenticated_user = authenticate(
            username=user.username,
            password=password,
        )

        if authenticated_user is None:
            user.failed_login_attempts = F("failed_login_attempts") + 1
            user.save(update_fields=["failed_login_attempts"])
            user.refresh_from_db()

            if user.failed_login_attempts >= AccountService.MAX_FAILED_ATTEMPTS:
                user.locked_until = timezone.now() + AccountService.LOCKOUT_DURATION
                user.save(update_fields=["locked_until"])
                logger.warning(f"Account locked for user {user.username}")
                raise ValidationError(
                    {
                        "login": f"Too many failed attempts. Account locked for {AccountService.LOCKOUT_DURATION.seconds // 60} minutes."
                    }
                )

            raise ValidationError({"login": "Invalid credentials."})

        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_ip = ip_address
        user.last_login = timezone.now()
        user.save(
            update_fields=[
                "failed_login_attempts",
                "locked_until",
                "last_login_ip",
                "last_login",
            ]
        )

        tokens = JWTService.create_tokens(user)

        return user, tokens

    @staticmethod
    def change_password(user, old_password, new_password):
        """Change user password with validation."""
        if not user.check_password(old_password):
            raise ValidationError({"old_password": "Incorrect current password."})

        validate_password(new_password, user)

        user.set_password(new_password)
        user.save(update_fields=["password"])

        logger.info(f"Password changed for user {user.username}")
        return True

    @staticmethod
    def verify_email(user):
        """Mark user as verified."""
        user.is_verified = True
        user.save(update_fields=["is_verified"])
        logger.info(f"Email verified for user {user.username}")
        return user

    @staticmethod
    def resend_verification(user):
        """Resend verification email."""

        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        verify_link = f"{settings.FRONTEND_VERIFY_EMAIL_URL}?uid={uid}&token={token}"

        EmailService.send(
            subject="Verify Your Email",
            template_name="email_verification.html",
            context={
                "user": user,
                "verify_link": verify_link,
            },
            recipient=user.email,
        )

    @staticmethod
    @transaction.atomic
    def clear_user_data(user):
        """Delete all user-generated content but keep the account."""

        Journey.objects.filter(owner=user).delete()

        Like.objects.filter(user=user).delete()

        Comment.objects.filter(user=user).delete()

        CommentReply.objects.filter(user=user).delete()

        SavedUpdate.objects.filter(user=user).delete()
        SavedJourney.objects.filter(user=user).delete()

        Notification.objects.filter(recipient=user).delete()
        Notification.objects.filter(actor=user).delete()

        ReportedItem.objects.filter(reporter=user).delete()

        profile = user.profile
        profile.bio = ""
        profile.avatar_url = None
        profile.avatar_public_id = None
        profile.location = ""
        profile.website = None
        profile.what_i_do = ""
        profile.following_count = 0
        profile.follower_count = 0
        profile.journey_count = 0
        profile.save()

        BuilderScore.objects.filter(user=user).delete()
        BuilderScoreHistory.objects.filter(user=user).delete()

        prefs = user.settings
        prefs.show_email = False
        prefs.show_full_name = True
        prefs.email_notifications = True
        prefs.show_activity_status = True
        prefs.allow_direct_messages = True
        prefs.save()

        user.following_relations.all().delete()
        user.follower_relations.all().delete()

        # ActivityLog.objects.filter(user=user).delete()

        return True


class FollowService:
    """Handles follow/unfollow operations."""

    @staticmethod
    @transaction.atomic
    def follow(follower, following):
        """Follow a user with race-condition-safe counter updates."""
        if Follower.objects.filter(
            follower=follower,
            following=following,
        ).exists():
            raise ValidationError({"detail": "You are already following this user."})

        Follower.objects.create(
            follower=follower,
            following=following,
        )

        Profile.objects.filter(user=follower).update(
            following_count=F("following_count") + 1
        )
        Profile.objects.filter(user=following).update(
            follower_count=F("follower_count") + 1
        )

        # TODO - Create Notification here!!
        return True

    @staticmethod
    @transaction.atomic
    def unfollow(follower, following):
        """Unfollow a user with race-condition-safe counter updates."""
        deleted_count, _ = Follower.objects.filter(
            follower=follower,
            following=following,
        ).delete()

        if deleted_count == 0:
            raise ValidationError({"detail": "You are not following this user."})

        Profile.objects.filter(user=follower).update(
            following_count=F("following_count") - 1
        )
        Profile.objects.filter(user=following).update(
            follower_count=F("follower_count") - 1
        )

        return True

    @staticmethod
    def is_following(follower, following):
        """Check if a user follows another."""
        return Follower.objects.filter(
            follower=follower,
            following=following,
        ).exists()
