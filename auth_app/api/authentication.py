from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT Authentication that reads the access token from cookies.
    """

    def authenticate(self, request):
        # Try to get token from cookie
        raw_token = request.COOKIES.get('access_token')

        if raw_token is None:
            return None

        # Validate the token
        validated_token = self.get_validated_token(raw_token)

        # Return user and token
        return self.get_user(validated_token), validated_token
