from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import F, Value
from django.db.models.functions import Greatest
from django.utils import timezone

from .models import (
    Journey,
    JourneyImage,
    JourneyUpdate,
    JourneyUpdateTag,
    Tag,
)
from .validators import validate_tag_limit, validate_tag_name


class JourneyService:
    """Service layer for Journey operations."""

    @staticmethod
    @transaction.atomic
    def create_journey(user, validated_data):
        validated_data["owner"] = user
        return Journey.objects.create(**validated_data)

    @staticmethod
    @transaction.atomic
    def update_journey(journey, validated_data):
        for attr, value in validated_data.items():
            setattr(journey, attr, value)
        journey.save()
        return journey

    @staticmethod
    @transaction.atomic
    def soft_delete_journey(journey, deleted_by):
        journey.is_deleted = True
        journey.deleted_at = timezone.now()
        journey.deleted_by = deleted_by
        journey.save(update_fields=["is_deleted", "deleted_at", "deleted_by"])

        journey.updates.update(
            is_deleted=True,
            deleted_at=timezone.now(),
            deleted_by=deleted_by,
        )
        return journey

    @staticmethod
    @transaction.atomic
    def increment_update_count(journey):
        journey.update_count = F("update_count") + 1
        journey.save(update_fields=["update_count"])

    @staticmethod
    @transaction.atomic
    def decrement_update_count(journey):
        journey.update_count = Greatest(F("update_count") - 1, Value(0))
        journey.save(update_fields=["update_count"])

    @staticmethod
    @transaction.atomic
    def update_latest_progress(journey, progress_percentage):
        """Update the denormalized latest_progress field."""
        journey.latest_progress = progress_percentage
        journey.save(update_fields=["latest_progress"])


class JourneyUpdateService:
    """Service layer for JourneyUpdate operations."""

    @staticmethod
    @transaction.atomic
    def create_update(journey, validated_data):
        validated_data["journey"] = journey
        update = JourneyUpdate.objects.create(**validated_data)

        JourneyService.increment_update_count(journey)
        JourneyService.update_latest_progress(journey, update.progress_percentage)

        return update

    @staticmethod
    @transaction.atomic
    def update_update(update, validated_data):
        for attr, value in validated_data.items():
            setattr(update, attr, value)
        update.save()

        if "progress_percentage" in validated_data:
            JourneyService.update_latest_progress(
                update.journey, update.progress_percentage
            )

        return update

    @staticmethod
    @transaction.atomic
    def delete_update(update, deleted_by):
        update.is_deleted = True
        update.deleted_at = timezone.now()
        update.deleted_by = deleted_by
        update.save(update_fields=["is_deleted", "deleted_at", "deleted_by"])

        JourneyService.decrement_update_count(update.journey)

        latest_update = (
            update.journey.updates.filter(is_deleted=False)
            .order_by("-created_at")
            .first()
        )
        if latest_update:
            JourneyService.update_latest_progress(
                update.journey, latest_update.progress_percentage
            )
        else:
            JourneyService.update_latest_progress(update.journey, 0)

        return update


class ImageService:
    """Service layer for Image operations with CloudinaryField."""

    @staticmethod
    @transaction.atomic
    def add_image(journey_update, image_data):
        """
        Add image to journey update.
        CloudinaryField auto-uploads when image is set.
        """
        return JourneyImage.objects.create(
            journey_update=journey_update,
            image=image_data.get("image"),
            order_index=image_data.get("order_index", 0),
        )

    @staticmethod
    @transaction.atomic
    def delete_image(image):
        """
        Delete image from Cloudinary and database.
        CloudinaryField auto-deletes from Cloudinary on model delete.
        """

        public_id = image.image.public_id if image.image else None

        image.delete()

        images = JourneyImage.objects.filter(
            journey_update=image.journey_update
        ).order_by("order_index")

        for idx, img in enumerate(images):
            img.order_index = idx
            img.save(update_fields=["order_index"])

        return public_id

    @staticmethod
    @transaction.atomic
    def replace_image(journey_update, old_image, new_image_data):
        """
        Replace an existing image with a new one.
        Handles deleting old image from Cloudinary.
        """
        old_image.delete()

        new_image = JourneyImage.objects.create(
            journey_update=journey_update,
            image=new_image_data.get("image"),
            order_index=new_image_data.get("order_index", 0),
        )

        images = JourneyImage.objects.filter(journey_update=journey_update).order_by(
            "order_index"
        )

        for idx, img in enumerate(images):
            img.order_index = idx
            img.save(update_fields=["order_index"])

        return new_image

    @staticmethod
    @transaction.atomic
    def reorder_images(journey_update, ordered_ids):
        """Reorder images by ID list."""
        images = {
            str(img.id): img
            for img in JourneyImage.objects.filter(journey_update=journey_update)
        }

        if len(ordered_ids) != len(images):
            raise ValidationError("Order list must contain all images.")

        for idx, img_id in enumerate(ordered_ids):
            img = images.get(str(img_id))
            if img is None:
                raise ValidationError(f"Invalid image id: {img_id}")
            img.order_index = idx
            img.save(update_fields=["order_index"])


class TagService:
    """Service layer for Tag operations."""

    @staticmethod
    def get_or_create_tag(name):
        name = name.strip().lower()
        validate_tag_name(name)

        slug = name.replace(" ", "-").lower()

        tag, created = Tag.objects.get_or_create(
            name=name,
            defaults={"slug": slug},
        )
        return tag

    @staticmethod
    @transaction.atomic
    def assign_tags(journey_update, tag_names):
        """Assign tags to an update (replaces all existing tags)."""
        validate_tag_limit(tag_names)

        tags = [TagService.get_or_create_tag(name) for name in tag_names]

        current_relations = JourneyUpdateTag.objects.filter(
            journey_update=journey_update
        )
        current_tag_ids = set(current_relations.values_list("tag_id", flat=True))
        new_tag_ids = set(tag.id for tag in tags)

        to_remove = current_tag_ids - new_tag_ids
        if to_remove:
            JourneyUpdateTag.objects.filter(
                journey_update=journey_update, tag_id__in=to_remove
            ).delete()

        for tag in tags:
            if tag.id not in current_tag_ids:
                JourneyUpdateTag.objects.create(journey_update=journey_update, tag=tag)

        return tags

    @staticmethod
    @transaction.atomic
    def update_usage_count(tag, delta):
        """Update denormalized usage_count."""
        if delta == 1:
            tag.usage_count = F("usage_count") + 1
        elif delta == -1:
            tag.usage_count = Greatest(F("usage_count") - 1, Value(0))
        tag.save(update_fields=["usage_count"])
