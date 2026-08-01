from django.db.models import IntegerField, Prefetch, Q, Value
from django.db.models.functions import Coalesce
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from accounts.models import User
from journey.models import Journey, JourneyUpdate, JourneyUpdateTag
from reaction.models import Like, SavedUpdate
from shared.pagination import FeedCursorPagination
from shared.permissions import CanViewJourney
from shared.responses import APIResponse

from .serializers import FeedItemSerializer


class BaseFeedView(generics.ListAPIView):
    """
    Base feed view with cursor pagination.
    All feed views inherit from this.
    """

    serializer_class = FeedItemSerializer
    pagination_class = FeedCursorPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        context["user"] = self.request.user
        return context

    def get_queryset(self):
        """
        Override this method in child classes.
        Must return a queryset of JourneyUpdate objects.
        """
        raise NotImplementedError("Subclasses must implement get_queryset")

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())

            paginator = self.pagination_class()

            page = paginator.paginate_queryset(queryset, request, view=self)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return APIResponse(
                    data={
                        "results": serializer.data,
                        "next_cursor": paginator.get_next_cursor(),
                        "has_next": paginator.has_next,
                        "page_size": paginator.page_size,
                    },
                    message="Feed retrieved successfully.",
                    status_code=status.HTTP_200_OK,
                )

            serializer = self.get_serializer(queryset, many=True)
            return APIResponse(
                data={"results": serializer.data},
                message="Feed retrieved successfully.",
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Feed error: {str(e)}", exc_info=True)

            return APIResponse(
                data=None,
                message=f"Error retrieving feed: {str(e)}",
                status_code=status.HTTP_400_BAD_REQUEST,
                is_success=False,
            )


class LatestFeedView(BaseFeedView):
    """
    Get the latest public journey updates.
    GET /api/v1/feed/latest/
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = (
            JourneyUpdate.objects.filter(
                Q(visibility=Journey.Visibility.PUBLIC)
                | Q(
                    visibility__isnull=True,
                    journey__visibility=Journey.Visibility.PUBLIC,
                ),
                is_deleted=False,
                journey__is_deleted=False,
            )
            .annotate(
                safe_like_count=Coalesce("like_count", Value(0), output_field=IntegerField()),
                safe_comment_count=Coalesce("comment_count", Value(0), output_field=IntegerField()),
            )
            .select_related(
                "journey",
                "journey__owner",
                "journey__owner__profile",
            )
            .prefetch_related(
                "images",
                Prefetch(
                    "tags",
                    queryset=JourneyUpdateTag.objects.select_related("tag").order_by("tag__name"),
                    to_attr="tags_prefetched",
                ),
                Prefetch(
                    "likes",
                    queryset=Like.objects.select_related("user"),
                    to_attr="likes_prefetched",
                ),
                Prefetch(
                    "saved_by",
                    queryset=SavedUpdate.objects.select_related("user"),
                    to_attr="saved_prefetched",
                ),
            )
        )

        if self.request.user.is_authenticated:
            qs = qs.exclude(journey__owner=self.request.user)

        return qs.order_by("-created_at", "-id")


class FollowingFeedView(BaseFeedView):
    """
    Get updates from users that the authenticated user follows.
    GET /api/v1/feed/following/
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        followed_user_ids = user.following_relations.values_list("following_id", flat=True)

        if not followed_user_ids:
            return JourneyUpdate.objects.none()

        qs = (
            JourneyUpdate.objects.filter(
                Q(visibility=Journey.Visibility.PUBLIC)
                | Q(
                    visibility__isnull=True,
                    journey__visibility=Journey.Visibility.PUBLIC,
                )
                | Q(
                    visibility=Journey.Visibility.FOLLOWERS,
                    journey__owner__in=followed_user_ids,
                )
                | Q(
                    visibility__isnull=True,
                    journey__visibility=Journey.Visibility.FOLLOWERS,
                    journey__owner__in=followed_user_ids,
                ),
                is_deleted=False,
                journey__is_deleted=False,
                journey__owner__in=followed_user_ids,
            )
            .annotate(
                safe_like_count=Coalesce("like_count", Value(0), output_field=IntegerField()),
                safe_comment_count=Coalesce("comment_count", Value(0), output_field=IntegerField()),
            )
            .select_related(
                "journey",
                "journey__owner",
                "journey__owner__profile",
            )
            .prefetch_related(
                "images",
                Prefetch(
                    "tags",
                    queryset=JourneyUpdateTag.objects.select_related("tag").order_by("tag__name"),
                    to_attr="tags_prefetched",
                ),
                Prefetch(
                    "likes",
                    queryset=Like.objects.select_related("user"),
                    to_attr="likes_prefetched",
                ),
                Prefetch(
                    "saved_by",
                    queryset=SavedUpdate.objects.select_related("user"),
                    to_attr="saved_prefetched",
                ),
            )
        )

        qs = qs.exclude(journey__owner=self.request.user)

        return qs.order_by("-created_at", "-id")


class HelpNeededFeedView(BaseFeedView):
    """
    Get updates where help is needed.
    GET /api/v1/feed/help-needed/
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = (
            JourneyUpdate.objects.filter(
                help_needed=True,
                is_deleted=False,
                journey__is_deleted=False,
            )
            .filter(
                Q(visibility=Journey.Visibility.PUBLIC)
                | Q(
                    visibility__isnull=True,
                    journey__visibility=Journey.Visibility.PUBLIC,
                )
            )
            .annotate(
                safe_like_count=Coalesce("like_count", Value(0), output_field=IntegerField()),
                safe_comment_count=Coalesce("comment_count", Value(0), output_field=IntegerField()),
            )
            .select_related(
                "journey",
                "journey__owner",
                "journey__owner__profile",
            )
            .prefetch_related(
                "images",
                Prefetch(
                    "tags",
                    queryset=JourneyUpdateTag.objects.select_related("tag").order_by("tag__name"),
                    to_attr="tags_prefetched",
                ),
                Prefetch(
                    "likes",
                    queryset=Like.objects.select_related("user"),
                    to_attr="likes_prefetched",
                ),
                Prefetch(
                    "saved_by",
                    queryset=SavedUpdate.objects.select_related("user"),
                    to_attr="saved_prefetched",
                ),
            )
        )

        if self.request.user.is_authenticated:
            qs = qs.exclude(journey__owner=self.request.user)

        return qs.order_by("-created_at", "-id")


class TrendingFeedView(BaseFeedView):
    """
    Get trending updates based on precomputed trending score.
    GET /api/v1/feed/trending/
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = (
            JourneyUpdate.objects.filter(
                Q(visibility=Journey.Visibility.PUBLIC)
                | Q(
                    visibility__isnull=True,
                    journey__visibility=Journey.Visibility.PUBLIC,
                ),
                is_deleted=False,
                journey__is_deleted=False,
            )
            .annotate(
                safe_like_count=Coalesce("like_count", Value(0), output_field=IntegerField()),
                safe_comment_count=Coalesce("comment_count", Value(0), output_field=IntegerField()),
            )
            .select_related(
                "journey",
                "journey__owner",
                "journey__owner__profile",
            )
            .prefetch_related(
                "images",
                Prefetch(
                    "tags",
                    queryset=JourneyUpdateTag.objects.select_related("tag").order_by("tag__name"),
                    to_attr="tags_prefetched",
                ),
                Prefetch(
                    "likes",
                    queryset=Like.objects.select_related("user"),
                    to_attr="likes_prefetched",
                ),
                Prefetch(
                    "saved_by",
                    queryset=SavedUpdate.objects.select_related("user"),
                    to_attr="saved_prefetched",
                ),
            )
        )

        if self.request.user.is_authenticated:
            qs = qs.exclude(journey__owner=self.request.user)

        return qs.order_by("-trending_score", "-created_at", "-id")


class JourneyTimelineView(BaseFeedView):
    """
    Get updates for a specific journey.
    GET /api/v1/feed/journeys/{journey_id}/timeline/
    """

    permission_classes = [IsAuthenticatedOrReadOnly, CanViewJourney]

    def get_queryset(self):
        journey_id = self.kwargs.get("journey_id")
        try:
            journey = Journey.objects.visible_to(self.request.user).get(id=journey_id)
        except Journey.DoesNotExist:
            return JourneyUpdate.objects.none()

        return (
            JourneyUpdate.objects.filter(
                journey=journey,
                is_deleted=False,
            )
            .annotate(
                safe_like_count=Coalesce(
                    "like_count", Value(0), output_field=IntegerField()
                ),
                safe_comment_count=Coalesce(
                    "comment_count", Value(0), output_field=IntegerField()
                ),
            )
            .select_related(
                "journey",
                "journey__owner",
                "journey__owner__profile",
            )
            .prefetch_related(
                "images",
                Prefetch(
                    "tags",
                    queryset=JourneyUpdateTag.objects.select_related("tag").order_by(
                        "tag__name"
                    ),
                    to_attr="tags_prefetched",
                ),
                Prefetch(
                    "likes",
                    queryset=Like.objects.select_related("user"),
                    to_attr="likes_prefetched",
                ),
                Prefetch(
                    "saved_by",
                    queryset=SavedUpdate.objects.select_related("user"),
                    to_attr="saved_prefetched",
                ),
            )
            .order_by("-created_at", "-id")
        )


class UserTimelineView(BaseFeedView):
    """
    Get all updates from a specific user.
    GET /api/v1/feed/users/{username}/timeline/
    """

    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        username = self.kwargs.get("username")
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JourneyUpdate.objects.none()

        return (
            JourneyUpdate.objects.filter(
                journey__owner=user,
                is_deleted=False,
                journey__is_deleted=False,
            )
            .filter(
                Q(visibility=Journey.Visibility.PUBLIC)
                | Q(
                    visibility__isnull=True,
                    journey__visibility=Journey.Visibility.PUBLIC,
                )
                | Q(visibility=Journey.Visibility.FOLLOWERS, journey__owner=user)
                | Q(
                    visibility__isnull=True,
                    journey__visibility=Journey.Visibility.FOLLOWERS,
                    journey__owner=user,
                )
                | Q(journey__owner=self.request.user)
            )
            .annotate(
                safe_like_count=Coalesce(
                    "like_count", Value(0), output_field=IntegerField()
                ),
                safe_comment_count=Coalesce(
                    "comment_count", Value(0), output_field=IntegerField()
                ),
            )
            .select_related(
                "journey",
                "journey__owner",
                "journey__owner__profile",
            )
            .prefetch_related(
                "images",
                Prefetch(
                    "tags",
                    queryset=JourneyUpdateTag.objects.select_related("tag").order_by(
                        "tag__name"
                    ),
                    to_attr="tags_prefetched",
                ),
                Prefetch(
                    "likes",
                    queryset=Like.objects.select_related("user"),
                    to_attr="likes_prefetched",
                ),
                Prefetch(
                    "saved_by",
                    queryset=SavedUpdate.objects.select_related("user"),
                    to_attr="saved_prefetched",
                ),
            )
            .order_by("-created_at", "-id")
        )
