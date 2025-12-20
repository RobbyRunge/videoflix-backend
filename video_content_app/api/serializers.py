from rest_framework import serializers

from video_content_app.models import Video


class VideoSerializer(serializers.ModelSerializer):
    """
    Serializer for Video model.
    Returns video metadata including thumbnail URL.
    """
    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = ['id', 'created_at', 'title',
                  'description', 'thumbnail_url', 'category']

    def get_thumbnail_url(self, obj):
        """
        Return full URL for thumbnail if it exists.
        """
        if obj.thumbnail:
            request = self.context.get('request')
            if request is not None:
                return request.build_absolute_uri(obj.thumbnail.url)
            return obj.thumbnail.url
        return None
