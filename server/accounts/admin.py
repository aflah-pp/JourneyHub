from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Follower, Profile, User, UserPreference


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("-created_at",)

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_verified",
        "is_active",
        "is_suspended",
        "is_staff",
        "created_at",
    )

    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "is_verified",
        "is_suspended",
        "created_at",
    )

    search_fields = (
        "username",
        "email",
        "first_name",
        "last_name",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "last_login",
        "last_login_ip",
        "failed_login_attempts",
    )

    fieldsets = (
        (
            "Account",
            {
                "fields": (
                    "username",
                    "email",
                    "password",
                )
            },
        ),
        (
            "Personal Information",
            {
                "fields": (
                    "first_name",
                    "last_name",
                )
            },
        ),
        (
            "Verification & Status",
            {
                "fields": (
                    "is_verified",
                    "is_active",
                    "is_suspended",
                    "suspension_reason",
                    "suspended_at",
                )
            },
        ),
        (
            "Security",
            {
                "fields": (
                    "last_login_ip",
                    "failed_login_attempts",
                    "locked_until",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Important Dates",
            {
                "fields": (
                    "last_login",
                    "created_at",
                    "created_by",
                    "updated_at",
                    "updated_by",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_verified",
                ),
            },
        ),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "location",
        "what_i_do",
        "follower_count",
        "following_count",
        "journey_count",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "location",
        "what_i_do",
    )

    list_filter = ("created_at",)

    ordering = ("user__username",)

    list_select_related = ("user",)

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )


@admin.register(Follower)
class FollowerAdmin(admin.ModelAdmin):
    list_display = (
        "follower",
        "following",
        "created_at",
    )

    search_fields = (
        "follower__username",
        "following__username",
    )

    list_filter = ("created_at",)

    ordering = ("-created_at",)

    list_select_related = (
        "follower",
        "following",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "show_email",
        "show_full_name",
        "email_notifications",
        "show_activity_status",
        "allow_direct_messages",
    )

    search_fields = (
        "user__username",
        "user__email",
    )

    list_filter = (
        "show_email",
        "show_full_name",
        "email_notifications",
        "show_activity_status",
        "allow_direct_messages",
    )

    list_select_related = ("user",)

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )
