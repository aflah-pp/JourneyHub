from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("verify-email/", views.VerifyEmailView.as_view(), name="verify-email"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("refresh/", TokenRefreshView.as_view(), name="refresh"),
    path(
        "password/forgot/", views.ForgotPasswordView.as_view(), name="password-forgot"
    ),
    path(
        "password/reset/<uidb64>/<token>/",
        views.ResetPasswordView.as_view(),
        name="password-reset",
    ),
    path(
        "password/change/", views.ChangePasswordView.as_view(), name="password-change"
    ),
    path("me/", views.MeView.as_view(), name="me"),
    path("users/<str:username>/", views.UserProfileView.as_view(), name="user-profile"),
    path("users/search/", views.UserSearchView.as_view(), name="user-search"),
    path("users/<uuid:user_id>/follow/", views.FollowView.as_view(), name="follow"),
    path(
        "users/<uuid:user_id>/unfollow/", views.UnfollowView.as_view(), name="unfollow"
    ),
    path("preferences/", views.UserPreferenceView.as_view(), name="preferences"),
]
