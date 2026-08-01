from django.db import transaction

from accounts.models import User

from .models import Feedback


class FeedbackService:
    """Service layer for Feedback operations."""

    @staticmethod
    @transaction.atomic
    def create_feedback(
        user: User,
        feedback_type: str,
        subject: str,
        message: str,
        rating: int = None,
        is_anonymous: bool = False,
    ) -> Feedback:
        """
        Create a new feedback entry.
        """
        feedback = Feedback.objects.create(
            user=user,
            feedback_type=feedback_type,
            subject=subject.strip(),
            message=message.strip(),
            rating=rating,
            is_anonymous=is_anonymous,
        )
        return feedback

    @staticmethod
    def get_user_feedbacks(user: User):
        """Get all feedbacks submitted by a user."""
        return Feedback.objects.filter(user=user).order_by("-created_at")

    @staticmethod
    def get_feedback_by_status(status: str):
        """Get feedbacks by status."""
        return Feedback.objects.filter(status=status).order_by("-created_at")

    @staticmethod
    @transaction.atomic
    def resolve_feedback(feedback_id: str, resolved_by: User, resolution_note: str = ""):
        """Resolve a feedback."""
        feedback = Feedback.objects.get(id=feedback_id)
        feedback.resolve(resolved_by, resolution_note)
        return feedback
