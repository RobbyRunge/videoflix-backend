import os
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from video_content_app.models import Video
from video_content_app.tasks import convert_480p, convert_720p, convert_1080p


@receiver(post_save, sender=Video)
def video_created_handler(sender, instance, created, **kwargs):
    """
    Signal handler for post_save signal of Video model.
    Perform actions when a new video is created.
    """
    if created and instance.video_file:
        convert_480p(instance.video_file.path)
        convert_720p(instance.video_file.path)
        convert_1080p(instance.video_file.path)


@receiver(post_delete, sender=Video)
def video_deleted_handler(sender, instance, **kwargs):
    """
    Signal handler for post_delete signal of Video model.
    Perform actions when a video is deleted.
    """
    if instance.video_file:  # For later, update this one for different videos (480p, 720p, etc.)
        if os.path.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)
