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

        if request and request.user.is_authenticated:
            if not self.pk and not self.created_by_id:
                self.created_by = request.user
        self.updated_by = request.user

        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class UUIDPrimaryKeyMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True
