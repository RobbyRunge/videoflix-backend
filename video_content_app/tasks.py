import subprocess
import os
from django.conf import settings


def convert_to_hls(source_path, video_id):
    """
    Convert the given video to HLS format with multiple resolutions.
    Creates directory structure: media/videos/<video_id>/<resolution>/
    """
    base_dir = os.path.join(settings.MEDIA_ROOT, 'videos', str(video_id))

    resolutions = {
        '480p': {'size': '854x480', 'bitrate': '1000k'},
        '720p': {'size': '1280x720', 'bitrate': '2500k'},
        '1080p': {'size': '1920x1080', 'bitrate': '5000k'},
    }

    for resolution, params in resolutions.items():
        output_dir = os.path.join(base_dir, resolution)
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, 'index.m3u8')

        cmd = [
            'ffmpeg',
            '-i', source_path,
            '-vf', f"scale={params['size']}",
            '-c:v', 'libx264',
            '-b:v', params['bitrate'],
            '-c:a', 'aac',
            '-b:a', '128k',
            '-start_number', '0',
            '-hls_time', '10',
            '-hls_list_size', '0',
            '-f', 'hls',
            output_path
        ]
        subprocess.run(cmd, check=True)


def delete_original_video(source_path):
    """
    Delete the original video file after conversion is complete.
    """
    if os.path.isfile(source_path):
        os.remove(source_path)
