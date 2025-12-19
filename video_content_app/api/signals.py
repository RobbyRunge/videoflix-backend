import os
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete
import django_rq

from video_content_app.models import Video
from video_content_app.tasks import (
    convert_to_hls,
    delete_original_video
)


@receiver(post_save, sender=Video)
def video_created_handler(sender, instance, created, **kwargs):
    """
    Signal handler for post_save signal of Video model.
    Converts video to HLS format with multiple resolutions and deletes the original.
    """
    if created and instance.video_file:
        queue = django_rq.get_queue('default', autocommit=True)
        job = queue.enqueue(
            convert_to_hls, instance.video_file.path, instance.id)
        queue.enqueue(
            delete_original_video,
            instance.video_file.path,
            depends_on=job
        )


@receiver(post_delete, sender=Video)
def video_deleted_handler(sender, instance, **kwargs):
    """
    Signal handler for post_delete signal of Video model.
    Deletes HLS files and thumbnail.
    """
    import shutil
    from django.conf import settings

    if instance.video_file:
        if os.path.isfile(instance.video_file.path):
            os.remove(instance.video_file.path)

    hls_dir = os.path.join(settings.MEDIA_ROOT, 'videos', str(instance.id))
    if os.path.isdir(hls_dir):
        shutil.rmtree(hls_dir)

    if instance.thumbnail:
        if os.path.isfile(instance.thumbnail.path):
            os.remove(instance.thumbnail.path)
