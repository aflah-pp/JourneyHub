from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.serializers import MiniUserSerializer
from shared.services.html_sanitizer import sanitize_html

from .models import (
    Journey,
    JourneyImage,
    JourneyUpdate,
    JourneyUpdateTag,
    Tag,
)
from .validators import (
    validate_progress_percentage,
    validate_stripped_text,
    validate_tag_limit,
    validate_tag_name,
)

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    """Read-only representation of a Tag."""

    class Meta:
        model = Tag
        fields = ("id", "name", "slug", "usage_count")
        read_only_fields = fields


class JourneyImageSerializer(serializers.ModelSerializer):
    """Read-only representation of an uploaded image."""

    cloudinary_url = serializers.SerializerMethodField()

    class Meta:
        model = JourneyImage
        fields = ("id", "cloudinary_url", "order_index")
        read_only_fields = fields

    def get_cloudinary_url(self, obj):
        if obj.image:
            return obj.image.url.replace(
                "/upload/", "/upload/q_auto,f_auto,w_600,h_400,c_limit/"
            )
        return None


class JourneyImageCreateSerializer(serializers.ModelSerializer):
    """Write-only serializer for uploading images."""

    image = serializers.ImageField(required=True)

    class Meta:
        model = JourneyImage
        fields = ("image", "order_index")

    def create(self, validated_data):
        return JourneyImage.objects.create(
            journey_update=self.context["journey_update"],
            **validated_data,
        )


class JourneyListSerializer(serializers.ModelSerializer):
    """Lightweight card for journey feed/list view."""

    owner = MiniUserSerializer(read_only=True)
    latest_progress = serializers.IntegerField(read_only=True)
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Journey
        fields = (
            "id",
            "title",
            "category",
            "cover_image_url",
            "status",
            "visibility",
            "update_count",
            "latest_progress",
            "created_at",
            "owner",
        )
        read_only_fields = fields

    def get_cover_image_url(self, obj):
        if obj.cover_image:
            return obj.cover_image.url.replace(
                "/upload/", "/upload/q_auto,f_auto,w_400,h_200,c_fill/"
            )
        return None


class JourneyDetailSerializer(serializers.ModelSerializer):
    """Full detail view of a single journey."""

    owner = MiniUserSerializer(read_only=True)
    latest_progress = serializers.IntegerField(read_only=True)
    cover_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Journey
        fields = (
            "id",
            "title",
            "category",
            "description",
            "cover_image_url",
            "status",
            "visibility",
            "update_count",
            "latest_progress",
            "created_at",
            "updated_at",
            "owner",
        )
        read_only_fields = fields

    def get_cover_image_url(self, obj):
        if obj.cover_image:
            return obj.cover_image.url.replace(
                "/upload/", "/upload/q_auto,f_auto,w_800,h_400,c_fill/"
            )
        return None


class JourneyCreateSerializer(serializers.ModelSerializer):
    """Payload for creating a new journey."""

    cover_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Journey
        fields = ("title", "category", "description", "cover_image", "visibility")
        read_only_fields = ("status", "update_count", "latest_progress")

    def validate_title(self, value):
        return validate_stripped_text(value, 3, "Title")

    def validate_description(self, value):
        if value:
            return sanitize_html(value.strip())
        return value

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)


class JourneyUpdateSerializer(serializers.ModelSerializer):
    """Payload for updating a journey."""

    class Meta:
        model = Journey
        fields = (
            "title",
            "category",
            "description",
            "status",
            "visibility",
        )

    def validate_title(self, value):
        return validate_stripped_text(value, 3, "Title")

    def validate_description(self, value):
        if value:
            return sanitize_html(value.strip())
        return value


class JourneyUpdateTagSerializer(serializers.ModelSerializer):
    """Tag attached to a journey update."""

    class Meta:
        model = JourneyUpdateTag
        fields = ("id", "tag")
        read_only_fields = fields

    def to_representation(self, instance):
        return TagSerializer(instance.tag).data


class JourneyUpdateListSerializer(serializers.ModelSerializer):
    """Lightweight card for journey update feed."""

    image = serializers.SerializerMethodField()
    comment_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = JourneyUpdate
        fields = (
            "id",
            "title",
            "milestone_status",
            "help_needed",
            "progress_percentage",
            "like_count",
            "comment_count",
            "created_at",
            "image",
        )
        read_only_fields = fields

    def get_image(self, obj):
        image = obj.images.first()
        return JourneyImageSerializer(image).data if image else None


class JourneyUpdateDetailSerializer(serializers.ModelSerializer):
    """
    Full detail view of a journey update.

    Note: Comments and accepted_solution are now handled by the reaction app.
    """

    images = JourneyImageSerializer(many=True, read_only=True)
    tags = JourneyUpdateTagSerializer(many=True, read_only=True)
    effective_visibility = serializers.CharField(read_only=True)

    like_count = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = JourneyUpdate
        fields = (
            "id",
            "title",
            "description",
            "progress_percentage",
            "milestone_status",
            "help_needed",
            "visibility",
            "effective_visibility",
            "like_count",
            "comment_count",
            "created_at",
            "updated_at",
            "images",
            "tags",
        )
        read_only_fields = fields


class JourneyUpdateCreateSerializer(serializers.ModelSerializer):
    """Payload for creating a journey update."""

    class Meta:
        model = JourneyUpdate
        fields = (
            "title",
            "description",
            "progress_percentage",
            "milestone_status",
            "help_needed",
            "visibility",
        )

    def validate_title(self, value):
        return validate_stripped_text(value, 3, "Title")

    def validate_description(self, value):
        value = validate_stripped_text(value, 10, "Description")
        return sanitize_html(value)

    def validate_progress_percentage(self, value):
        return validate_progress_percentage(value)

    def create(self, validated_data):
        validated_data["journey"] = self.context["journey"]
        return super().create(validated_data)


class JourneyUpdateUpdateSerializer(serializers.ModelSerializer):
    """Payload for updating a journey update."""

    class Meta:
        model = JourneyUpdate
        fields = (
            "title",
            "description",
            "progress_percentage",
            "milestone_status",
            "help_needed",
            "visibility",
        )

    def validate_title(self, value):
        return validate_stripped_text(value, 3, "Title")

    def validate_description(self, value):
        if value:
            return sanitize_html(value.strip())
        return value

    def validate_progress_percentage(self, value):
        return validate_progress_percentage(value)


class UpdateTagsSerializer(serializers.Serializer):
    """Payload for updating tags on an update."""

    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=True,
    )

    def validate_tags(self, value):
        validate_tag_limit(value)
        for tag in value:
            validate_tag_name(tag)
        return value


class TrendingTagsSerializer(serializers.ModelSerializer):
    """Trending tags with usage count."""

    class Meta:
        model = Tag
        fields = ("id", "name", "slug", "usage_count")
        read_only_fields = fields
