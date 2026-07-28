from django.contrib import admin

from .models import (
    Comment,
    CommentReply,
    Like,
    Notification,
    SavedJourney,
)


@admin.action(description="Soft delete selected comments")
def soft_delete_comments(modeladmin, request, queryset):
    queryset.update(is_deleted=True)


@admin.action(description="Restore selected comments")
def restore_comments(modeladmin, request, queryset):
    queryset.update(is_deleted=False)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "journey_update",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "journey_update__title",
    )

    list_filter = ("created_at",)

    autocomplete_fields = (
        "user",
        "journey_update",
    )

    list_select_related = (
        "user",
        "journey_update",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "created_by",
    )

    ordering = ("-created_at",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "journey_update",
        "short_content",
        "is_deleted",
        "created_at",
    )

    search_fields = (
        "content",
        "user__username",
        "journey_update__title",
    )

    list_filter = (
        "is_deleted",
        "created_at",
    )

    autocomplete_fields = (
        "user",
        "journey_update",
        "deleted_by",
    )

    list_select_related = (
        "user",
        "journey_update",
        "deleted_by",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "created_by",
    )

    actions = (
        soft_delete_comments,
        restore_comments,
    )

    fieldsets = (
        (
            "Comment",
            {
                "fields": (
                    "user",
                    "journey_update",
                    "content",
                )
            },
        ),
        (
            "Soft Delete",
            {
                "fields": (
                    "is_deleted",
                    "deleted_at",
                    "deleted_by",
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

    @admin.display(description="Content")
    def short_content(self, obj):
        return obj.content[:60] + "..." if len(obj.content) > 60 else obj.content


@admin.register(CommentReply)
class CommentReplyAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "comment",
        "short_content",
        "is_deleted",
        "created_at",
    )

    search_fields = (
        "content",
        "user__username",
        "comment__content",
    )

    list_filter = (
        "is_deleted",
        "created_at",
    )

    autocomplete_fields = (
        "user",
        "comment",
        "deleted_by",
    )

    list_select_related = (
        "user",
        "comment",
        "deleted_by",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "created_by",
    )

    actions = (
        soft_delete_comments,
        restore_comments,
    )

    fieldsets = (
        (
            "Reply",
            {
                "fields": (
                    "comment",
                    "user",
                    "content",
                )
            },
        ),
        (
            "Soft Delete",
            {
                "fields": (
                    "is_deleted",
                    "deleted_at",
                    "deleted_by",
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

    @admin.display(description="Content")
    def short_content(self, obj):
        return obj.content[:60] + "..." if len(obj.content) > 60 else obj.content


@admin.register(SavedJourney)
class SavedJourneyAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "journey",
        "created_at",
    )

    search_fields = (
        "user__username",
        "user__email",
        "journey__title",
    )

    autocomplete_fields = (
        "user",
        "journey",
    )

    list_select_related = (
        "user",
        "journey",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "created_by",
    )

    ordering = ("-created_at",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        "recipient",
        "actor",
        "notification_type",
        "title",
        "is_read",
        "created_at",
    )

    search_fields = (
        "recipient__username",
        "recipient__email",
        "actor__username",
        "actor__email",
        "title",
        "body",
    )

    list_filter = (
        "notification_type",
        "is_read",
        "created_at",
    )

    autocomplete_fields = (
        "recipient",
        "actor",
    )

    raw_id_fields = ("content_type",)

    list_select_related = (
        "recipient",
        "actor",
        "content_type",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "created_by",
        "read_at",
    )

    ordering = ("-created_at",)

    fieldsets = (
        (
            "Notification",
            {
                "fields": (
                    "recipient",
                    "actor",
                    "notification_type",
                    "title",
                    "body",
                )
            },
        ),
        (
            "Target",
            {
                "fields": (
                    "content_type",
                    "object_id",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "is_read",
                    "read_at",
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
