from django.db import models


class ActiveCommentManager(models.Manager):
    """Returns only non‑deleted comments/replies."""

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class CommentManager(ActiveCommentManager):
    def for_update(self, journey_update):
        return self.get_queryset().filter(journey_update=journey_update)


class CommentReplyManager(ActiveCommentManager):
    def for_comment(self, comment):
        return self.get_queryset().filter(comment=comment)
