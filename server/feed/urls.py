from django.urls import path

from .views import (
    FollowingFeedView,
    HelpNeededFeedView,
    JourneyTimelineView,
    LatestFeedView,
    TrendingFeedView,
    UserTimelineView,
)

app_name = "feed"

urlpatterns = [
    path("latest/", LatestFeedView.as_view(), name="latest-feed"),
    path("following/", FollowingFeedView.as_view(), name="following-feed"),
    path("trending/", TrendingFeedView.as_view(), name="trending-feed"),
    path("help-needed/", HelpNeededFeedView.as_view(), name="help-needed-feed"),
    path(
        "journeys/<uuid:journey_id>/timeline/",
        JourneyTimelineView.as_view(),
        name="journey-timeline",
    ),
    path(
        "users/<str:username>/timeline/",
        UserTimelineView.as_view(),
        name="user-timeline",
    ),
]
