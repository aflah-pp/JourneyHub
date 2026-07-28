from django.contrib import admin

from .models import (
    Journey,
    JourneyImage,
    JourneyUpdate,
    JourneyUpdateTag,
    Tag,
)


class JourneyImageInline(admin.TabularInline):
    model = JourneyImage
    extra = 0
    fields = (
        "image",
        "order_index",
        "created_at",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )


class JourneyUpdateTagInline(admin.TabularInline):
    model = JourneyUpdateTag
    extra = 0


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "usage_count",
        "created_at",
    )

    search_fields = (
        "name",
        "slug",
    )

    ordering = (
        "-usage_count",
        "name",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "created_by",
    )


@admin.action(description="Soft delete selected journeys")
def soft_delete(modeladmin, request, queryset):
    queryset.update(is_deleted=True)


@admin.action(description="Restore selected journeys")
def restore(modeladmin, request, queryset):
    queryset.update(is_deleted=False)


@admin.register(Journey)
class JourneyAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "owner",
        "category",
        "status",
        "visibility",
        "latest_progress",
        "update_count",
        "is_deleted",
        "created_at",
    )

    list_filter = (
        "category",
        "status",
        "visibility",
        "is_deleted",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
        "owner__username",
        "owner__email",
    )

    autocomplete_fields = (
        "owner",
        "deleted_by",
    )

    list_select_related = (
        "owner",
        "deleted_by",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "created_by",
    )

    actions = (
        soft_delete,
        restore,
    )

    fieldsets = (
        (
            "Journey",
            {
                "fields": (
                    "owner",
                    "title",
                    "description",
                    "cover_image",
                )
            },
        ),
        (
            "Configuration",
            {
                "fields": (
                    "category",
                    "status",
                    "visibility",
                )
            },
        ),
        (
            "Statistics",
            {
                "fields": (
                    "latest_progress",
                    "update_count",
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


@admin.register(JourneyUpdate)
class JourneyUpdateAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "journey",
        "progress_percentage",
        "milestone_status",
        "help_needed",
        "like_count",
        "comment_count",
        "is_deleted",
        "created_at",
    )

    list_filter = (
        "milestone_status",
        "help_needed",
        "visibility",
        "is_deleted",
        "created_at",
    )

    search_fields = (
        "title",
        "description",
        "journey__title",
        "journey__owner__username",
    )

    autocomplete_fields = (
        "journey",
        "deleted_by",
    )

    list_select_related = (
        "journey",
        "deleted_by",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "created_by",
        "effective_visibility",
    )

    inlines = (
        JourneyImageInline,
        JourneyUpdateTagInline,
    )

    fieldsets = (
        (
            "Update",
            {
                "fields": (
                    "journey",
                    "title",
                    "description",
                )
            },
        ),
        (
            "Progress",
            {
                "fields": (
                    "progress_percentage",
                    "milestone_status",
                    "help_needed",
                )
            },
        ),
        (
            "Visibility",
            {
                "fields": (
                    "visibility",
                    "effective_visibility",
                )
            },
        ),
        (
            "Metrics",
            {
                "fields": (
                    "like_count",
                    "comment_count",
                    "trending_score",
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


@admin.register(JourneyImage)
class JourneyImageAdmin(admin.ModelAdmin):
    list_display = (
        "journey_update",
        "order_index",
        "created_at",
    )

    autocomplete_fields = ("journey_update",)

    list_select_related = ("journey_update",)

    ordering = (
        "journey_update",
        "order_index",
    )

    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
        "created_by",
    )


@admin.register(JourneyUpdateTag)
class JourneyUpdateTagAdmin(admin.ModelAdmin):
    list_display = (
        "journey_update",
        "tag",
        "created_at",
    )

    autocomplete_fields = (
        "journey_update",
        "tag",
    )

    list_select_related = (
        "journey_update",
        "tag",
    )

    search_fields = (
        "journey_update__title",
        "tag__name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "created_by",
    )
