import pytest
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core import mail

from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestPasswordResetView:
    """Test suite for password reset request endpoint."""

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def user(self):
        """Create a user for password reset testing."""
        return User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='OldPassword123!',
            is_active=True
        )

    def test_password_reset_request_success(self, api_client, user):
        """Test successful password reset request."""
        data = {'email': 'testuser@example.com'}
        response = api_client.post('/api/password_reset/', data)

        assert response.status_code == status.HTTP_200_OK
        assert 'detail' in response.data
        assert 'email has been sent' in response.data['detail']

        # Verify email was sent
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == 'Reset Your Videoflix Password'
        assert user.email in mail.outbox[0].to

    def test_password_reset_request_nonexistent_email(self, api_client):
        """Test password reset request with non-existent email."""
        data = {'email': 'nonexistent@example.com'}
        response = api_client.post('/api/password_reset/', data)

        # Should return success for security reasons (don't reveal user existence)
        assert response.status_code == status.HTTP_200_OK
        assert 'detail' in response.data

        # No email should be sent
        assert len(mail.outbox) == 0

    def test_password_reset_request_invalid_email_format(self, api_client):
        """Test password reset request with invalid email format."""
        data = {'email': 'not-an-email'}
        response = api_client.post('/api/password_reset/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data

    def test_password_reset_request_missing_email(self, api_client):
        """Test password reset request with missing email."""
        response = api_client.post('/api/password_reset/', {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data

    def test_password_reset_request_empty_email(self, api_client):
        """Test password reset request with empty email."""
        data = {'email': ''}
        response = api_client.post('/api/password_reset/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data


@pytest.mark.django_db
class TestPasswordResetConfirmView:
    """Test suite for password reset confirmation endpoint."""

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def user(self):
        """Create a user for password reset confirmation testing."""
        return User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='OldPassword123!',
            is_active=True
        )

    def test_password_reset_confirm_success(self, api_client, user):
        """Test successful password reset confirmation."""
        token = default_token_generator.make_token(user)
        data = {
            'new_password': 'NewSecurePass456!',
            'confirm_password': 'NewSecurePass456!'
        }

        response = api_client.post(
            f'/api/password_confirm/{user.pk}/{token}/',
            data
        )

        assert response.status_code == status.HTTP_200_OK
        assert 'detail' in response.data
        assert 'successfully reset' in response.data['detail']

        # Verify password was changed
        user.refresh_from_db()
        assert user.check_password('NewSecurePass456!')
        assert not user.check_password('OldPassword123!')

    def test_password_reset_confirm_password_mismatch(self, api_client, user):
        """Test password reset fails when passwords don't match."""
        token = default_token_generator.make_token(user)
        data = {
            'new_password': 'NewSecurePass456!',
            'confirm_password': 'DifferentPass789!'
        }

        response = api_client.post(
            f'/api/password_confirm/{user.pk}/{token}/',
            data
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'confirm_password' in response.data

        # Verify password was not changed
        user.refresh_from_db()
        assert user.check_password('OldPassword123!')

    def test_password_reset_confirm_invalid_token(self, api_client, user):
        """Test password reset fails with invalid token."""
        invalid_token = 'invalid-token-123'
        data = {
            'new_password': 'NewSecurePass456!',
            'confirm_password': 'NewSecurePass456!'
        }

        response = api_client.post(
            f'/api/password_confirm/{user.pk}/{invalid_token}/',
            data
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

        # Verify password was not changed
        user.refresh_from_db()
        assert user.check_password('OldPassword123!')

    def test_password_reset_confirm_invalid_user_id(self, api_client):
        """Test password reset fails with invalid user ID."""
        invalid_uid = 99999
        token = 'some-token'
        data = {
            'new_password': 'NewSecurePass456!',
            'confirm_password': 'NewSecurePass456!'
        }

        response = api_client.post(
            f'/api/password_confirm/{invalid_uid}/{token}/',
            data
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_password_reset_confirm_short_password(self, api_client, user):
        """Test password reset fails with password shorter than 8 characters."""
        token = default_token_generator.make_token(user)
        data = {
            'new_password': 'Short1!',
            'confirm_password': 'Short1!'
        }

        response = api_client.post(
            f'/api/password_confirm/{user.pk}/{token}/',
            data
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'new_password' in response.data

    def test_password_reset_confirm_missing_new_password(self, api_client, user):
        """Test password reset fails with missing new_password."""
        token = default_token_generator.make_token(user)
        data = {'confirm_password': 'NewSecurePass456!'}

        response = api_client.post(
            f'/api/password_confirm/{user.pk}/{token}/',
            data
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'new_password' in response.data

    def test_password_reset_confirm_missing_confirm_password(self, api_client, user):
        """Test password reset fails with missing confirm_password."""
        token = default_token_generator.make_token(user)
        data = {'new_password': 'NewSecurePass456!'}

        response = api_client.post(
            f'/api/password_confirm/{user.pk}/{token}/',
            data
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'confirm_password' in response.data

    def test_password_reset_confirm_expired_token(self, api_client, user):
        """Test password reset with potentially expired token."""
        # Generate a token
        token = default_token_generator.make_token(user)

        # Change user's password (this invalidates old tokens)
        user.set_password('ChangedPassword!')
        user.save()

        data = {
            'new_password': 'NewSecurePass456!',
            'confirm_password': 'NewSecurePass456!'
        }

        response = api_client.post(
            f'/api/password_confirm/{user.pk}/{token}/',
            data
        )

        # Token should be invalid after password change
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data
