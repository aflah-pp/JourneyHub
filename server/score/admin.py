from django.contrib import admin

from .models import BuilderScore, BuilderScoreHistory


@admin.register(BuilderScore)
class BuilderScoreAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "total_score",
        "level",
        "rank",
        "consistency_score",
        "engagement_score",
        "milestone_score",
        "influence_score",
        "current_streak",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
    )

    list_filter = (
        "level",
        "created_at",
        "last_activity_at",
    )

    ordering = (
        "-total_score",
        "rank",
    )

    autocomplete_fields = ("user",)

    list_select_related = ("user",)

    readonly_fields = (
        "id",
        "created_by",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "User",
            {"fields": ("user",)},
        ),
        (
            "Scores",
            {
                "fields": (
                    "consistency_score",
                    "engagement_score",
                    "milestone_score",
                    "influence_score",
                    "total_score",
                )
            },
        ),
        (
            "Level",
            {
                "fields": (
                    "level",
                    "experience_points",
                    "next_level_xp",
                    "rank",
                )
            },
        ),
        (
            "Streak",
            {
                "fields": (
                    "current_streak",
                    "longest_streak",
                    "last_activity_at",
                )
            },
        ),
        (
            "Daily Activity",
            {
                "fields": (
                    "last_update_date",
                    "updates_today",
                    "last_comment_date",
                    "comments_today",
                )
            },
        ),
        (
            "Audit",
            {
                "fields": (
                    "created_by",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )


@admin.register(BuilderScoreHistory)
class BuilderScoreHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "category",
        "delta",
        "old_value",
        "new_value",
        "reason",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "reason",
    )

    list_filter = (
        "category",
        "reason",
        "created_at",
    )

    ordering = ("-created_at",)

    autocomplete_fields = ("user",)

    raw_id_fields = ("related_obj_type",)

    list_select_related = (
        "user",
        "related_obj_type",
    )

    readonly_fields = (
        "id",
        "created_by",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Score Change",
            {
                "fields": (
                    "user",
                    "category",
                    "delta",
                    "old_value",
                    "new_value",
                    "reason",
                )
            },
        ),
        (
            "Related Object",
            {
                "fields": (
                    "related_obj_type",
                    "related_obj_id",
                )
            },
        ),
        (
            "Request Metadata",
            {
                "fields": (
                    "user_agent",
                    "ip_address",
                )
            },
        ),
        (
            "Audit",
            {
                "fields": (
                    "created_by",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )
