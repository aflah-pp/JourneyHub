import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class TelegramService:
    """Service for sending feedback notifications to Telegram."""

    BOT_TOKEN = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    CHAT_ID = getattr(settings, "TELEGRAM_CHAT_ID", "")

    @classmethod
    def is_configured(cls) -> bool:
        """Check if Telegram is configured."""
        return bool(cls.BOT_TOKEN and cls.CHAT_ID)

    @classmethod
    def send_message(cls, message: str, parse_mode: str = "HTML") -> bool:
        """
        Send a message to the configured Telegram chat.
        Returns True if successful, False otherwise.
        """
        if not cls.is_configured():
            logger.warning("Telegram not configured. Message not sent.")
            return False

        try:
            url = f"https://api.telegram.org/bot{cls.BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": cls.CHAT_ID,
                "text": message,
                "parse_mode": parse_mode,
            }
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                logger.info("Telegram message sent successfully.")
                return True
            else:
                logger.error(
                    f"Telegram API error: {response.status_code} - {response.text}"
                )
                return False
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {str(e)}")
            return False

    @classmethod
    def format_feedback_message(cls, feedback) -> str:
        """Format feedback as a Telegram message."""
        from feedback.models import FeedbackStatus, FeedbackType

        type_label = dict(FeedbackType.choices).get(
            feedback.feedback_type, feedback.feedback_type
        )
        status_label = dict(FeedbackStatus.choices).get(
            feedback.status, feedback.status
        )

        message = (
            f"<b>📝 New Feedback</b>\n"
            f"<b>ID:</b> <code>{feedback.id}</code>\n"
            f"<b>Type:</b> {type_label}\n"
            f"<b>Status:</b> {status_label}\n"
            f"<b>User:</b> {feedback.display_username}\n"
            f"<b>Subject:</b> {feedback.subject}\n"
            f"<b>Message:</b>\n{feedback.message}\n"
        )

        if feedback.rating:
            message += f"<b>Rating:</b> {'⭐' * feedback.rating}\n"

        message += (
            f"\n<i>Submitted: {feedback.created_at.strftime('%Y-%m-%d %H:%M UTC')}</i>"
        )

        return message

    @classmethod
    def send_feedback_notification(cls, feedback) -> bool:
        """Send a formatted feedback notification to Telegram."""
        if not cls.is_configured():
            return False

        message = cls.format_feedback_message(feedback)
        return cls.send_message(message)
