from django.conf import settings
from django.core.mail import send_mail


class EmailService:

    @staticmethod
    def send(
        subject,
        message,
        recipient,
    ):
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
        )
