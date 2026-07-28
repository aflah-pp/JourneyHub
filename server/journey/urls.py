from django.urls import path

from .views import (
    JourneyCreateView,
    JourneyDeleteView,
    JourneyDetailView,
    JourneyImageCreateView,
    JourneyImageDeleteView,
    JourneyImageReorderView,
    JourneyListMyView,
    JourneyListPublicView,
    JourneySearchView,
    JourneyUpdateCreateView,
    JourneyUpdateDeleteView,
    JourneyUpdateDetailView,
    JourneyUpdateListView,
    JourneyUpdateTagsView,
    JourneyUpdateUpdateView,
    JourneyUpdateView,
    TagDetailView,
    TrendingTagsView,
)

app_name = "journey"

urlpatterns = [
    path("", JourneyListPublicView.as_view(), name="journey-list"),
    path("my/", JourneyListMyView.as_view(), name="journey-list-my"),
    path("create/", JourneyCreateView.as_view(), name="journey-create"),
    path("<uuid:id>/", JourneyDetailView.as_view(), name="journey-detail"),
    path("<uuid:id>/update/", JourneyUpdateView.as_view(), name="journey-update"),
    path("<uuid:id>/delete/", JourneyDeleteView.as_view(), name="journey-delete"),
    path(
        "<uuid:journey_id>/updates/",
        JourneyUpdateListView.as_view(),
        name="update-list",
    ),
    path(
        "<uuid:journey_id>/updates/create/",
        JourneyUpdateCreateView.as_view(),
        name="update-create",
    ),
    path(
        "<uuid:journey_id>/updates/<uuid:id>/",
        JourneyUpdateDetailView.as_view(),
        name="update-detail",
    ),
    path(
        "<uuid:journey_id>/updates/<uuid:id>/update/",
        JourneyUpdateUpdateView.as_view(),
        name="update-update",
    ),
    path(
        "<uuid:journey_id>/updates/<uuid:id>/delete/",
        JourneyUpdateDeleteView.as_view(),
        name="update-delete",
    ),
    path(
        "<uuid:journey_id>/updates/<uuid:update_id>/tags/",
        JourneyUpdateTagsView.as_view(),
        name="update-tags",
    ),
    path(
        "updates/<uuid:update_id>/images/create/",
        JourneyImageCreateView.as_view(),
        name="image-create",
    ),
    path(
        "updates/<uuid:update_id>/images/<uuid:id>/delete/",
        JourneyImageDeleteView.as_view(),
        name="image-delete",
    ),
    path(
        "updates/<uuid:update_id>/images/reorder/",
        JourneyImageReorderView.as_view(),
        name="image-reorder",
    ),
    path("search/", JourneySearchView.as_view(), name="journey-search"),
    path("tags/trending/", TrendingTagsView.as_view(), name="trending-tags"),
    path("tags/<slug:slug>/", TagDetailView.as_view(), name="tag-detail"),
]
