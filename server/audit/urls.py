from django.urls import path

from .views import (
    ActivityLogDetailView,
    ActivityLogListView,
    ActivityLogStatsView,
    ReportCreateView,
    ReportDetailView,
    ReportListView,
    ReportStatsView,
)

app_name = "audit"

urlpatterns = [
    path("reports/", ReportListView.as_view(), name="report-list"),
    path("reports/create/", ReportCreateView.as_view(), name="report-create"),
    path("reports/<uuid:id>/", ReportDetailView.as_view(), name="report-detail"),
    path("reports/stats/", ReportStatsView.as_view(), name="report-stats"),
    path("activity-logs/", ActivityLogListView.as_view(), name="activity-log-list"),
    path(
        "activity-logs/<uuid:id>/",
        ActivityLogDetailView.as_view(),
        name="activity-log-detail",
    ),
    path(
        "activity-logs/stats/",
        ActivityLogStatsView.as_view(),
        name="activity-log-stats",
    ),
]
