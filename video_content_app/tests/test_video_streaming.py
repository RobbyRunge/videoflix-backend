import pytest
import os
from django.conf import settings

from rest_framework import status

from video_content_app.models import Video


@pytest.mark.django_db
class TestVideoManifestView:
    """Test suite for HLS manifest endpoint."""

    def test_manifest_unauthenticated(self, api_client, sample_video):
        """Test that unauthenticated users cannot access manifest."""
        response = api_client.get(
            f'/api/video/{sample_video.id}/720p/index.m3u8'
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_manifest_nonexistent_video(self, authenticated_client):
        """Test accessing manifest for non-existent video."""
        response = authenticated_client.get(
            '/api/video/99999/720p/index.m3u8'
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_manifest_file_not_found(self, authenticated_client, sample_video):
        """Test accessing manifest when file doesn't exist."""
        response = authenticated_client.get(
            f'/api/video/{sample_video.id}/720p/index.m3u8'
        )

        # Should return 404 if manifest file doesn't exist
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_manifest_with_existing_file(self, authenticated_client, sample_video, tmp_path, settings):
        """Test accessing manifest when file exists."""
        # Create manifest directory and file
        manifest_dir = os.path.join(
            settings.MEDIA_ROOT,
            'videos',
            str(sample_video.id),
            '720p'
        )
        os.makedirs(manifest_dir, exist_ok=True)

        manifest_path = os.path.join(manifest_dir, 'index.m3u8')
        manifest_content = """#EXTM3U
#EXT-X-VERSION:3
#EXT-X-TARGETDURATION:10
#EXTINF:10.0,
segment0.ts
#EXT-X-ENDLIST
"""
        with open(manifest_path, 'w', encoding='utf-8') as f:
            f.write(manifest_content)

        response = authenticated_client.get(
            f'/api/video/{sample_video.id}/720p/index.m3u8'
        )

        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'application/vnd.apple.mpegurl'
        assert '#EXTM3U' in response.content.decode('utf-8')

    def test_manifest_different_resolutions(self, authenticated_client, sample_video, settings):
        """Test accessing manifests for different resolutions."""
        resolutions = ['480p', '720p', '1080p']

        for resolution in resolutions:
            # Create manifest file for each resolution
            manifest_dir = os.path.join(
                settings.MEDIA_ROOT,
                'videos',
                str(sample_video.id),
                resolution
            )
            os.makedirs(manifest_dir, exist_ok=True)

            manifest_path = os.path.join(manifest_dir, 'index.m3u8')
            with open(manifest_path, 'w', encoding='utf-8') as f:
                f.write(f'#EXTM3U\n#{resolution}\n')

            response = authenticated_client.get(
                f'/api/video/{sample_video.id}/{resolution}/index.m3u8'
            )

            assert response.status_code == status.HTTP_200_OK
            assert resolution in response.content.decode('utf-8')


@pytest.mark.django_db
class TestVideoSegmentView:
    """Test suite for HLS segment endpoint."""

    def test_segment_unauthenticated(self, api_client, sample_video):
        """Test that unauthenticated users cannot access segments."""
        response = api_client.get(
            f'/api/video/{sample_video.id}/720p/segment0.ts/'
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_segment_nonexistent_video(self, authenticated_client):
        """Test accessing segment for non-existent video."""
        response = authenticated_client.get(
            '/api/video/99999/720p/segment0.ts/'
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_segment_file_not_found(self, authenticated_client, sample_video):
        """Test accessing segment when file doesn't exist."""
        response = authenticated_client.get(
            f'/api/video/{sample_video.id}/720p/segment0.ts/'
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_segment_with_existing_file(self, authenticated_client, sample_video, settings):
        """Test accessing segment when file exists."""
        # Create segment directory and file
        segment_dir = os.path.join(
            settings.MEDIA_ROOT,
            'videos',
            str(sample_video.id),
            '720p'
        )
        os.makedirs(segment_dir, exist_ok=True)

        segment_path = os.path.join(segment_dir, 'segment0.ts')
        segment_content = b'fake video segment data'
        with open(segment_path, 'wb') as f:
            f.write(segment_content)

        response = authenticated_client.get(
            f'/api/video/{sample_video.id}/720p/segment0.ts/'
        )

        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'video/MP2T'
        # FileResponse uses streaming_content, read it to compare
        content = b''.join(response.streaming_content)
        assert content == segment_content

    def test_segment_different_names(self, authenticated_client, sample_video, settings):
        """Test accessing different segment files."""
        segment_names = ['segment0.ts', 'segment1.ts', 'segment2.ts']

        segment_dir = os.path.join(
            settings.MEDIA_ROOT,
            'videos',
            str(sample_video.id),
            '720p'
        )
        os.makedirs(segment_dir, exist_ok=True)

        for segment_name in segment_names:
            segment_path = os.path.join(segment_dir, segment_name)
            with open(segment_path, 'wb') as f:
                f.write(f'segment {segment_name}'.encode())

            response = authenticated_client.get(
                f'/api/video/{sample_video.id}/720p/{segment_name}/'
            )

            assert response.status_code == status.HTTP_200_OK
            # FileResponse uses streaming_content
            content = b''.join(response.streaming_content)
            assert segment_name.encode() in content

    def test_segment_invalid_path(self, authenticated_client, sample_video, settings):
        """Test accessing segment with path traversal attempt."""
        # Attempt path traversal
        response = authenticated_client.get(
            f'/api/video/{sample_video.id}/720p/../../../etc/passwd/'
        )

        # Should be blocked or return 404
        assert response.status_code in [
            status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST]
