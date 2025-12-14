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
        except Exception as e:
            return Response(
                {"detail": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
