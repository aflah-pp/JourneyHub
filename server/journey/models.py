from cloudinary.models import CloudinaryField
from django.core.validators import MaxValueValidator
from django.db import models

from accounts.models import User
from shared.models import TimeStampMixin, UUIDPrimaryKeyMixin

from .managers import JourneyManager, JourneyUpdateManager


class Tag(UUIDPrimaryKeyMixin, TimeStampMixin):
    """Tag model with denormalized usage_count."""

    name = models.CharField(max_length=50, unique=True, db_index=True)
    slug = models.SlugField(max_length=60, unique=True, db_index=True)
    usage_count = models.PositiveIntegerField(default=0, db_index=True)

    class Meta:
        db_table = "journey_tags"
        ordering = ("-usage_count", "name")
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["slug"]),
            models.Index(fields=["-usage_count"]),
        ]

    def __str__(self):
        return self.name


class Journey(UUIDPrimaryKeyMixin, TimeStampMixin):
    """Journey model - the core container for a user's building journey."""

    class Visibility(models.TextChoices):
        PUBLIC = "PUBLIC", "Public"
        FOLLOWERS = "FOLLOWERS", "Followers"
        PRIVATE = "PRIVATE", "Private"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        COMPLETED = "COMPLETED", "Completed"
        PAUSED = "PAUSED", "Paused"
        ABANDONED = "ABANDONED", "Abandoned"

    class Category(models.TextChoices):
        SOFTWARE = "SOFTWARE", "Software"
        STARTUP = "STARTUP", "Startup"
        SKILL = "SKILL", "Skill"
        RESEARCH = "RESEARCH", "Research"
        BOOK = "BOOK", "Book"
        ART = "ART", "Art"
        FITNESS = "FITNESS", "Fitness"
        DIY = "DIY", "DIY"
        CONTENT = "CONTENT", "Content"
        CHALLENGE = "CHALLENGE", "Challenge"
        OTHER = "OTHER", "Other"

    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="journeys",
        db_index=True,
    )
    title = models.CharField(max_length=200, db_index=True)
    category = models.CharField(
        max_length=30,
        choices=Category.choices,
        default=Category.OTHER,
        db_index=True,
    )
    description = models.TextField(blank=True, null=True)
    cover_image = CloudinaryField(
        "cover_image",
        folder="journeyhub/journey-cover",
        blank=True,
        null=True,
        transformation={
            "width": 800,
            "height": 400,
            "crop": "fill",
            "quality": "auto",
            "fetch_format": "auto",
        },
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
        db_index=True,
    )
    visibility = models.CharField(
        max_length=20,
        choices=Visibility.choices,
        default=Visibility.PUBLIC,
        db_index=True,
    )

    latest_progress = models.PositiveSmallIntegerField(default=0)
    update_count = models.PositiveIntegerField(default=0)

    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="deleted_journeys",
    )

    objects = JourneyManager()

    class Meta:
        db_table = "journeys"
        ordering = ("-created_at",)
        verbose_name = "Journey"
        verbose_name_plural = "Journeys"
        indexes = [
            models.Index(fields=["owner", "-created_at"]),
            models.Index(fields=["status", "visibility"]),
            models.Index(fields=["category"]),
            models.Index(fields=["-created_at"]),
            models.Index(fields=["owner", "visibility", "is_deleted"]),
            models.Index(
                name="journey_search_idx",
                fields=["title", "description"],
                condition=models.Q(is_deleted=False),
            ),
        ]

    def __str__(self):
        return self.title

    def is_visible_to(self, user):
        """Check if this journey is visible to a user."""
        if self.is_deleted:
            return False
        if self.visibility == self.Visibility.PUBLIC:
            return True
        if self.visibility == self.Visibility.FOLLOWERS:
            if not user or not user.is_authenticated:
                return False
            if user == self.owner:
                return True
            return user.follower_relations.filter(following=self.owner).exists()
        if self.visibility == self.Visibility.PRIVATE:
            return user == self.owner
        return False


class JourneyUpdate(UUIDPrimaryKeyMixin, TimeStampMixin):
    """Journey Update - individual progress entries within a journey."""

    class MilestoneStatus(models.TextChoices):
        NONE = "NONE", "None"
        MILESTONE = "MILESTONE", "Milestone"
        COMPLETED = "COMPLETED", "Completed"

    journey = models.ForeignKey(
        Journey,
        on_delete=models.CASCADE,
        related_name="updates",
        db_index=True,
    )
    title = models.CharField(max_length=200, db_index=True)
    description = models.TextField(help_text="Sanitized HTML content.")

    progress_percentage = models.PositiveSmallIntegerField(
        default=0,
        validators=[MaxValueValidator(100)],
    )
    milestone_status = models.CharField(
        max_length=20,
        choices=MilestoneStatus.choices,
        default=MilestoneStatus.NONE,
        db_index=True,
    )

    visibility = models.CharField(
        max_length=20,
        choices=Journey.Visibility.choices,
        blank=True,
        null=True,
    )

    help_needed = models.BooleanField(default=False, db_index=True)

    like_count = models.PositiveIntegerField(default=0, db_index=True)
    comment_count = models.PositiveIntegerField(default=0)
    trending_score = models.FloatField(
        default=0,
        db_index=True,
        help_text="Precomputed trending score for feed sorting.",
    )

    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="deleted_updates",
    )

    objects = JourneyUpdateManager()

    class Meta:
        db_table = "journey_updates"
        ordering = ("-created_at",)
        verbose_name = "Journey Update"
        verbose_name_plural = "Journey Updates"
        indexes = [
            models.Index(fields=["journey", "-created_at"]),
            models.Index(fields=["help_needed", "is_deleted"]),
            models.Index(fields=["milestone_status"]),
            models.Index(fields=["-created_at"]),
            models.Index(
                fields=["visibility"],
                condition=models.Q(visibility__isnull=False),
                name="journey_visibility_partial_idx",
            ),
            models.Index(
                fields=["visibility", "is_deleted", "-created_at"],
                name="update_feed_idx",
            ),
            models.Index(
                fields=["-created_at"],
                condition=models.Q(help_needed=True, is_deleted=False),
                name="help_needed_feed_idx",
            ),
            models.Index(
                name="update_search_idx",
                fields=["title", "description"],
                condition=models.Q(is_deleted=False),
            ),
        ]

    def __str__(self):
        return self.title

    @property
    def effective_visibility(self):
        """Return the effective visibility (update override or journey default)."""
        return self.visibility or self.journey.visibility

    def is_visible_to(self, user):
        """Check if this update is visible to a user."""
        if self.is_deleted:
            return False
        visibility = self.effective_visibility

        if visibility == Journey.Visibility.PUBLIC:
            return True
        if visibility == Journey.Visibility.PRIVATE:
            return self.journey.owner == user
        if visibility == Journey.Visibility.FOLLOWERS:
            if user == self.journey.owner:
                return True
            if not user or not user.is_authenticated:
                return False
            return user.follower_relations.filter(following=self.journey.owner).exists()
        return False


class JourneyImage(UUIDPrimaryKeyMixin, TimeStampMixin):
    """Images attached to a journey update (Cloudinary-hosted)."""

    journey_update = models.ForeignKey(
        JourneyUpdate,
        on_delete=models.CASCADE,
        related_name="images",
        db_index=True,
    )
    image = CloudinaryField(
        "image",
        folder="journeyhub/updates",
        blank=True,
        null=True,
        transformation={
            "width": 600,
            "height": 400,
            "crop": "limit",
            "quality": "auto",
            "fetch_format": "auto",
        },
    )
    order_index = models.PositiveSmallIntegerField(default=0, db_index=True)

    class Meta:
        db_table = "journey_images"
        ordering = ("order_index", "created_at")
        verbose_name = "Journey Image"
        verbose_name_plural = "Journey Images"
        indexes = [
            models.Index(fields=["journey_update", "order_index"]),
        ]

    def __str__(self):
        return f"{self.journey_update}'s {self.order_index} image"


class JourneyUpdateTag(TimeStampMixin):
    """Many-to-many relationship between updates and tags."""

    journey_update = models.ForeignKey(
        JourneyUpdate,
        on_delete=models.CASCADE,
        related_name="tags",
        db_index=True,
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name="journey_updates",
        db_index=True,
    )

    class Meta:
        db_table = "journey_update_tags"
        verbose_name = "Journey Update Tag"
        verbose_name_plural = "Journey Update Tags"
        constraints = [
            models.UniqueConstraint(
                fields=("journey_update", "tag"),
                name="unique_journey_update_tag",
            )
        ]
        indexes = [
            models.Index(fields=["tag", "journey_update"]),
        ]

    def __str__(self):
        return f"{self.journey_update.title} - {self.tag.name}"
