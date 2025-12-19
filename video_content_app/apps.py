from django.apps import AppConfig


class VideoContentAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'video_content_app'

    def ready(self):
        # Import signal handlers to ensure they are registered
        import video_content_app.api.signals
