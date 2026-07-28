from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from journey.models import Journey, JourneyUpdate
from shared.pagination import StandardResultsSetPagination
from shared.permissions import (
    CanAcceptSolution,
    CanRemoveAcceptedSolution,
    CanSaveJourney,
    CanSaveUpdate,
    IsCommentAuthor,
    IsNotificationRecipient,
    IsReplyAuthor,
    IsSavedUpdateOwner,
)
from shared.responses import APIResponse
from shared.throttles import (
    CommentThrottle,
    LikeThrottle,
    ReplyThrottle,
    SaveJourneyThrottle,
    SaveUpdateThrottle,
    SolutionAcceptThrottle,
)

from .models import (
    AcceptedSolution,
    Comment,
    CommentReply,
    Like,
    Notification,
    SavedJourney,
    SavedUpdate,
)
from .serializers import (
    AcceptedSolutionCreateSerializer,
    AcceptedSolutionSerializer,
    CommentCreateSerializer,
    CommentReplyCreateSerializer,
    CommentReplySerializer,
    CommentReplyUpdateSerializer,
    CommentSerializer,
    CommentUpdateSerializer,
    LikeCreateSerializer,
    LikeSerializer,
    NotificationSerializer,
    NotificationUpdateSerializer,
    SavedJourneyCreateSerializer,
    SavedJourneySerializer,
    SavedUpdateCreateSerializer,
    SavedUpdateSerializer,
)
from .service import (
    CommentReplyService,
    CommentService,
    LikeService,
    NotificationService,
    SavedJourneyService,
    SavedUpdateService,
    SolutionService,
)


class LikeCreateView(generics.CreateAPIView):
    """
    Create a like on a journey update.
    POST /api/v1/updates/{update_id}/like/
    """

    serializer_class = LikeCreateSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [LikeThrottle]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        update_id = self.kwargs["update_id"]
        journey_update = get_object_or_404(
            JourneyUpdate.objects.select_related("journey"), id=update_id
        )
        if not journey_update.is_visible_to(self.request.user):
            raise PermissionDenied("You do not have permission to like this update.")
        context["journey_update"] = journey_update
        return context

    def perform_create(self, serializer):
        journey_update = self.get_serializer_context()["journey_update"]
        like = LikeService.create_like(self.request.user, journey_update)
        serializer.instance = like

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(
            data=LikeSerializer(serializer.instance).data,
            message="You liked this update.",
            status_code=status.HTTP_201_CREATED,
        )


class LikeDeleteView(generics.DestroyAPIView):
    """
    Remove a like from a journey update.
    DELETE /api/v1/updates/{update_id}/like/
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [LikeThrottle]

    def get_object(self):
        try:
            return Like.objects.get(
                journey_update_id=self.kwargs["update_id"], user=self.request.user
            )
        except Like.DoesNotExist:
            raise NotFound("You have not liked this update.")

    def destroy(self, request, *args, **kwargs):
        like = self.get_object()
        LikeService.remove_like(user=request.user, journey_update=like.journey_update)
        return APIResponse(
            message="Like removed successfully",
            status_code=status.HTTP_204_NO_CONTENT,
        )


class CommentListView(generics.ListAPIView):
    """
    List all non-deleted comments for a journey update.
    GET /api/v1/updates/{update_id}/comments/
    """

    serializer_class = CommentSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        update_id = self.kwargs["update_id"]
        journey_update = get_object_or_404(
            JourneyUpdate.objects.select_related("journey"), id=update_id
        )

        if not journey_update.is_visible_to(self.request.user):
            raise PermissionDenied(
                "You do not have permission to view comments on this update."
            )

        return (
            Comment.objects.filter(journey_update=journey_update, is_deleted=False)
            .select_related("user", "user__profile")
            .prefetch_related("replies__user__profile")
            .order_by("created_at")
        )


class CommentCreateView(generics.CreateAPIView):
    """
    Create a new comment on a journey update.
    POST /api/v1/updates/{update_id}/comments/create/
    """

    serializer_class = CommentCreateSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [CommentThrottle]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        update_id = self.kwargs["update_id"]
        journey_update = get_object_or_404(
            JourneyUpdate.objects.select_related("journey"), id=update_id
        )
        if not journey_update.is_visible_to(self.request.user):
            raise PermissionDenied(
                "You do not have permission to comment on this update."
            )
        context["journey_update"] = journey_update
        return context

    def perform_create(self, serializer):
        journey_update = self.get_serializer_context()["journey_update"]
        comment = CommentService.create_comment(
            user=self.request.user,
            journey_update=journey_update,
            content=serializer.validated_data["content"],
        )
        serializer.instance = comment

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(
            data=CommentSerializer(serializer.instance).data,
            message="Comment added successfully.",
            status_code=status.HTTP_201_CREATED,
        )


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or soft-delete a comment.
    GET/PATCH/DELETE /api/v1/comments/{id}/
    """

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsCommentAuthor]
    lookup_field = "id"

    def get_queryset(self):
        return (
            Comment.objects.filter(is_deleted=False)
            .select_related("user", "user__profile")
            .prefetch_related("replies__user__profile")
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.journey_update.is_visible_to(request.user):
            raise PermissionDenied("You do not have permission to view this comment.")
        serializer = self.get_serializer(instance)
        return APIResponse(
            data=serializer.data,
            message="Comment retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        self.check_object_permissions(request, instance)

        update_serializer = CommentUpdateSerializer(
            instance, data=request.data, partial=partial
        )
        update_serializer.is_valid(raise_exception=True)

        instance.content = update_serializer.validated_data["content"]
        instance.save(update_fields=["content", "updated_at"])

        return APIResponse(
            data=CommentSerializer(instance).data,
            message="Comment updated successfully.",
            status_code=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        self.check_object_permissions(request, comment)
        CommentService.soft_delete_comment(comment, request.user)
        return APIResponse(
            message="Comment deleted successfully.",
            status_code=status.HTTP_204_NO_CONTENT,
        )


class CommentReplyListView(generics.ListAPIView):
    """
    List all non-deleted replies to a specific comment.
    GET /api/v1/comments/{comment_id}/replies/
    """

    serializer_class = CommentReplySerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        comment_id = self.kwargs["comment_id"]
        comment = get_object_or_404(
            Comment.objects.select_related("journey_update__journey"),
            id=comment_id,
            is_deleted=False,
        )

        if not comment.journey_update.is_visible_to(self.request.user):
            raise PermissionDenied("You do not have permission to view this comment.")

        return (
            CommentReply.objects.filter(comment=comment, is_deleted=False)
            .select_related("user", "user__profile")
            .order_by("created_at")
        )


class CommentReplyCreateView(generics.CreateAPIView):
    """
    Create a reply to a comment.
    POST /api/v1/comments/{comment_id}/replies/create/
    """

    serializer_class = CommentReplyCreateSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [ReplyThrottle]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        comment_id = self.kwargs["comment_id"]
        parent_comment = get_object_or_404(
            Comment.objects.select_related("journey_update__journey"),
            id=comment_id,
            is_deleted=False,
        )

        if not parent_comment.journey_update.is_visible_to(self.request.user):
            raise PermissionDenied(
                "You do not have permission to reply to this comment."
            )

        context["comment"] = parent_comment
        return context

    def perform_create(self, serializer):
        parent_comment = self.get_serializer_context()["comment"]
        reply = CommentReplyService.create_reply(
            user=self.request.user,
            parent_comment=parent_comment,
            content=serializer.validated_data["content"],
        )
        serializer.instance = reply

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(
            data=CommentReplySerializer(serializer.instance).data,
            message="Reply added successfully.",
            status_code=status.HTTP_201_CREATED,
        )


class CommentReplyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or soft-delete a reply.
    GET/PATCH/DELETE /api/v1/replies/{id}/
    """

    serializer_class = CommentReplySerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsReplyAuthor]
    lookup_field = "id"

    def get_queryset(self):
        return CommentReply.objects.filter(is_deleted=False).select_related(
            "user", "user__profile", "comment__journey_update__journey"
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if not instance.comment.journey_update.is_visible_to(request.user):
            raise PermissionDenied("You do not have permission to view this reply.")
        serializer = self.get_serializer(instance)
        return APIResponse(
            data=serializer.data,
            message="Reply retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        self.check_object_permissions(request, instance)

        update_serializer = CommentReplyUpdateSerializer(
            instance, data=request.data, partial=partial
        )
        update_serializer.is_valid(raise_exception=True)

        instance.content = update_serializer.validated_data["content"]
        instance.save(update_fields=["content", "updated_at"])

        return APIResponse(
            data=CommentReplySerializer(instance).data,
            message="Reply updated successfully.",
            status_code=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        reply = self.get_object()
        self.check_object_permissions(request, reply)
        CommentReplyService.soft_delete_reply(reply, request.user)
        return APIResponse(
            message="Reply deleted successfully.",
            status_code=status.HTTP_204_NO_CONTENT,
        )


class AcceptedSolutionDetailView(generics.RetrieveAPIView):
    """
    Get the accepted solution for a journey update.
    GET /api/v1/updates/{update_id}/accepted-solution/
    """

    serializer_class = AcceptedSolutionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = "update_id"

    def get_object(self):
        update_id = self.kwargs["update_id"]
        try:
            return AcceptedSolution.objects.get(journey_update_id=update_id)
        except AcceptedSolution.DoesNotExist:
            raise NotFound("No accepted solution found for this update.")

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        if not instance.journey_update.is_visible_to(request.user):
            raise PermissionDenied(
                "You do not have permission to view this accepted solution."
            )

        serializer = self.get_serializer(instance)
        return APIResponse(
            data=serializer.data,
            message="Accepted solution retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )


class AcceptedSolutionCreateView(generics.CreateAPIView):
    """
    Accept a comment as the solution for a journey update.
    POST /api/v1/updates/{update_id}/accept-solution/
    Request body: {"comment_id": "comment_uuid"}
    """

    serializer_class = AcceptedSolutionCreateSerializer
    permission_classes = [IsAuthenticated, CanAcceptSolution]
    throttle_classes = [SolutionAcceptThrottle]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        update_id = self.kwargs["update_id"]
        update = get_object_or_404(
            JourneyUpdate.objects.select_related("journey"), id=update_id
        )
        self.check_object_permissions(self.request, update)
        context["update"] = update
        context["request"] = self.request
        return context

    def perform_create(self, serializer):
        accepted = SolutionService.accept_solution(
            journey_update=self.get_serializer_context()["update"],
            comment=self.get_serializer_context()["comment"],
            accepted_by=self.request.user,
        )
        serializer.instance = accepted

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(
            data=AcceptedSolutionSerializer(serializer.instance).data,
            message="Solution accepted successfully.",
            status_code=status.HTTP_201_CREATED,
        )


class AcceptedSolutionRemoveView(generics.DestroyAPIView):
    """
    Remove the accepted solution for a journey update.
    DELETE /api/v1/updates/{update_id}/remove-accepted/
    """

    permission_classes = [IsAuthenticated, CanRemoveAcceptedSolution]

    def get_object(self):
        update_id = self.kwargs["update_id"]
        update = get_object_or_404(
            JourneyUpdate.objects.select_related("journey"), id=update_id
        )
        self.check_object_permissions(self.request, update)

        try:
            return AcceptedSolution.objects.get(journey_update_id=update_id)
        except AcceptedSolution.DoesNotExist:
            raise NotFound("No accepted solution found for this update.")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        SolutionService.remove_accepted_solution(instance.journey_update)
        return APIResponse(
            message="Accepted solution removed successfully.",
            status_code=status.HTTP_204_NO_CONTENT,
        )


class SavedUpdateListView(generics.ListAPIView):
    """
    List all updates saved by the authenticated user.
    GET /api/v1/updates/saved/
    """

    serializer_class = SavedUpdateSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            SavedUpdate.objects.filter(user=self.request.user)
            .select_related("update", "update__journey", "update__journey__owner")
            .prefetch_related("update__images")
            .order_by("-created_at")
        )


class SaveUpdateView(generics.CreateAPIView):
    """
    Save a journey update.
    POST /api/v1/updates/{update_id}/save/
    """

    serializer_class = SavedUpdateCreateSerializer
    permission_classes = [IsAuthenticated, CanSaveUpdate]
    throttle_classes = [SaveUpdateThrottle]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        update_id = self.kwargs["update_id"]
        update = get_object_or_404(
            JourneyUpdate.objects.select_related("journey"), id=update_id
        )
        self.check_object_permissions(self.request, update)
        context["update"] = update
        context["request"] = self.request
        return context

    def perform_create(self, serializer):
        update = self.get_serializer_context()["update"]
        saved = SavedUpdateService.save_update(user=self.request.user, update=update)
        serializer.instance = saved

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(
            data=SavedUpdateSerializer(serializer.instance).data,
            message="Update saved successfully.",
            status_code=status.HTTP_201_CREATED,
        )


class UnsaveUpdateView(generics.DestroyAPIView):
    """
    Unsave a journey update.
    DELETE /api/v1/updates/{update_id}/unsave/
    """

    permission_classes = [IsAuthenticated, IsSavedUpdateOwner]
    throttle_classes = [SaveUpdateThrottle]

    def get_object(self):
        update_id = self.kwargs["update_id"]
        return get_object_or_404(
            SavedUpdate, user=self.request.user, update_id=update_id
        )

    def destroy(self, request, *args, **kwargs):
        saved = self.get_object()
        saved.delete()
        return APIResponse(
            message="Update unsaved successfully.",
            status_code=status.HTTP_204_NO_CONTENT,
        )


class SavedJourneyListView(generics.ListAPIView):
    """
    List all journeys saved by the authenticated user.
    GET /api/v1/journeys/saved/
    """

    serializer_class = SavedJourneySerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            SavedJourney.objects.filter(user=self.request.user)
            .select_related("journey", "journey__owner", "journey__owner__profile")
            .order_by("-created_at")
        )


class SavedJourneyCreateView(generics.CreateAPIView):
    """
    Save a journey.
    POST /api/v1/journeys/{journey_id}/save/
    """

    serializer_class = SavedJourneyCreateSerializer
    permission_classes = [IsAuthenticated, CanSaveJourney]
    throttle_classes = [SaveJourneyThrottle]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        journey_id = self.kwargs["journey_id"]
        journey = get_object_or_404(
            Journey.objects.visible_to(self.request.user), id=journey_id
        )
        context["journey"] = journey
        return context

    def perform_create(self, serializer):
        saved = SavedJourneyService.save_journey(
            self.request.user, self.get_serializer_context()["journey"]
        )
        serializer.instance = saved

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(
            data=SavedJourneySerializer(serializer.instance).data,
            message="Journey saved successfully.",
            status_code=status.HTTP_201_CREATED,
        )


class SavedJourneyDeleteView(generics.DestroyAPIView):
    """
    Remove a saved journey (unsave).
    DELETE /api/v1/journeys/{journey_id}/unsave/
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [SaveJourneyThrottle]

    def delete(self, request, *args, **kwargs):
        journey_id = self.kwargs["journey_id"]
        deleted, _ = SavedJourney.objects.filter(
            user=request.user, journey_id=journey_id
        ).delete()

        if deleted == 0:
            raise NotFound("You haven't saved this journey.")

        return APIResponse(
            message="Journey unsaved successfully.",
            status_code=status.HTTP_204_NO_CONTENT,
        )


class NotificationListView(generics.ListAPIView):
    """
    List all notifications for the authenticated user.
    GET /api/v1/notifications/
    """

    serializer_class = NotificationSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            Notification.objects.filter(recipient=self.request.user)
            .select_related("actor", "actor__profile")
            .order_by("-created_at")
        )


class NotificationDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update a notification.
    GET/PATCH /api/v1/notifications/{id}/
    """

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, IsNotificationRecipient]
    lookup_field = "id"

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse(
            data=serializer.data,
            message="Notification retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        self.check_object_permissions(request, instance)

        update_serializer = NotificationUpdateSerializer(
            instance, data=request.data, partial=partial
        )
        update_serializer.is_valid(raise_exception=True)
        update_serializer.save()

        return APIResponse(
            data=NotificationSerializer(instance).data,
            message="Notification updated successfully.",
            status_code=status.HTTP_200_OK,
        )


class NotificationMarkAllReadView(generics.UpdateAPIView):
    """
    Mark all notifications for the authenticated user as read.
    POST /api/v1/notifications/mark-all-read/
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        count = NotificationService.mark_all_as_read(request.user)
        return APIResponse(
            data={"updated_count": count},
            message=f"{count} notifications marked as read.",
            status_code=status.HTTP_200_OK,
        )


class NotificationUnreadCountView(generics.RetrieveAPIView):
    """
    Get the count of unread notifications for the authenticated user.
    GET /api/v1/notifications/unread-count/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        count = NotificationService.get_unread_count(request.user)
        return APIResponse(
            data={"unread_count": count},
            message="Unread count retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )
