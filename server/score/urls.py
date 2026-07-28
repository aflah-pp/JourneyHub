from django.urls import path

from .views import (
    LeaderboardView,
    MyRankView,
    MyScoreView,
    PublicScoreView,
    ScoreHistoryDetailView,
    ScoreHistoryView,
)

app_name = "score"

urlpatterns = [
    path("me/", MyScoreView.as_view(), name="my-score"),
    path("rank/", MyRankView.as_view(), name="my-rank"),
    path("history/", ScoreHistoryView.as_view(), name="score-history"),
    path(
        "history/<uuid:id>/",
        ScoreHistoryDetailView.as_view(),
        name="score-history-detail",
    ),
    path("users/<str:username>/", PublicScoreView.as_view(), name="public-score"),
    path("leaderboard/", LeaderboardView.as_view(), name="leaderboard"),
]
