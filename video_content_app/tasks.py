import subprocess
import os


def convert_480p(source_path):
    """
    Convert the given video to 480p resolution using ffmpeg.
    """
    target = source_path + '_480p.mp4'
    cmd = [
        'ffmpeg',
        '-i', source_path,
        '-s', 'hd480',
        '-c:v', 'libx264',
        '-crf', '23',
        '-c:a', 'aac',
        '-strict', '-2',
        target
    ]
    subprocess.run(cmd)


def convert_720p(source_path):
    """
    Convert the given video to 720p resolution using ffmpeg.
    """
    target = source_path + '_720p.mp4'
    cmd = [
        'ffmpeg',
        '-i', source_path,
        '-s', 'hd720',
        '-c:v', 'libx264',
        '-crf', '23',
        '-c:a', 'aac',
        '-strict', '-2',
        target
    ]
    subprocess.run(cmd)


def convert_1080p(source_path):
    """
    Convert the given video to 1080p resolution using ffmpeg.
    """
    target = source_path + '_1080p.mp4'
    cmd = [
        'ffmpeg',
        '-i', source_path,
        '-s', 'hd1080',
        '-c:v', 'libx264',
        '-crf', '23',
        '-c:a', 'aac',
        '-strict', '-2',
        target
    ]
    subprocess.run(cmd)


def delete_original_video(source_path):
    """
    Delete the original video file after conversion is complete.
    """
    if os.path.isfile(source_path):
        os.remove(source_path)
