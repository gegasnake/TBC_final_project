from django.apps import AppConfig


class EventConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'event'

    def ready(self):
        import notifications.signals  # Ensure the signals are loaded
