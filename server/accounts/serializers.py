from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers

from .models import Follower, Profile, UserPreference
from .validators import validate_email_domain, validate_password_strength

User = get_user_model()


USER_FIELDS = ("first_name", "last_name", "email")
PROFILE_FIELDS = (
    "bio",
    "avatar",
    "location",
    "website",
    "what_i_do",
)


class RegisterSerializer(serializers.ModelSerializer):
    """
    Handles user registration with email verification.
    """

    password = serializers.CharField(
        write_only=True,
        validators=[
            validate_password_strength,
            validate_password,
        ],
    )
    confirm_password = serializers.CharField(
        write_only=True,
    )
    terms_accepted = serializers.BooleanField(
        write_only=True,
        required=True,
        error_messages={
            "required": "You must accept the terms and conditions.",
            "invalid": "You must accept the terms and conditions.",
        },
    )

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "confirm_password",
            "terms_accepted",
        )

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError(
                "A user with this username already exists."
            )
        return value.lower()

    def validate_email(self, value):
        value = value.lower().strip()

        validate_email_domain(value)

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        if password != confirm_password:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop("confirm_password")
        validated_data.pop("terms_accepted")

        password = validated_data.pop("password")

        user = User.objects.create_user(
            password=password,
            is_verified=False,
            **validated_data,
        )

        Profile.objects.create(user=user)
        UserPreference.objects.create(user=user)

        return user


class LoginSerializer(serializers.Serializer):
    """
    Validates login credentials.
    """

    login = serializers.CharField(
        required=True,
        error_messages={"required": "Username or email is required."},
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={"required": "Password is required."},
    )


class EmailVerificationSerializer(serializers.Serializer):
    """
    Validates email verification request.
    """

    token = serializers.CharField(required=True)


class ForgotPasswordSerializer(serializers.Serializer):
    """
    Validates password reset request.
    """

    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        """Check if email exists but don't reveal if it doesn't."""
        value = value.lower().strip()
        self.context["email_exists"] = User.objects.filter(email__iexact=value).exists()

        return value


class ResetPasswordSerializer(serializers.Serializer):
    """
    Validates password reset with token.
    """

    password = serializers.CharField(
        validators=[
            validate_password_strength,
            validate_password,
        ],
        write_only=True,
    )
    confirm_password = serializers.CharField(
        write_only=True,
    )

    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """
    Validates password change for authenticated user.
    """

    old_password = serializers.CharField(
        write_only=True,
        required=True,
    )
    new_password = serializers.CharField(
        validators=[
            validate_password_strength,
            validate_password,
        ],
        write_only=True,
    )
    confirm_password = serializers.CharField(
        write_only=True,
    )

    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    """
    Profile representation with Cloudinary support.
    """

    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            "bio",
            "avatar_url",
            "location",
            "website",
            "what_i_do",
            "following_count",
            "follower_count",
            "journey_count",
        )
        read_only_fields = (
            "following_count",
            "follower_count",
            "journey_count",
        )

    def get_avatar_url(self, obj):
        """Return optimized Cloudinary URL."""
        if obj.avatar:
            return obj.avatar.url.replace(
                "/upload/", "/upload/q_auto,f_auto,w_200,h_200,c_fill/"
            )
        return None


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Combined user and profile representation.
    """

    email = serializers.SerializerMethodField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    profile = ProfileSerializer(read_only=True)
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "profile",
            "is_following",
            "is_verified",
        )

    def _is_owner(self, obj):
        """Check if requesting user is the profile owner."""
        request = self.context.get("request")
        return (
            request is not None
            and request.user.is_authenticated
            and request.user == obj
        )

    def get_email(self, obj):
        """Only show email if owner or preference allows."""
        if self._is_owner(obj):
            return obj.email
        return obj.email if obj.settings.show_email else None

    def get_first_name(self, obj):
        """Only show first name if owner or preference allows."""
        if self._is_owner(obj):
            return obj.first_name
        return obj.first_name if obj.settings.show_full_name else None

    def get_last_name(self, obj):
        """Only show last name if owner or preference allows."""
        if self._is_owner(obj):
            return obj.last_name
        return obj.last_name if obj.settings.show_full_name else None

    def get_is_following(self, obj):
        """Check if requesting user follows this profile."""
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        if request.user == obj:
            return False
        return Follower.objects.filter(
            follower=request.user,
            following=obj,
        ).exists()


class MeUpdateSerializer(serializers.ModelSerializer):
    """
    Update authenticated user and profile.
    """

    USER_FIELDS = USER_FIELDS
    PROFILE_FIELDS = PROFILE_FIELDS

    first_name = serializers.CharField(required=False, max_length=50)
    last_name = serializers.CharField(required=False, max_length=50)
    email = serializers.EmailField(required=False)

    bio = serializers.CharField(required=False, allow_blank=True, max_length=250)
    avatar = serializers.ImageField(required=False, allow_null=True)
    location = serializers.CharField(required=False, allow_blank=True, max_length=100)
    website = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    what_i_do = serializers.CharField(required=False, allow_blank=True, max_length=100)

    class Meta:
        model = User
        fields = (
            *USER_FIELDS,
            *PROFILE_FIELDS,
        )

    def validate_email(self, value):
        value = value.lower().strip()
        validate_email_domain(value)

        if (
            User.objects.exclude(pk=self.instance.pk)
            .filter(email__iexact=value)
            .exists()
        ):
            raise serializers.ValidationError("Email already exists.")
        return value

    @transaction.atomic
    def update(self, instance, validated_data):
        profile = instance.profile

        user_updates = []
        for field in self.USER_FIELDS:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
                user_updates.append(field)

        if user_updates:
            instance.save(update_fields=user_updates)

        profile_updates = []
        for field in self.PROFILE_FIELDS:
            if field in validated_data:
                setattr(profile, field, validated_data[field])
                profile_updates.append(field)

        if profile_updates:
            profile.save(update_fields=profile_updates)

        return instance


class FollowSerializer(serializers.Serializer):
    """
    Validate follow/unfollow request.
    """

    def validate(self, attrs):
        request = self.context["request"]
        following = self.context["following"]

        if request.user == following:
            raise serializers.ValidationError({"detail": "You cannot follow yourself."})

        attrs["follower"] = request.user
        attrs["following"] = following
        return attrs


class UserPreferenceSerializer(serializers.ModelSerializer):
    """
    User preference management.
    """

    class Meta:
        model = UserPreference
        fields = (
            "show_email",
            "show_full_name",
            "email_notifications",
            "show_activity_status",
            "allow_direct_messages",
        )


class MiniUserSerializer(serializers.ModelSerializer):
    """
    Minimal user representation for list views.
    """

    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "avatar_url",
        )
        read_only_fields = fields

    def get_avatar_url(self, obj):
        profile = getattr(obj, "profile", None)
        if profile and profile.avatar:
            return profile.avatar.url.replace(
                "/upload/", "/upload/q_auto,f_auto,w_200,h_200,c_fill/"
            )
        return None
