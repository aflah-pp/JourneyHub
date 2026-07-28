from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import JourneyUpdateTag
from .service import TagService


@receiver(post_save, sender=JourneyUpdateTag)
def increment_tag_usage(sender, instance, created, **kwargs):
    """Increment tag usage count when a tag is attached."""
    if created:
        TagService.update_usage_count(instance.tag, delta=1)


@receiver(post_delete, sender=JourneyUpdateTag)
def decrement_tag_usage(sender, instance, **kwargs):
    """Decrement tag usage count when a tag is detached."""
    TagService.update_usage_count(instance.tag, delta=-1)
