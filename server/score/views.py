from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)

from accounts.models import User
from shared.pagination import StandardResultsSetPagination
from shared.permissions import IsOwnerOrReadOnly
from shared.responses import APIResponse

from .models import BuilderScore, BuilderScoreHistory
from .serializers import (
    BuilderScoreHistorySerializer,
    BuilderScoreSerializer,
    LeaderboardEntrySerializer,
    PublicBuilderScoreSerializer,
)
from .service import ScoreService


class MyScoreView(generics.RetrieveAPIView):
    """
    Get the authenticated user's own full score.
    GET /api/v1/score/me/
    """

    permission_classes = [IsAuthenticated]
    serializer_class = BuilderScoreSerializer

    def get_object(self):
        return ScoreService.get_score(self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse(
            data=serializer.data,
            message="Score retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )


class PublicScoreView(generics.RetrieveAPIView):
    """
    Get any user's public score by username.
    GET /api/v1/score/users/{username}/
    - Owner or staff gets full details.
    - Others get limited public fields (per SRS).
    """

    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    lookup_field = "username"

    def get_object(self):
        username = self.kwargs["username"]
        user = get_object_or_404(User, username=username)
        score, _ = BuilderScore.objects.get_or_create(user=user)
        self.check_object_permissions(self.request, score)
        return score

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        if request.user == instance.user or request.user.is_staff:
            serializer = BuilderScoreSerializer(instance)
        else:

            serializer = PublicBuilderScoreSerializer(instance)

        return APIResponse(
            data=serializer.data,
            message="Score retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )


class LeaderboardView(generics.ListAPIView):
    """
    Get top users by total_score with rank.
    GET /api/v1/score/leaderboard/
    Public endpoint – anyone can view.
    """

    serializer_class = LeaderboardEntrySerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [AllowAny]

    def get_queryset(self):
        return ScoreService.get_leaderboard(limit=50)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            page_number = self.paginator.page.number
            page_size = self.paginator.get_page_size(request)

            start_rank = ((page_number - 1) * page_size) + 1

            for idx, item in enumerate(page):
                item.rank = start_rank + idx

            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        for idx, item in enumerate(queryset, start=1):
            item.rank = idx

        serializer = self.get_serializer(queryset, many=True)

        return APIResponse(
            data=serializer.data,
            message="Leaderboard retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )


class ScoreHistoryView(generics.ListAPIView):
    """
    List score history for the authenticated user.
    GET /api/v1/score/history/
    Only owner can view their own history.
    """

    serializer_class = BuilderScoreHistorySerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (
            BuilderScoreHistory.objects.filter(user=self.request.user)
            .select_related("user")
            .order_by("-created_at")
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return APIResponse(
            data=serializer.data,
            message="Score history retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )


class ScoreHistoryDetailView(generics.RetrieveAPIView):
    """
    Get a specific score history entry.
    GET /api/v1/score/history/{id}/
    Only owner can view their own history.
    """

    serializer_class = BuilderScoreHistorySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "id"

    def get_queryset(self):
        return BuilderScoreHistory.objects.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return APIResponse(
            data=serializer.data,
            message="Score history entry retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )


class MyRankView(generics.RetrieveAPIView):
    """
    Get the authenticated user's current rank.
    GET /api/v1/score/rank/
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        rank = ScoreService.get_rank(request.user)
        score = ScoreService.get_score(request.user)
        total_users = BuilderScore.objects.count()

        return APIResponse(
            data={
                "rank": rank,
                "total_users": total_users,
                "total_score": score.total_score,
                "level": score.level,
            },
            message="Rank retrieved successfully.",
            status_code=status.HTTP_200_OK,
        )
