from video_content_app.models import Video
from django.dispatch import receiver
from django.db.models.signals import post_save


@receiver(post_save, sender=Video)
def video_created_handler(sender, instance, created, **kwargs):
    """
    Signal handler for post_save signal of Video model.
    Perform actions when a new video is created.
    """
    if created:
        pass  # Placeholder for actions to perform on video creation
