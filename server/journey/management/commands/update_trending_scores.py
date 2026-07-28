from django.core.management.base import BaseCommand
from django.db.models import ExpressionWrapper, F, FloatField, Value
from django.db.models.functions import Now
from django.utils import timezone

from journey.models import JourneyUpdate


class Command(BaseCommand):
    help = "Update trending scores for all journey updates"

    def handle(self, *args, **options):
        self.stdout.write("Updating trending scores...")
        start_time = timezone.now()

        updated_count = JourneyUpdate.objects.filter(
            is_deleted=False,
            journey__is_deleted=False,
        ).update(
            trending_score=ExpressionWrapper(
                (F("like_count") * 2 + F("comment_count") * 3)
                / (
                    ((Now() - F("created_at")) / Value(3600)) ** Value(1.5) + Value(1.0)
                ),
                output_field=FloatField(),
            )
        )

        elapsed = (timezone.now() - start_time).total_seconds()
        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully updated trending scores for {updated_count} updates "
                f"in {elapsed:.2f} seconds."
            )
        )
