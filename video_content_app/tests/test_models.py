import pytest

from video_content_app.models import Video


@pytest.mark.django_db
class TestVideoModel:
    """Test suite for Video model."""

    def test_create_video(self):
        """Test creating a video."""
        video = Video.objects.create(
            title='Test Video',
            description='Test description',
            category='Action'
        )

        assert video.id is not None
        assert video.title == 'Test Video'
        assert video.description == 'Test description'
        assert video.category == 'Action'
        assert video.created_at is not None

    def test_video_str_representation(self):
        """Test video string representation."""
        video = Video.objects.create(
            title='My Awesome Video',
            description='Description',
            category='Comedy'
        )

        assert str(video) == 'My Awesome Video'

    def test_video_ordering(self):
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
        video3 = Video.objects.create(
            title='Third',
            description='Third video',
            category='Drama'
        )

        videos = Video.objects.all()
        assert videos[0].title == 'Third'
        assert videos[1].title == 'Second'
        assert videos[2].title == 'First'

    def test_valid_categories(self):
        """Test all valid category choices."""
        valid_categories = [
            'Action', 'Comedy', 'Drama', 'Romance',
            'Horror', 'Sci-Fi', 'Documentary', 'Animation'
        ]

        for category in valid_categories:
            video = Video.objects.create(
                title=f'{category} Video',
                description='Test',
                category=category
            )
            assert video.category == category

    def test_video_with_thumbnail(self, sample_video):
        """Test video with thumbnail."""
        assert sample_video.thumbnail is not None
        assert sample_video.thumbnail.name

    def test_video_without_thumbnail(self):
        """Test video without thumbnail."""
        video = Video.objects.create(
            title='No Thumbnail',
            description='Video without thumbnail',
            category='Drama'
        )

        # FileField can be empty string or falsy (None/'')
        assert not video.thumbnail

    def test_video_fields_max_length(self):
        """Test video field max lengths."""
        # Title max length is 200
        long_title = 'A' * 200
        video = Video.objects.create(
            title=long_title,
            description='Test',
            category='Action'
        )
        assert len(video.title) == 200

    def test_video_description_text_field(self):
        """Test that description can hold long text."""
        long_description = 'Long description. ' * 100
        video = Video.objects.create(
            title='Long Desc Video',
            description=long_description,
            category='Drama'
        )

        assert video.description == long_description
        assert len(video.description) > 1000

    def test_video_default_values(self):
        """Test video default values."""
        video = Video.objects.create(
            title='Test',
            description='Test',
            category='Action'
        )

        # created_at should be auto-set
        assert video.created_at is not None
        # thumbnail and video_file are optional (falsy when not set)
        assert not video.thumbnail
        assert not video.video_file

    def test_video_update(self):
        """Test updating video fields."""
        video = Video.objects.create(
            title='Original Title',
            description='Original description',
            category='Action'
        )

        video.title = 'Updated Title'
        video.description = 'Updated description'
        video.category = 'Comedy'
        video.save()

        updated_video = Video.objects.get(id=video.id)
        assert updated_video.title == 'Updated Title'
        assert updated_video.description == 'Updated description'
        assert updated_video.category == 'Comedy'

    def test_video_delete(self):
        """Test deleting a video."""
        video = Video.objects.create(
            title='To Delete',
            description='Will be deleted',
            category='Horror'
        )
        video_id = video.id

        video.delete()

        assert Video.objects.filter(id=video_id).count() == 0

    def test_multiple_videos_same_category(self):
        """Test creating multiple videos with same category."""
        for i in range(5):
            Video.objects.create(
                title=f'Action Video {i}',
                description=f'Description {i}',
                category='Action'
            )

        action_videos = Video.objects.filter(category='Action')
        assert action_videos.count() == 5
