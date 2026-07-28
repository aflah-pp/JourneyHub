from django.contrib import admin

from .models import ActivityLog, ReportedItem


@admin.action(description="Mark selected reports as Under Review")
def mark_under_review(modeladmin, request, queryset):
    queryset.update(status="UNDER_REVIEW")


@admin.action(description="Mark selected reports as Needs Info")
def mark_needs_info(modeladmin, request, queryset):
    queryset.update(status="NEEDS_INFO")


@admin.register(ReportedItem)
class ReportedItemAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "reporter",
        "content_type",
        "reason",
        "status",
        "moderator",
        "created_at",
        "resolved_at",
    )

    search_fields = (
        "reporter__username",
        "reporter__email",
        "description",
        "resolution_note",
    )

    list_filter = (
        "status",
        "reason",
        "created_at",
        "resolved_at",
    )

    ordering = ("-created_at",)

    autocomplete_fields = (
        "reporter",
        "moderator",
    )

    raw_id_fields = ("content_type",)

    list_select_related = (
        "reporter",
        "moderator",
        "content_type",
    )

    readonly_fields = (
        "id",
        "created_by",
        "created_at",
        "updated_at",
        "resolved_at",
    )

    actions = (
        mark_under_review,
        mark_needs_info,
    )

    fieldsets = (
        (
            "Report",
            {
                "fields": (
                    "reporter",
                    "reason",
                    "description",
                    "status",
                )
            },
        ),
        (
            "Reported Object",
            {
                "fields": (
                    "content_type",
                    "object_id",
                )
            },
        ),
        (
            "Moderation",
            {
                "fields": (
                    "moderator",
                    "resolved_at",
                    "resolution_note",
                )
            },
        ),
        (
            "Request Information",
            {
                "fields": (
                    "ip_address",
                    "user_agent",
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


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "action_type",
        "request_method",
        "request_path",
        "ip_address",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "request_path",
        "ip_address",
        "user_agent",
    )

    list_filter = (
        "action_type",
        "request_method",
        "created_at",
    )

    ordering = ("-created_at",)

    autocomplete_fields = ("user",)

    raw_id_fields = ("content_type",)

    list_select_related = (
        "user",
        "content_type",
    )

    readonly_fields = (
        "id",
        "user",
        "action_type",
        "content_type",
        "object_id",
        "ip_address",
        "user_agent",
        "request_path",
        "request_method",
        "metadata",
        "created_by",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Activity",
            {
                "fields": (
                    "user",
                    "action_type",
                )
            },
        ),
        (
            "Target Object",
            {
                "fields": (
                    "content_type",
                    "object_id",
                )
            },
        ),
        (
            "Request",
            {
                "fields": (
                    "request_method",
                    "request_path",
                    "ip_address",
                    "user_agent",
                )
            },
        ),
        (
            "Metadata",
            {"fields": ("metadata",)},
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

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
