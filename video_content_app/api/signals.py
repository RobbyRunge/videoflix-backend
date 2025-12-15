from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
import os

from video_content_app.models import Video


@receiver(post_save, sender=Video)
def video_created_handler(sender, instance, created, **kwargs):
    """
    Signal handler for post_save signal of Video model.
    Perform actions when a new video is created.
    """
    if created:
        pass  # Placeholder for actions to perform on video creation


@receiver(post_delete, sender=Video)
def video_deleted_handler(sender, instance, **kwargs):
    """
    Signal handler for post_delete signal of Video model.
    Perform actions when a video is deleted.
    """
    if instance.video_file:  # For later, update this one for different videos (480p, 720p, etc.)
        if os.path.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)
