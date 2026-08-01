from django.urls import path

from .views import FeedbackCreateView, FeedbackDetailView, FeedbackListView

app_name = "feedback"

urlpatterns = [
    path("", FeedbackListView.as_view(), name="feedback-list"),
    path("create/", FeedbackCreateView.as_view(), name="feedback-create"),
    path("<uuid:id>/", FeedbackDetailView.as_view(), name="feedback-detail"),
]
