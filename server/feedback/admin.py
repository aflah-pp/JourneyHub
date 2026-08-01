from django.contrib import admin

from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("subject", "user", "feedback_type", "status", "created_at")
    list_filter = ("feedback_type", "status", "is_anonymous")
    search_fields = ("subject", "message", "user__username")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"
    ordering = ("-created_at",)

    fieldsets = (
        (
            "Feedback",
            {
                "fields": (
                    "user",
                    "feedback_type",
                    "subject",
                    "message",
                    "rating",
                    "is_anonymous",
                )
            },
        ),
        (
            "Status",
            {"fields": ("status", "resolved_at", "resolved_by", "resolution_note")},
        ),
        (
            "Admin",
            {
                "fields": ("admin_notes",),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
