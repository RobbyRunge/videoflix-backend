import os
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
import django_rq

from video_content_app.models import Video
from video_content_app.tasks import convert_480p, convert_720p, convert_1080p


@receiver(post_save, sender=Video)
def video_created_handler(sender, instance, created, **kwargs):
    """
    Signal handler for post_save signal of Video model.
    Perform actions when a new video is created.
    """
    if created and instance.video_file:
        queue = django_rq.get_queue('default', autocommit=True)
        queue.enqueue(convert_480p, instance.video_file.path)
        queue.enqueue(convert_720p, instance.video_file.path)
        queue.enqueue(convert_1080p, instance.video_file.path)


@receiver(post_delete, sender=Video)
def video_deleted_handler(sender, instance, **kwargs):
    """
    Signal handler for post_delete signal of Video model.
    Deletes original video, converted versions, and thumbnail.
    """
    # Delete original video file
    if instance.video_file:
        if os.path.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)

        # Delete converted video files (480p, 720p, 1080p)
        base_path = instance.video_file.path
        for resolution in ['480p', '720p', '1080p']:
            converted_path = f"{base_path}_{resolution}.mp4"
            if os.path.isfile(converted_path):
                os.remove(converted_path)

    # Delete thumbnail
    if instance.thumbnail:
        if os.path.isfile(instance.thumbnail.path):
            os.remove(instance.thumbnail.path)
