import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from audit.models import ActivityLog
from audit.service import ActivityLogService
from shared.responses import APIResponse
from shared.services.cookies import CookieService
from shared.services.email import EmailService
from shared.services.jwt import JWTService
from shared.throttles import (
    LoginRateThrottle,
    PasswordResetRateThrottle,
    RegistrationRateThrottle,
)

from .serializers import (
    ChangePasswordSerializer,
    EmailVerificationSerializer,
    FollowSerializer,
    ForgotPasswordSerializer,
    LoginSerializer,
    MeUpdateSerializer,
    MiniUserSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    UserPreferenceSerializer,
    UserProfileSerializer,
)
from .services import AccountService, FollowService

User = get_user_model()
logger = logging.getLogger(__name__)


@extend_schema(
    tags=["Authentication"], summary="User registration with email verification"
)
class RegisterView(APIView):
    """
    User registration with email verification.
    """

    permission_classes = [AllowAny]
    throttle_classes = [RegistrationRateThrottle]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        ActivityLogService.log_activity(
            user=user,
            action_type=ActivityLog.ActionType.REGISTER,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            request_path=request.path,
            request_method=request.method,
            metadata={
                "user_id": str(user.id),
                "username": user.username,
                "email": user.email,
            },
        )

        try:
            AccountService.resend_verification(user)
        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
            # ? Here made user can register without verifying email which mean they can verify later.

        return APIResponse(
            message="Registration successful. Please check your email to verify your account.",
            data={
                "id": str(user.id),
                "username": user.username,
                "email": user.email,
                "requires_verification": True,
            },
            status_code=201,
        )


@extend_schema(tags=["Authentication"], summary="Verify user email with token")
class VerifyEmailView(APIView):
    """
    Verify user email with token.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        token = serializer.validated_data["token"]

        try:
            parts = token.split("-")
            if len(parts) != 2:
                raise ValueError("Invalid token format")

            uid = parts[0]
            token_value = parts[1]

            uid = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return APIResponse(
                message="Invalid verification token.",
                status_code=400,
                is_success=False,
            )

        if not default_token_generator.check_token(user, token_value):
            return APIResponse(
                message="Invalid or expired verification token.",
                status_code=400,
                is_success=False,
            )

        if user.is_verified:
            return APIResponse(
                message="Email already verified.",
                status_code=200,
            )

        AccountService.verify_email(user)

        ActivityLogService.log_activity(
            user=user,
            action_type=ActivityLog.ActionType.VERIFY_EMAIL,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            request_path=request.path,
            request_method=request.method,
            metadata={
                "user_id": str(user.id),
                "username": user.username,
            },
        )

        return APIResponse(
            message="Email verified successfully.",
            status_code=200,
        )


@extend_schema(tags=["Authentication"], summary="User login with JWT tokens")
class LoginView(APIView):
    """
    User login with JWT tokens.
    """

    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ip_address = request.META.get("REMOTE_ADDR")

        user, tokens = AccountService.login(
            serializer.validated_data["login"],
            serializer.validated_data["password"],
            ip_address=ip_address,
        )

        ActivityLogService.log_activity(
            user=user,
            action_type=ActivityLog.ActionType.LOGIN,
            ip_address=ip_address,
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            request_path=request.path,
            request_method=request.method,
            metadata={
                "user_id": str(user.id),
                "username": user.username,
            },
        )

        response = APIResponse(
            message="Login successful.",
            data={
                "access": tokens["access"],
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "email": user.email,
                    "is_verified": user.is_verified,
                },
            },
        )

        CookieService.set_refresh_cookie(response, tokens["refresh"])

        return response


@extend_schema(tags=["Authentication"], summary="User logout with token blacklisting")
class LogoutView(APIView):
    """
    User logout with token blacklisting.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        ActivityLogService.log_activity(
            user=request.user,
            action_type=ActivityLog.ActionType.LOGOUT,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            request_path=request.path,
            request_method=request.method,
            metadata={
                "user_id": str(request.user.id),
                "username": request.user.username,
            },
        )

        refresh_token = CookieService.get_refresh_cookie(request)
        if refresh_token:
            JWTService.blacklist_refresh_token(refresh_token)

        response = APIResponse(message="Logout successful.")
        CookieService.clear_refresh_cookie(response)

        return response


@extend_schema(
    tags=["Password Management"], summary="Send password reset link via email"
)
class ForgotPasswordView(APIView):
    """
    Send password reset link via email.
    """

    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetRateThrottle]

    def post(self, request):
        serializer = ForgotPasswordSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        email_exists = serializer.context.get("email_exists", False)

        if email_exists:
            try:
                user = User.objects.get(email__iexact=email)
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                reset_link = (
                    f"{settings.FRONTEND_RESET_PASSWORD_URL}"
                    f"?uid={uid}&token={token}"
                )

                EmailService.send(
                    subject="Password Reset Request",
                    template_name="password_reset.html",
                    context={
                        "user": user,
                        "reset_link": reset_link,
                    },
                    recipient=user.email,
                )

                logger.info(f"Password reset link sent to {email}")
            except Exception as e:
                logger.error(f"Failed to send password reset email: {str(e)}")

        return APIResponse(
            message="If an account exists with this email, a password reset link has been sent.",
        )


@extend_schema(tags=["Password Management"], summary="Reset password with token")
class ResetPasswordView(APIView):
    """
    Reset password with token.
    """

    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is None or not default_token_generator.check_token(user, token):
            return APIResponse(
                message="Invalid or expired reset link.",
                status_code=400,
                is_success=False,
            )

        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.set_password(serializer.validated_data["password"])
        user.save(update_fields=["password"])

        JWTService.blacklist_all_user_tokens(user)

        ActivityLogService.log_activity(
            user=user,
            action_type=ActivityLog.ActionType.PASSWORD_RESET,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            request_path=request.path,
            request_method=request.method,
            metadata={
                "user_id": str(user.id),
                "username": user.username,
            },
        )

        logger.info(f"Password reset successful for {user.username}")

        return APIResponse(
            message="Password reset successfully.",
        )


@extend_schema(
    tags=["Password Management"], summary="Change password for authenticated user"
)
class ChangePasswordView(APIView):
    """
    Change password for authenticated user.
    """

    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        AccountService.change_password(
            request.user,
            serializer.validated_data["old_password"],
            serializer.validated_data["new_password"],
        )

        ActivityLogService.log_activity(
            user=request.user,
            action_type=ActivityLog.ActionType.PASSWORD_CHANGE,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            request_path=request.path,
            request_method=request.method,
            metadata={
                "user_id": str(request.user.id),
                "username": request.user.username,
            },
        )

        return APIResponse(
            message="Password changed successfully.",
        )


@extend_schema(tags=["User Profile"])
class MeView(APIView):
    """
    Retrieve and update authenticated user's profile.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(
            request.user,
            context={"request": request},
        )
        return APIResponse(
            message="Profile retrieved successfully.",
            data=serializer.data,
        )

    @transaction.atomic
    def patch(self, request):
        serializer = MeUpdateSerializer(
            instance=request.user,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return APIResponse(
            message="Profile updated successfully.",
            data=UserProfileSerializer(
                user,
                context={"request": request},
            ).data,
        )


@extend_schema(tags=["User Profile"])
class UserProfileView(APIView):
    """
    Get public user profile.
    """

    permission_classes = [AllowAny]

    def get(self, request, username):
        user = get_object_or_404(User, username=username)

        serializer = UserProfileSerializer(
            user,
            context={"request": request},
        )

        return APIResponse(
            message="User profile retrieved successfully.",
            data=serializer.data,
        )


@extend_schema(tags=["User Profile"])
class UserSearchView(APIView):
    """
    Search users by username.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get("q", "").strip()

        if not query:
            return APIResponse(
                message="Search query required.",
                data=[],
                status_code=400,
            )

        try:
            user = User.objects.get(username__iexact=query)
            serializer = MiniUserSerializer(user, context={"request": request})
            return APIResponse(
                message="User found.",
                data=serializer.data,
            )
        except User.DoesNotExist:
            pass

        users = User.objects.filter(username__icontains=query).select_related(
            "profile"
        )[:10]

        serializer = MiniUserSerializer(users, many=True, context={"request": request})
        return APIResponse(
            message="Search results.",
            data=serializer.data,
        )


@extend_schema(tags=["User Profile"])
class FollowView(APIView):
    """
    Follow a user.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        following = get_object_or_404(User, pk=user_id)

        serializer = FollowSerializer(
            data={},
            context={
                "request": request,
                "following": following,
            },
        )
        serializer.is_valid(raise_exception=True)

        FollowService.follow(
            follower=request.user,
            following=following,
        )

        return APIResponse(
            message="User followed successfully.",
        )


@extend_schema(tags=["User Profile"])
class UnfollowView(APIView):
    """
    Unfollow a user.
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request, user_id):
        following = get_object_or_404(User, pk=user_id)

        FollowService.unfollow(
            follower=request.user,
            following=following,
        )

        return APIResponse(
            message="User unfollowed successfully.",
        )


@extend_schema(tags=["User Preferences"])
class UserPreferenceView(APIView):
    """
    Manage user preferences.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserPreferenceSerializer(request.user.settings)
        return APIResponse(
            message="Preferences retrieved successfully.",
            data=serializer.data,
        )

    @transaction.atomic
    def patch(self, request):
        serializer = UserPreferenceSerializer(
            instance=request.user.settings,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return APIResponse(
            message="Preferences updated successfully.",
            data=serializer.data,
        )
