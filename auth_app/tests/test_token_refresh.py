import pytest
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.mark.django_db
class TestCookieTokenRefreshView:
    """Test suite for JWT token refresh endpoint."""

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def user(self):
        """Create an active user for testing."""
        return User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='SecurePass123!',
            is_active=True
        )

    @pytest.fixture
    def logged_in_client(self, api_client, user):
        """Create a logged-in client with valid tokens."""
        response = api_client.post('/api/login/', {
            'email': 'testuser@example.com',
            'password': 'SecurePass123!'
        })
        return api_client

    def test_token_refresh_success_with_cookie(self, logged_in_client):
        """Test successful token refresh using cookie."""
        response = logged_in_client.post('/api/token/refresh/')

        assert response.status_code == status.HTTP_200_OK
        assert 'detail' in response.data
        assert 'access' in response.data
        assert 'access_token' in response.cookies

    def test_token_refresh_success_with_request_data(self, api_client, user):
        """Test successful token refresh using request data."""
        refresh = RefreshToken.for_user(user)
        data = {'refresh': str(refresh)}

        response = api_client.post('/api/token/refresh/', data)

        assert response.status_code == status.HTTP_200_OK
        assert 'detail' in response.data
        assert 'access' in response.data

    def test_token_refresh_without_token(self, api_client):
        """Test token refresh fails without refresh token."""
        response = api_client.post('/api/token/refresh/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'error' in response.data

    def test_token_refresh_with_invalid_token(self, api_client):
        """Test token refresh fails with invalid token."""
        data = {'refresh': 'invalid-token-123'}
        response = api_client.post('/api/token/refresh/', data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'error' in response.data

    def test_token_refresh_with_expired_token(self, api_client, user):
        """Test token refresh with potentially expired token."""
        # Create a refresh token
        refresh = RefreshToken.for_user(user)

        # Blacklist/invalidate the token if using blacklist
        # This test simulates an expired or blacklisted token
        data = {'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.expired'}

        response = api_client.post('/api/token/refresh/', data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'error' in response.data

    def test_token_refresh_updates_cookie(self, logged_in_client):
        """Test that token refresh updates the access_token cookie."""
        response = logged_in_client.post('/api/token/refresh/')

        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.cookies

        # Verify cookie properties
        cookie = response.cookies['access_token']
        assert cookie['httponly'] is True
        assert cookie['secure'] is True
        assert cookie['samesite'] == 'Lax'

    def test_token_refresh_multiple_times(self, logged_in_client):
        """Test that token can be refreshed multiple times."""
        # First refresh
        response1 = logged_in_client.post('/api/token/refresh/')
        assert response1.status_code == status.HTTP_200_OK
        token1 = response1.data['access']

        # Second refresh
        response2 = logged_in_client.post('/api/token/refresh/')
        assert response2.status_code == status.HTTP_200_OK
        token2 = response2.data['access']

        # Tokens should be different
        assert token1 != token2
