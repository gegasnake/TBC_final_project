from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.tasks import send_event_creation_email  # Import the Celery task
from event.models import Event


@receiver(post_save, sender=Event)
def notify_followers_on_new_event(sender, instance, created, **kwargs):
    """
    Sends an email notification to all followers when a user creates a new event.
    This task is offloaded to Celery to avoid blocking the main thread.
    """
    if created:  # Trigger only on event creation, not updates
        organizer = instance.organizer
        followers = organizer.followers.all()  # Get all followers

        # Prepare email content
        subject = f"New Event Created by {organizer.username}"
        message = (
            f"Hello,\n\n{organizer.username} has created a new event: '{instance.title}'.\n"
            f"Event Details:\n"
            f" - Description: {instance.description}\n"
            f" - Start Date: {instance.start_date}\n"
            f" - Location: {instance.location}\n"
            f" - Link: {instance.link if instance.link else 'No link provided'}\n\n"
            f"Don't miss it!"
        )

        # Use Celery to send emails to each follower in the background
        for follower in followers:
            print(follower)
            send_event_creation_email.delay(follower.email, subject, message)  # This triggers the task
