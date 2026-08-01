from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated

from shared.pagination import StandardResultsSetPagination
from shared.responses import APIResponse
from shared.services.telegram_service import TelegramService
from shared.throttles import FeedbackThrottle

from .models import Feedback
from .serializers import (
    FeedbackCreateSerializer,
    FeedbackSerializer,
    FeedbackUpdateSerializer,
)


class FeedbackCreateView(generics.CreateAPIView):
    """
    Submit feedback.
    POST /api/v1/feedback/
    """

    serializer_class = FeedbackCreateSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [FeedbackThrottle]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def perform_create(self, serializer):
        feedback = serializer.save()
        # Send Telegram notification
        TelegramService.send_feedback_notification(feedback)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(
            data=FeedbackSerializer(serializer.instance).data,
            message="Thank you for your feedback! We appreciate your input.",
            status_code=status.HTTP_201_CREATED,
        )


class FeedbackListView(generics.ListAPIView):
    """
    List feedbacks.
    GET /api/v1/feedback/
    - Users see only their own feedbacks.
    - Moderators see all feedbacks.
    """

    serializer_class = FeedbackSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "feedback_type"]
    search_fields = ["subject", "message"]
    ordering_fields = ["created_at", "status"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Feedback.objects.select_related("user", "user__profile").all()
        return Feedback.objects.filter(user=user).select_related(
            "user", "user__profile"
        )


class FeedbackDetailView(generics.RetrieveUpdateAPIView):
    """
    Get or update a feedback.
    GET/PATCH /api/v1/feedback/{id}/
    - Users can view their own feedbacks.
    - Moderators can update status/admin_notes.
    """

    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Feedback.objects.select_related("user", "user__profile")
        return Feedback.objects.filter(user=user)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        # Only staff can update
        if not request.user.is_staff:
            return APIResponse(
                message="Only moderators can update feedbacks.",
                status_code=status.HTTP_403_FORBIDDEN,
                is_success=False,
            )

        update_serializer = FeedbackUpdateSerializer(
            instance,
            data=request.data,
            partial=partial,
        )
        update_serializer.is_valid(raise_exception=True)
        update_serializer.save()

        return APIResponse(
            data=FeedbackSerializer(instance).data,
            message="Feedback updated successfully.",
            status_code=status.HTTP_200_OK,
        )
