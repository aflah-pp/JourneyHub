from django.urls import path

from .views import (
    AcceptedSolutionCreateView,
    AcceptedSolutionDetailView,
    AcceptedSolutionRemoveView,
    CommentCreateView,
    CommentDetailView,
    CommentListView,
    CommentReplyCreateView,
    CommentReplyDetailView,
    CommentReplyListView,
    LikeCreateView,
    LikeDeleteView,
    NotificationDetailView,
    NotificationListView,
    NotificationMarkAllReadView,
    NotificationUnreadCountView,
    SavedJourneyCreateView,
    SavedJourneyDeleteView,
    SavedJourneyListView,
    SavedUpdateListView,
    SaveUpdateView,
    UnsaveUpdateView,
)

app_name = "reaction"

urlpatterns = [
    path(
        "updates/<uuid:update_id>/like/", LikeCreateView.as_view(), name="like-create"
    ),
    path(
        "updates/<uuid:update_id>/unlike/", LikeDeleteView.as_view(), name="like-delete"
    ),
    path(
        "updates/<uuid:update_id>/comments/",
        CommentListView.as_view(),
        name="comment-list",
    ),
    path(
        "updates/<uuid:update_id>/comments/create/",
        CommentCreateView.as_view(),
        name="comment-create",
    ),
    path("comments/<uuid:id>/", CommentDetailView.as_view(), name="comment-detail"),
    path(
        "comments/<uuid:comment_id>/replies/",
        CommentReplyListView.as_view(),
        name="reply-list",
    ),
    path(
        "comments/<uuid:comment_id>/replies/create/",
        CommentReplyCreateView.as_view(),
        name="reply-create",
    ),
    path("replies/<uuid:id>/", CommentReplyDetailView.as_view(), name="reply-detail"),
    path(
        "updates/<uuid:update_id>/accepted-solution/",
        AcceptedSolutionDetailView.as_view(),
        name="accepted-solution-detail",
    ),
    path(
        "updates/<uuid:update_id>/accept-solution/",
        AcceptedSolutionCreateView.as_view(),
        name="accept-solution",
    ),
    path(
        "updates/<uuid:update_id>/remove-accepted/",
        AcceptedSolutionRemoveView.as_view(),
        name="remove-accepted",
    ),
    path("updates/saved/", SavedUpdateListView.as_view(), name="saved-update-list"),
    path(
        "updates/<uuid:update_id>/save/", SaveUpdateView.as_view(), name="save-update"
    ),
    path(
        "updates/<uuid:update_id>/unsave/",
        UnsaveUpdateView.as_view(),
        name="unsave-update",
    ),
    path("journeys/saved/", SavedJourneyListView.as_view(), name="saved-list"),
    path(
        "journeys/<uuid:journey_id>/save/",
        SavedJourneyCreateView.as_view(),
        name="saved-create",
    ),
    path(
        "journeys/<uuid:journey_id>/unsave/",
        SavedJourneyDeleteView.as_view(),
        name="saved-delete",
    ),
    path("notifications/", NotificationListView.as_view(), name="notification-list"),
    path(
        "notifications/<uuid:id>/",
        NotificationDetailView.as_view(),
        name="notification-detail",
    ),
    path(
        "notifications/mark-all-read/",
        NotificationMarkAllReadView.as_view(),
        name="notification-mark-all-read",
    ),
    path(
        "notifications/unread-count/",
        NotificationUnreadCountView.as_view(),
        name="notification-unread-count",
    ),
]
