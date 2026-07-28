import django_filters

from .models import Journey, JourneyUpdate


class JourneyFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name="status")
    category = django_filters.CharFilter(field_name="category")
    visibility = django_filters.CharFilter(field_name="visibility")
    owner = django_filters.UUIDFilter(field_name="owner__id")
    created_after = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_before = django_filters.DateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )

    class Meta:
        model = Journey
        fields = ["status", "category", "visibility", "owner"]


class JourneyUpdateFilter(django_filters.FilterSet):
    help_needed = django_filters.BooleanFilter(field_name="help_needed")
    milestone_status = django_filters.CharFilter(field_name="milestone_status")
    date = django_filters.DateTimeFilter(field_name="created_at", lookup_expr="date")

    class Meta:
        model = JourneyUpdate
        fields = ["help_needed", "milestone_status"]
