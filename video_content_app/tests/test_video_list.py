import pytest
from django.contrib.auth.models import User

from rest_framework import status

from video_content_app.models import Video


@pytest.mark.django_db
class TestVideoListView:
    """Test suite for video list endpoint."""

    def test_list_videos_authenticated(self, authenticated_client, multiple_videos):
        """Test retrieving video list as authenticated user."""
        response = authenticated_client.get('/api/video/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

        # Check that videos are ordered by created_at (descending)
        titles = [video['title'] for video in response.data]
        assert 'Test Video' in titles[0]

    def test_list_videos_unauthenticated(self, api_client, multiple_videos):
        """Test that unauthenticated users cannot access video list."""
        response = api_client.get('/api/video/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_videos_empty(self, authenticated_client):
        """Test retrieving empty video list."""
        response = authenticated_client.get('/api/video/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_list_videos_contains_metadata(self, authenticated_client, sample_video):
        """Test that video list contains all required metadata."""
        response = authenticated_client.get('/api/video/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

        video_data = response.data[0]
        assert 'id' in video_data
        assert 'title' in video_data
        assert 'description' in video_data
        assert 'category' in video_data
        assert 'created_at' in video_data
        assert 'thumbnail_url' in video_data

        assert video_data['title'] == 'Test Video'
        assert video_data['category'] == 'Action'

    def test_list_videos_thumbnail_url(self, authenticated_client, sample_video):
        """Test that thumbnail URL is properly generated."""
        response = authenticated_client.get('/api/video/')

        assert response.status_code == status.HTTP_200_OK
        video_data = response.data[0]

        # Should contain a URL if thumbnail exists
        if sample_video.thumbnail:
            assert video_data['thumbnail_url'] is not None
            assert 'http' in video_data['thumbnail_url']

    def test_list_videos_ordering(self, authenticated_client):
        """Test that videos are ordered by creation date (newest first)."""
        # Create videos in specific order
        video1 = Video.objects.create(
            title='First Video',
            description='First',
            category='Action'
        )
        video2 = Video.objects.create(
            title='Second Video',
            description='Second',
            category='Comedy'
        )
        video3 = Video.objects.create(
            title='Third Video',
            description='Third',
            category='Drama'
        )

        response = authenticated_client.get('/api/video/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

        # Newest should be first
        assert response.data[0]['title'] == 'Third Video'
        assert response.data[1]['title'] == 'Second Video'
        assert response.data[2]['title'] == 'First Video'

    def test_list_videos_filter_by_category(self, authenticated_client, multiple_videos):
        """Test filtering videos by category."""
        response = authenticated_client.get('/api/video/')

        assert response.status_code == status.HTTP_200_OK

        # Check that different categories exist
        categories = [video['category'] for video in response.data]
        assert 'Action' in categories
        assert 'Comedy' in categories
        assert 'Drama' in categories

    def test_list_videos_with_invalid_token(self, api_client, multiple_videos):
        """Test accessing video list with invalid authentication."""
        api_client.credentials(HTTP_AUTHORIZATION='Bearer invalid-token')
        response = api_client.get('/api/video/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_videos_performance(self, authenticated_client):
        """Test that listing many videos performs well."""
        # Create 50 videos
        videos = [
            Video(
                title=f'Video {i}',
                description=f'Description {i}',
                category='Action'
            )
            for i in range(50)
        ]
        Video.objects.bulk_create(videos)

        response = authenticated_client.get('/api/video/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 50
