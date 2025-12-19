import pytest
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core import mail

from rest_framework import status
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestRegisterView:
    """Test suite for user registration endpoint."""

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def valid_registration_data(self):
        return {
            'email': 'testuser@example.com',
            'password': 'SecurePass123!',
            'confirmed_password': 'SecurePass123!'
        }

    def test_register_user_success(self, api_client, valid_registration_data):
        """Test successful user registration."""
        response = api_client.post(
            '/api/register/', valid_registration_data)

        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert 'token' in response.data
        assert response.data['user']['email'] == valid_registration_data['email']

        # Verify user was created in database
        user = User.objects.get(email=valid_registration_data['email'])
        assert user is not None
        assert user.username == valid_registration_data['email']
        assert user.is_active is False

        # Verify activation email was sent
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == 'Activate Your Videoflix Account'
        assert valid_registration_data['email'] in mail.outbox[0].to

    def test_register_user_password_mismatch(self, api_client):
        """Test registration fails when passwords don't match."""
        data = {
            'email': 'testuser@example.com',
            'password': 'SecurePass123!',
            'confirmed_password': 'DifferentPass123!'
        }
        response = api_client.post('/api/register/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data
        assert User.objects.filter(email=data['email']).count() == 0

    def test_register_user_duplicate_email(self, api_client, valid_registration_data):
        """Test registration fails with duplicate email."""
        # Create first user
        User.objects.create_user(
            username=valid_registration_data['email'],
            email=valid_registration_data['email'],
            password=valid_registration_data['password']
        )

        # Try to register with same email
        response = api_client.post(
            '/api/register/', valid_registration_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data

    def test_register_user_missing_fields(self, api_client):
        """Test registration fails with missing required fields."""
        data = {'email': 'testuser@example.com'}
        response = api_client.post('/api/register/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'password' in response.data or 'confirmed_password' in response.data

    def test_register_user_invalid_email(self, api_client):
        """Test registration fails with invalid email format."""
        data = {
            'email': 'invalid-email',
            'password': 'SecurePass123!',
            'confirmed_password': 'SecurePass123!'
        }
        response = api_client.post('/api/register/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in response.data

    def test_register_user_empty_password(self, api_client):
        """Test registration fails with empty password."""
        data = {
            'email': 'testuser@example.com',
            'password': '',
            'confirmed_password': ''
        }
        response = api_client.post('/api/register/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestActivateAccountView:
    """Test suite for account activation endpoint."""

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.fixture
    def inactive_user(self):
        return User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='SecurePass123!',
            is_active=False
        )

    def test_activate_account_success(self, api_client, inactive_user):
        """Test successful account activation."""
        token = default_token_generator.make_token(inactive_user)

        response = api_client.get(
            f'/api/activate/{inactive_user.pk}/{token}/'
        )

        assert response.status_code == status.HTTP_200_OK
        assert 'message' in response.data

        # Verify user is now active
        inactive_user.refresh_from_db()
        assert inactive_user.is_active is True

    def test_activate_account_invalid_token(self, api_client, inactive_user):
        """Test activation fails with invalid token."""
        invalid_token = 'invalid-token-123'

        response = api_client.get(
            f'/api/activate/{inactive_user.pk}/{invalid_token}/'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

        # Verify user is still inactive
        inactive_user.refresh_from_db()
        assert inactive_user.is_active is False

    def test_activate_account_invalid_user_id(self, api_client):
        """Test activation fails with invalid user ID."""
        invalid_uid = 99999
        token = 'some-token'

        response = api_client.get(
            f'/api/activate/{invalid_uid}/{token}/'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_activate_already_active_user(self, api_client):
        """Test activating an already active user."""
        active_user = User.objects.create_user(
            username='active@example.com',
            email='active@example.com',
            password='SecurePass123!',
            is_active=True
        )
        token = default_token_generator.make_token(active_user)

        response = api_client.get(
            f'/api/activate/{active_user.pk}/{token}/'
        )

        # Should still succeed even if already active
        assert response.status_code == status.HTTP_200_OK
