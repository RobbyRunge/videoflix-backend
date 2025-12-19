import pytest
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestLoginView:
    """Test suite for user login endpoint."""

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def active_user(self):
        """Create an active user for testing."""
        user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='SecurePass123!',
            is_active=True
        )
        return user

    @pytest.fixture
    def inactive_user(self):
        """Create an inactive user for testing."""
        user = User.objects.create_user(
            username='inactive@example.com',
            email='inactive@example.com',
            password='SecurePass123!',
            is_active=False
        )
        return user

    def test_login_success(self, api_client, active_user):
        """Test successful login with valid credentials."""
        data = {
            'email': 'testuser@example.com',
            'password': 'SecurePass123!'
        }
        response = api_client.post('/api/login/', data)

        assert response.status_code == status.HTTP_200_OK
        assert 'detail' in response.data
        assert response.data['detail'] == 'Login successful'
        assert 'user' in response.data
        assert response.data['user']['username'] == active_user.email

        # Verify cookies are set
        assert 'access_token' in response.cookies
        assert 'refresh_token' in response.cookies
        assert response.cookies['access_token']['httponly'] is True
        assert response.cookies['refresh_token']['httponly'] is True

    def test_login_invalid_email(self, api_client):
        """Test login fails with non-existent email."""
        data = {
            'email': 'nonexistent@example.com',
            'password': 'SecurePass123!'
        }
        response = api_client.post('/api/login/', data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'detail' in response.data
        assert response.data['detail'] == 'Invalid credentials'

    def test_login_invalid_password(self, api_client, active_user):
        """Test login fails with incorrect password."""
        data = {
            'email': 'testuser@example.com',
            'password': 'WrongPassword123!'
        }
        response = api_client.post('/api/login/', data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'detail' in response.data
        assert response.data['detail'] == 'Invalid credentials'

    def test_login_inactive_account(self, api_client, inactive_user):
        """Test login fails for inactive account."""
        data = {
            'email': 'inactive@example.com',
            'password': 'SecurePass123!'
        }
        response = api_client.post('/api/login/', data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'detail' in response.data

    def test_login_missing_email(self, api_client):
        """Test login fails with missing email."""
        data = {'password': 'SecurePass123!'}
        response = api_client.post('/api/login/', data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'detail' in response.data

    def test_login_missing_password(self, api_client):
        """Test login fails with missing password."""
        data = {'email': 'testuser@example.com'}
        response = api_client.post('/api/login/', data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'detail' in response.data

    def test_login_empty_credentials(self, api_client):
        """Test login fails with empty credentials."""
        data = {'email': '', 'password': ''}
        response = api_client.post('/api/login/', data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'detail' in response.data

    def test_login_invalid_email_format(self, api_client):
        """Test login fails with invalid email format."""
        data = {
            'email': 'not-an-email',
            'password': 'SecurePass123!'
        }
        response = api_client.post('/api/login/', data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert 'detail' in response.data


@pytest.mark.django_db
class TestLogoutView:
    """Test suite for user logout endpoint."""

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def logged_in_client(self, api_client):
        """Create a logged-in client with tokens."""
        user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='SecurePass123!',
            is_active=True
        )

        # Login to get cookies
        api_client.post('/api/login/', {
            'email': 'testuser@example.com',
            'password': 'SecurePass123!'
        })
        return api_client

    def test_logout_success(self, logged_in_client):
        """Test successful logout."""
        response = logged_in_client.post('/api/logout/')

        assert response.status_code == status.HTTP_200_OK
        assert 'detail' in response.data

        # Verify cookies are deleted (value should be empty string or None)
        access_cookie = response.cookies.get(
            'access_token', {}).get('value', '')
        refresh_cookie = response.cookies.get(
            'refresh_token', {}).get('value', '')
        assert access_cookie in ['', None]
        assert refresh_cookie in ['', None]

    def test_logout_without_login(self, api_client):
        """Test logout without being logged in."""
        response = api_client.post('/api/logout/')

        # Should still succeed
        assert response.status_code == status.HTTP_200_OK
