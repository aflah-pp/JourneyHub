import logging

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from audit.models import ActivityLog
from audit.service import ActivityLogService
from shared.pagination import StandardResultsSetPagination
from shared.permissions import (
    CanManageImages,
    CanManageTags,
    CanViewJourney,
    CanViewJourneyUpdate,
    IsAuthenticatedAndVerified,
    IsJourneyOwner,
)
from shared.responses import APIResponse
from shared.throttles import (
    JourneyCreateThrottle,
    JourneysAnonRateThrottle,
    UpdateCreateThrottle,
)

from .filters import JourneyFilter, JourneyUpdateFilter
from .models import (
    Journey,
    JourneyImage,
    JourneyUpdate,
    Tag,
)
from .serializers import (
    JourneyCreateSerializer,
    JourneyDetailSerializer,
    JourneyImageCreateSerializer,
    JourneyListSerializer,
    JourneyUpdateCreateSerializer,
    JourneyUpdateDetailSerializer,
    JourneyUpdateListSerializer,
    JourneyUpdateSerializer,
    JourneyUpdateUpdateSerializer,
    TagSerializer,
    TrendingTagsSerializer,
    UpdateTagsSerializer,
)
from .service import (
    ImageService,
    JourneyService,
    JourneyUpdateService,
    TagService,
)

User = get_user_model()
logger = logging.getLogger(__name__)


@extend_schema(tags=["Journey"], summary="Public list of journeys")
class JourneyListPublicView(generics.ListAPIView):
    """
    Public list of journeys (visible based on visibility rules).
    GET /api/v1/journeys/
    """

    serializer_class = JourneyListSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = JourneyFilter
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "title", "latest_progress"]
    ordering = ["-created_at"]
    throttle_classes = [JourneysAnonRateThrottle]

    def get_queryset(self):
        qs = (
            Journey.objects.visible_to(self.request.user)
            .select_related("owner", "owner__profile")
            .prefetch_related("owner__profile")
        )

        if self.request.user.is_authenticated:
            qs = qs.exclude(owner=self.request.user)
        return qs


@extend_schema(tags=["Journey"], summary="List journeys owned by authenticated user")
class JourneyListMyView(generics.ListAPIView):
    """
    List journeys owned by the authenticated user.
    GET /api/v1/journeys/my/
    """

    serializer_class = JourneyListSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = JourneyFilter
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "title", "latest_progress"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return (
            Journey.objects.owned_by(self.request.user)
            .not_deleted()
            .select_related("owner", "owner__profile")
            .prefetch_related("owner__profile")
        )


@extend_schema(
    tags=["Journey"],
    summary="List public journeys for a user",
)
class UserJourneyListView(generics.ListAPIView):
    """
    List all public journeys belonging to a user.

    GET /api/v1/accounts/users/<username>/journeys/
    """

    serializer_class = JourneyListSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]

    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    ]
    filterset_class = JourneyFilter
    search_fields = [
        "title",
        "description",
    ]
    ordering_fields = [
        "created_at",
        "updated_at",
        "title",
        "latest_progress",
    ]
    ordering = ["-created_at"]

    def get_queryset(self):
        username = self.kwargs["username"]

        owner = get_object_or_404(
            User.objects.select_related("profile"),
            username__iexact=username,
        )

        return (
            Journey.objects.filter(
                owner=owner,
                visibility=Journey.Visibility.PUBLIC,
            )
            .not_deleted()
            .select_related(
                "owner",
                "owner__profile",
            )
        )


@extend_schema(tags=["Journey"], summary="Get detailed view of a single journey")
class JourneyDetailView(generics.RetrieveAPIView):
    """
    Get detailed view of a single journey.
    GET /api/v1/journeys/{id}/
    """

    serializer_class = JourneyDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, CanViewJourney]
    lookup_field = "id"

    def get_queryset(self):
        return (
            Journey.objects.visible_to(self.request.user)
            .select_related("owner", "owner__profile")
            .prefetch_related("owner__profile")
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        ActivityLogService.log_activity(
            user=request.user if request.user.is_authenticated else None,
            action_type=ActivityLog.ActionType.VIEW,
            target=instance,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            request_path=request.path,
            request_method=request.method,
            metadata={
                "journey_id": str(instance.id),
                "journey_title": instance.title,
            },
        )

        return APIResponse(
            data=serializer.data,
            message="Journey retrieved successfully",
            status_code=status.HTTP_200_OK,
        )


@extend_schema(tags=["Journey"], summary="Create a new journey")
class JourneyCreateView(generics.CreateAPIView):
    """
    Create a new journey.
    POST /api/v1/journeys/create/
    """

    serializer_class = JourneyCreateSerializer
    permission_classes = [IsAuthenticated, IsAuthenticatedAndVerified]
    throttle_classes = [JourneyCreateThrottle]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def perform_create(self, serializer):
        journey = JourneyService.create_journey(
            user=self.request.user, validated_data=serializer.validated_data
        )
        serializer.instance = journey

        ActivityLogService.log_activity(
            user=self.request.user,
            action_type=ActivityLog.ActionType.CREATE,
            target=journey,
            ip_address=self.request.META.get("REMOTE_ADDR"),
            user_agent=self.request.META.get("HTTP_USER_AGENT", ""),
            request_path=self.request.path,
            request_method=self.request.method,
            metadata={
                "journey_id": str(journey.id),
                "journey_title": journey.title,
            },
        )

    def create(self, request, *args, **kwargs):

        if request.content_type and "multipart/form-data" in request.content_type:
            data = (
                request.data.dict() if hasattr(request.data, "dict") else request.data
            )
            if "cover_image" in request.FILES:
                data["cover_image"] = request.FILES["cover_image"]
        else:
            data = request.data

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(
            data=serializer.data,
            message="Journey created successfully",
            status_code=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["Journey"], summary="Update an existing journey")
class JourneyUpdateView(generics.UpdateAPIView):
    """
    Update an existing journey.
    PATCH /api/v1/journeys/{id}/update/
    """

    serializer_class = JourneyUpdateSerializer
    permission_classes = [IsAuthenticated, IsJourneyOwner]
    lookup_field = "id"

    def get_queryset(self):
        return Journey.objects.owned_by(self.request.user).not_deleted()

    def perform_update(self, serializer):
        journey = JourneyService.update_journey(
            journey=serializer.instance, validated_data=serializer.validated_data
        )
        serializer.instance = journey

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        if request.content_type and "multipart/form-data" in request.content_type:
            data = (
                request.data.dict() if hasattr(request.data, "dict") else request.data
            )
            if "cover_image" in request.FILES:
                data["cover_image"] = request.FILES["cover_image"]
        else:
            data = request.data

        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        ActivityLogService.log_activity(
            user=request.user,
            action_type=ActivityLog.ActionType.UPDATE,
            target=instance,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            request_path=request.path,
            request_method=request.method,
            metadata={
                "journey_id": str(instance.id),
                "journey_title": instance.title,
            },
        )

        return APIResponse(
            data=serializer.data,
            message="Journey updated successfully",
            status_code=status.HTTP_200_OK,
        )


@extend_schema(tags=["Journey"], summary="Soft delete a journey")
class JourneyDeleteView(generics.DestroyAPIView):
    """
    Soft delete a journey.
    DELETE /api/v1/journeys/{id}/delete/
    """

    permission_classes = [IsAuthenticated, IsJourneyOwner]
    lookup_field = "id"

    def get_queryset(self):
        return Journey.objects.owned_by(self.request.user).not_deleted()

    def destroy(self, request, *args, **kwargs):
        journey = self.get_object()

        ActivityLogService.log_activity(
            user=request.user,
            action_type=ActivityLog.ActionType.DELETE,
            target=journey,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            request_path=request.path,
            request_method=request.method,
            metadata={
                "journey_id": str(journey.id),
                "journey_title": journey.title,
            },
        )

        JourneyService.soft_delete_journey(journey, request.user)
        return APIResponse(
            message="Journey deleted successfully",
            status_code=status.HTTP_204_NO_CONTENT,
        )


@extend_schema(
    tags=["Journey Updates"], summary="List all updates for a specific journey"
)
class JourneyUpdateListView(generics.ListAPIView):
    """
    List all updates for a specific journey.
    GET /api/v1/journeys/{journey_id}/updates/
    """

    serializer_class = JourneyUpdateListSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = JourneyUpdateFilter
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "progress_percentage"]
    ordering = ["-created_at"]

    def get_queryset(self):
        journey_id = self.kwargs["journey_id"]
        journey = get_object_or_404(
            Journey.objects.visible_to(self.request.user), id=journey_id
        )
        return (
            JourneyUpdate.objects.for_journey(journey)
            .not_deleted()
            .select_related("journey", "journey__owner")
            .prefetch_related("images")
        )


@extend_schema(
    tags=["Journey Updates"], summary="Get detailed view of a journey update"
)
class JourneyUpdateDetailView(generics.RetrieveAPIView):
    """
    Get detailed view of a journey update.
    GET /api/v1/journeys/{journey_id}/updates/{id}/
    """

    serializer_class = JourneyUpdateDetailSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, CanViewJourneyUpdate]
    lookup_field = "id"

    def get_queryset(self):
        journey_id = self.kwargs["journey_id"]
        return (
            JourneyUpdate.objects.filter(journey_id=journey_id)
            .not_deleted()
            .select_related("journey", "journey__owner")
            .prefetch_related("images", "tags__tag", "comments__user__profile")
        )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        serializer = self.get_serializer(instance)
        return APIResponse(
            data=serializer.data,
            message="Journey update retrieved successfully",
            status_code=status.HTTP_200_OK,
        )


@extend_schema(tags=["Journey Updates"], summary="Create a new journey update")
class JourneyUpdateCreateView(generics.CreateAPIView):
    """
    Create a new journey update.
    POST /api/v1/journeys/{journey_id}/updates/create/
    """

    serializer_class = JourneyUpdateCreateSerializer
    permission_classes = [IsAuthenticated, IsJourneyOwner]
    throttle_classes = [UpdateCreateThrottle]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["journey"] = self.get_journey()
        return context

    def get_journey(self):
        return get_object_or_404(
            Journey.objects.owned_by(self.request.user).not_deleted(),
            id=self.kwargs["journey_id"],
        )

    def perform_create(self, serializer):
        journey = self.get_journey()
        update = JourneyUpdateService.create_update(
            journey=journey, validated_data=serializer.validated_data
        )
        serializer.instance = update

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(
            data=serializer.data,
            message="Journey update created successfully",
            status_code=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["Journey Updates"], summary="Update an existing journey update")
class JourneyUpdateUpdateView(generics.UpdateAPIView):
    """
    Update an existing journey update.
    PATCH /api/v1/journeys/{journey_id}/updates/{id}/update/
    """

    serializer_class = JourneyUpdateUpdateSerializer
    permission_classes = [IsAuthenticated, IsJourneyOwner]
    lookup_field = "id"

    def get_queryset(self):
        return (
            JourneyUpdate.objects.filter(journey_id=self.kwargs["journey_id"])
            .not_deleted()
            .select_related("journey")
        )

    def perform_update(self, serializer):
        update = JourneyUpdateService.update_update(
            update=serializer.instance, validated_data=serializer.validated_data
        )
        serializer.instance = update

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return APIResponse(
            data=serializer.data,
            message="Journey update updated successfully",
            status_code=status.HTTP_200_OK,
        )


@extend_schema(tags=["Journey Updates"], summary="Soft delete a journey update")
class JourneyUpdateDeleteView(generics.DestroyAPIView):
    """
    Soft delete a journey update.
    DELETE /api/v1/journeys/{journey_id}/updates/{id}/delete/
    """

    permission_classes = [IsAuthenticated, IsJourneyOwner]
    lookup_field = "id"

    def get_queryset(self):
        return JourneyUpdate.objects.filter(
            journey_id=self.kwargs["journey_id"]
        ).not_deleted()

    def destroy(self, request, *args, **kwargs):
        update = self.get_object()
        JourneyUpdateService.delete_update(update, request.user)
        return APIResponse(
            message="Journey update deleted successfully",
            status_code=status.HTTP_204_NO_CONTENT,
        )


@extend_schema(
    tags=["Journey Updates"], summary="Update tags for a specific journey update"
)
class JourneyUpdateTagsView(generics.UpdateAPIView):
    """
    Update tags for a specific journey update.
    PATCH /api/v1/journeys/{journey_id}/updates/{update_id}/tags/
    Request body: {"tags": ["tag1", "tag2"]}
    """

    permission_classes = [IsAuthenticated, CanManageTags]
    lookup_field = "id"
    lookup_url_kwarg = "update_id"

    def get_queryset(self):
        return (
            JourneyUpdate.objects.filter(journey_id=self.kwargs["journey_id"])
            .not_deleted()
            .select_related("journey")
        )

    def patch(self, request, *args, **kwargs):
        update = self.get_object()
        self.check_object_permissions(request, update)

        serializer = UpdateTagsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tags = TagService.assign_tags(update, serializer.validated_data["tags"])
        tag_serializer = TagSerializer(tags, many=True)

        return APIResponse(
            data=tag_serializer.data,
            message="Tags updated successfully",
            status_code=status.HTTP_200_OK,
        )


@extend_schema(tags=["Journey Images"], summary="Add an image to a journey update")
class JourneyImageCreateView(generics.CreateAPIView):
    """
    Add an image to a journey update.
    POST /api/v1/updates/{update_id}/images/create/
    """

    serializer_class = JourneyImageCreateSerializer
    permission_classes = [IsAuthenticated, CanManageImages]
    throttle_classes = [UpdateCreateThrottle]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        journey_update = get_object_or_404(
            JourneyUpdate.objects.select_related("journey"), id=self.kwargs["update_id"]
        )
        self.check_object_permissions(self.request, journey_update)
        context["journey_update"] = journey_update
        return context

    def perform_create(self, serializer):
        journey_update = self.get_serializer_context()["journey_update"]
        image = ImageService.add_image(journey_update, serializer.validated_data)
        serializer.instance = image

    def create(self, request, *args, **kwargs):

        if request.content_type and "multipart/form-data" in request.content_type:
            data = (
                request.data.dict() if hasattr(request.data, "dict") else request.data
            )
            if "image" in request.FILES:
                data["image"] = request.FILES["image"]
        else:
            data = request.data

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return APIResponse(
            data=serializer.data,
            message="Image added successfully",
            status_code=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["Journey Images"], summary="Delete an image from a journey update")
class JourneyImageDeleteView(generics.DestroyAPIView):
    """
    Delete an image from a journey update.
    DELETE /api/v1/updates/{update_id}/images/{id}/delete/
    """

    permission_classes = [IsAuthenticated, CanManageImages]
    lookup_field = "id"

    def get_queryset(self):
        return JourneyImage.objects.filter(
            journey_update_id=self.kwargs["update_id"]
        ).select_related("journey_update__journey")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(request, instance.journey_update)
        ImageService.delete_image(instance)
        return APIResponse(
            message="Image deleted successfully",
            status_code=status.HTTP_204_NO_CONTENT,
        )


@extend_schema(tags=["Journey Images"], summary="Reorder images for a journey update")
class JourneyImageReorderView(generics.UpdateAPIView):
    """
    Reorder images for a journey update.
    PATCH /api/v1/updates/{update_id}/images/reorder/
    Request body: {"ordered_ids": ["id1", "id2", "id3"]}
    """

    permission_classes = [IsAuthenticated, CanManageImages]

    def get_queryset(self):
        return JourneyImage.objects.none()

    def patch(self, request, *args, **kwargs):
        update_id = self.kwargs["update_id"]
        ordered_ids = request.data.get("ordered_ids", [])

        if not ordered_ids:
            return APIResponse(
                message="ordered_ids is required",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        journey_update = get_object_or_404(
            JourneyUpdate.objects.select_related("journey"), id=update_id
        )
        self.check_object_permissions(request, journey_update)

        ImageService.reorder_images(journey_update, ordered_ids)

        return APIResponse(
            message="Images reordered successfully",
            status_code=status.HTTP_200_OK,
        )


@extend_schema(tags=["Journey"], summary="Search for journeys with full-text search")
class JourneySearchView(generics.ListAPIView):
    """
    Search for journeys with full-text search.
    GET /api/v1/journeys/search/?q=query
    """

    serializer_class = JourneyListSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title"]
    ordering_fields = ["created_at", "updated_at", "latest_progress"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return (
            Journey.objects.visible_to(self.request.user)
            .select_related("owner", "owner__profile")
            .prefetch_related("owner__profile")
        )


@extend_schema(tags=["Tags"], summary="Get trending tags (most used)")
class TrendingTagsView(generics.ListAPIView):
    """
    Get trending tags (most used).
    GET /api/v1/journeys/tags/trending/
    """

    serializer_class = TrendingTagsSerializer
    pagination_class = None

    def get_queryset(self):
        return Tag.objects.order_by("-usage_count")[:10]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return APIResponse(
            data=serializer.data,
            message="Trending tags retrieved",
            status_code=status.HTTP_200_OK,
        )


@extend_schema(tags=["Tags"], summary="Get details of a specific tag")
class TagDetailView(generics.RetrieveAPIView):
    """
    Get details of a specific tag.
    GET /api/v1/journeys/tags/{slug}/
    """

    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = "slug"

    def get_queryset(self):
        return Tag.objects.all()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse(
            data=serializer.data,
            message="Tag retrieved successfully",
            status_code=status.HTTP_200_OK,
        )
