from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_event_creation_email(user_email, subject, message):
    """
    Celery task to send the email to a user about a new event.
    """
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            # fail_silently=True
        )
    except Exception as e:
        print(f"Error sending email: {e}")
