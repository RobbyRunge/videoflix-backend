"""
Pytest configuration and shared fixtures for video_content_app tests.
"""
import pytest
import os
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User

from rest_framework.test import APIClient
from video_content_app.models import Video


@pytest.fixture
def api_client():
    """Provides a DRF API client for testing."""
    return APIClient()


@pytest.fixture
def authenticated_user(db):
    """Create an authenticated user for testing."""
    user = User.objects.create_user(
        username='testuser@example.com',
        email='testuser@example.com',
        password='SecurePass123!',
        is_active=True
    )
    return user


@pytest.fixture
def authenticated_client(api_client, authenticated_user):
    """Create an authenticated API client."""
    api_client.force_authenticate(user=authenticated_user)
    return api_client


@pytest.fixture
def sample_video(db, tmp_path):
    """Create a sample video for testing."""
    # Create a simple test image for thumbnail
    thumbnail = SimpleUploadedFile(
        name='test_thumbnail.jpg',
        content=b'fake image content',
        content_type='image/jpeg'
    )

    video = Video.objects.create(
        title='Test Video',
        description='This is a test video description',
        category='Action',
        thumbnail=thumbnail
    )
    return video


@pytest.fixture
def multiple_videos(db):
    """Create multiple videos for testing."""
    videos = []
    categories = ['Action', 'Comedy', 'Drama']

    for i, category in enumerate(categories, 1):
        video = Video.objects.create(
            title=f'Test Video {i}',
            description=f'Description for test video {i}',
            category=category
        )
        videos.append(video)

    return videos


@pytest.fixture(autouse=True)
def clear_media_files(settings, tmp_path):
    """Use temporary directory for media files during tests."""
    settings.MEDIA_ROOT = str(tmp_path / 'media')
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
