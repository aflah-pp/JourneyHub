import uuid

from django.conf import settings
from django.db import models

from shared.middleware import get_current_request


class TimeStampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated",
    )

    def save(self, *args, **kwargs):
        request = get_current_request()

        user = None
        if request:
            user = getattr(request, "user", None)

        if user and user.is_authenticated:
            if self._state.adding and self.created_by_id is None:
                self.created_by = user

            self.updated_by = user

        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class UUIDPrimaryKeyMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
