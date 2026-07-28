from django.db import models
from django.db.models import Q


class JourneyQuerySet(models.QuerySet):
    """Custom QuerySet for Journey with visibility filters."""

    def public(self):
        return self.filter(visibility="PUBLIC")

    def active(self):
        return self.filter(status="ACTIVE")

    def not_deleted(self):
        return self.filter(is_deleted=False)

    def owned_by(self, user):
        return self.filter(owner=user)

    def visible_to(self, user):
        """
        Return journeys that a given user is allowed to see.
        Core visibility filter - single source of truth.
        """
        base = self.not_deleted()

        if not user or user.is_anonymous:
            return base.filter(visibility="PUBLIC")

        return base.filter(
            Q(visibility="PUBLIC")
            | Q(visibility="FOLLOWERS", owner__follower_relations__follower=user)
            | Q(owner=user)
        ).distinct()

    def with_update_counts(self):
        """Annotate with update count."""
        return self.annotate(
            update_count=models.Count("updates", filter=Q(updates__is_deleted=False))
        )


class JourneyManager(models.Manager):
    """Custom Manager for"""

    def get_queryset(self):
        return JourneyQuerySet(self.model, using=self._db)

    def public(self):
        return self.get_queryset().public()

    def active(self):
        return self.get_queryset().active()

    def not_deleted(self):
        return self.get_queryset().not_deleted()

    def owned_by(self, user):
        return self.get_queryset().owned_by(user)

    def visible_to(self, user):
        return self.get_queryset().visible_to(user)


class JourneyUpdateQuerySet(models.QuerySet):
    """Custom QuerySet for JourneyUpdate with filters."""

    def not_deleted(self):
        return self.filter(is_deleted=False)

    def for_journey(self, journey):
        return self.filter(journey=journey)

    def with_help_needed(self):
        return self.filter(help_needed=True, is_deleted=False)

    def visible_to(self, user):
        """
        Filter updates based on visibility rules.
        Handles both direct visibility and journey-level
        """
        base = self.not_deleted().select_related("journey")

        if not user or user.is_anonymous:
            return base.filter(
                Q(visibility="PUBLIC")
                | Q(visibility__isnull=True, journey__visibility="PUBLIC")
            )

        return base.filter(
            Q(visibility="PUBLIC")
            | Q(visibility__isnull=True, journey__visibility="PUBLIC")
            | Q(
                visibility="FOLLOWERS",
                journey__owner__follower_relations__follower=user,
            )
            | Q(
                visibility__isnull=True,
                journey__visibility="FOLLOWERS",
                journey__owner__follower_relations__follower=user,
            )
            | Q(journey__owner=user)
        ).distinct()


class JourneyUpdateManager(models.Manager):
    """Custom Manager for JourneyUpdate."""

    def get_queryset(self):
        return JourneyUpdateQuerySet(self.model, using=self._db)

    def not_deleted(self):
        return self.get_queryset().not_deleted()

    def for_journey(self, journey):
        return self.get_queryset().for_journey(journey)

    def with_help_needed(self):
        return self.get_queryset().with_help_needed()

    def visible_to(self, user):
        return self.get_queryset().visible_to(user)
