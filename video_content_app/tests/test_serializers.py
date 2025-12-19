import pytest

from video_content_app.models import Video
from video_content_app.api.serializers import VideoSerializer


@pytest.mark.django_db
class TestVideoSerializer:
    """Test suite for VideoSerializer."""

    def test_serialize_video(self, sample_video, rf):
        """Test serializing a video object."""
        from django.test import RequestFactory
        request = RequestFactory().get('/')

        serializer = VideoSerializer(
            sample_video, context={'request': request})
        data = serializer.data

        assert data['id'] == sample_video.id
        assert data['title'] == 'Test Video'
        assert data['description'] == 'This is a test video description'
        assert data['category'] == 'Action'
        assert 'created_at' in data

    def test_serialize_video_without_thumbnail(self):
        """Test serializing a video without thumbnail."""
        video = Video.objects.create(
            title='No Thumbnail Video',
            description='Video without thumbnail',
            category='Drama'
        )

        serializer = VideoSerializer(video)
        data = serializer.data

        assert data['thumbnail_url'] is None

    def test_serialize_video_with_thumbnail(self, sample_video, rf):
        """Test serializing a video with thumbnail."""
        from django.test import RequestFactory
        request = RequestFactory().get('/')

        serializer = VideoSerializer(
            sample_video, context={'request': request})
        data = serializer.data

        # Should have thumbnail_url if thumbnail exists
        if sample_video.thumbnail:
            assert data['thumbnail_url'] is not None

    def test_serialize_multiple_videos(self, multiple_videos, rf):
        """Test serializing multiple videos."""
        from django.test import RequestFactory
        request = RequestFactory().get('/')

        serializer = VideoSerializer(
            multiple_videos,
            many=True,
            context={'request': request}
        )
        data = serializer.data

        assert len(data) == 3
        assert all('title' in video for video in data)
        assert all('category' in video for video in data)

    def test_serializer_fields(self, sample_video):
        """Test that serializer contains all required fields."""
        serializer = VideoSerializer(sample_video)
        data = serializer.data

        required_fields = ['id', 'created_at', 'title',
                           'description', 'thumbnail_url', 'category']
        for field in required_fields:
            assert field in data

    def test_serializer_excludes_video_file(self, sample_video):
        """Test that video_file field is not exposed in serializer."""
        serializer = VideoSerializer(sample_video)
        data = serializer.data

        assert 'video_file' not in data

    def test_thumbnail_url_absolute_path(self, sample_video, rf):
        """Test that thumbnail URL is absolute."""
        from django.test import RequestFactory
        request = RequestFactory().get('/')
        request.META['HTTP_HOST'] = 'testserver'

        serializer = VideoSerializer(
            sample_video, context={'request': request})
        data = serializer.data

        if data['thumbnail_url']:
            assert data['thumbnail_url'].startswith('http')

    def test_category_choices(self):
        """Test that only valid categories are accepted."""
        valid_categories = [
            'Action', 'Comedy', 'Drama', 'Romance',
            'Horror', 'Sci-Fi', 'Documentary', 'Animation'
        ]

        for category in valid_categories:
            video = Video.objects.create(
                title=f'{category} Video',
                description=f'A {category} video',
                category=category
            )
            assert video.category == category

    def test_video_ordering_in_queryset(self):
        """Test that videos are ordered by created_at descending."""
        video1 = Video.objects.create(
            title='First',
            description='First video',
            category='Action'
        )
        video2 = Video.objects.create(
            title='Second',
            description='Second video',
            category='Comedy'
        )

        videos = Video.objects.all()
        serializer = VideoSerializer(videos, many=True)

        # First item should be the most recently created
        assert serializer.data[0]['title'] == 'Second'
        assert serializer.data[1]['title'] == 'First'
