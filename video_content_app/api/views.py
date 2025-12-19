import os
from django.http import FileResponse, HttpResponse, Http404
from django.conf import settings

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from video_content_app.models import Video
from video_content_app.api.serializers import VideoSerializer


class VideoListView(APIView):
    """
    API view to retrieve all available videos.
    Requires JWT authentication.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        GET /api/video/
        Returns a list of all available videos with metadata.
        """
        try:
            videos = Video.objects.all()
            serializer = VideoSerializer(
                videos, many=True, context={'request': request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"detail": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class VideoManifestView(APIView):
    """
    API view to serve HLS manifest (index.m3u8) for a specific video and resolution.
    Requires JWT authentication.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution):
        """
        GET /api/video/<movie_id>/<resolution>/index.m3u8
        Returns the HLS master playlist for a specific movie and resolution.
        """
        try:
            Video.objects.get(id=movie_id)
        except Video.DoesNotExist:
            raise Http404("Video not found")

        manifest_path = os.path.join(
            settings.MEDIA_ROOT,
            'videos',
            f'{movie_id}',
            resolution,
            'index.m3u8'
        )

        if not os.path.exists(manifest_path):
            raise Http404("Manifest not found")

        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return HttpResponse(
                content,
                content_type='application/vnd.apple.mpegurl',
                status=status.HTTP_200_OK
            )
        except Exception:
            raise Http404("Error reading manifest file")


class VideoSegmentView(APIView):
    """
    API view to serve HLS video segments for a specific video and resolution.
    Requires JWT authentication.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, movie_id, resolution, segment):
        """
        GET /api/video/<movie_id>/<resolution>/<segment>/
        Returns a single HLS video segment for a specific movie and resolution.
        """
        try:
            Video.objects.get(id=movie_id)
        except Video.DoesNotExist:
            raise Http404("Video not found")

        segment_path = os.path.join(
            settings.MEDIA_ROOT,
            'videos',
            f'{movie_id}',
            resolution,
            segment
        )

        if not os.path.exists(segment_path):
            raise Http404("Segment not found")

        try:
            return FileResponse(
                open(segment_path, 'rb'),
                content_type='video/MP2T',
                status=status.HTTP_200_OK
            )
        except Exception:
            raise Http404("Error reading segment file")
