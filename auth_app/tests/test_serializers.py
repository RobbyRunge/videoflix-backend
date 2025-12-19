import pytest
from django.contrib.auth.models import User

from auth_app.api.serializers import (
    RegistrationSerializer,
    EmailTokenObtainPairSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer
)


@pytest.mark.django_db
class TestRegistrationSerializer:
    """Test suite for RegistrationSerializer."""

    def test_valid_registration_data(self):
        """Test serializer with valid registration data."""
        data = {
            'email': 'testuser@example.com',
            'password': 'SecurePass123!',
            'confirmed_password': 'SecurePass123!'
        }
        serializer = RegistrationSerializer(data=data)

        assert serializer.is_valid()
        user = serializer.save()

        assert user.email == data['email']
        assert user.username == data['email']
        assert user.check_password(data['password'])
        assert user.is_active is False

    def test_password_mismatch(self):
        """Test validation fails when passwords don't match."""
        data = {
            'email': 'testuser@example.com',
            'password': 'SecurePass123!',
            'confirmed_password': 'DifferentPass456!'
        }
        serializer = RegistrationSerializer(data=data)

        assert not serializer.is_valid()
        assert 'password' in serializer.errors

    def test_duplicate_email(self):
        """Test validation fails with duplicate email."""
        # Create existing user
        User.objects.create_user(
            username='existing@example.com',
            email='existing@example.com',
            password='Password123!'
        )

        data = {
            'email': 'existing@example.com',
            'password': 'SecurePass123!',
            'confirmed_password': 'SecurePass123!'
        }
        serializer = RegistrationSerializer(data=data)

        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_invalid_email_format(self):
        """Test validation fails with invalid email format."""
        data = {
            'email': 'not-an-email',
            'password': 'SecurePass123!',
            'confirmed_password': 'SecurePass123!'
        }
        serializer = RegistrationSerializer(data=data)

        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_missing_email(self):
        """Test validation fails with missing email."""
        data = {
            'password': 'SecurePass123!',
            'confirmed_password': 'SecurePass123!'
        }
        serializer = RegistrationSerializer(data=data)

        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_missing_password(self):
        """Test validation fails with missing password."""
        data = {
            'email': 'testuser@example.com',
            'confirmed_password': 'SecurePass123!'
        }
        serializer = RegistrationSerializer(data=data)

        assert not serializer.is_valid()
        assert 'password' in serializer.errors

    def test_missing_confirmed_password(self):
        """Test validation fails with missing confirmed_password."""
        data = {
            'email': 'testuser@example.com',
            'password': 'SecurePass123!'
        }
        serializer = RegistrationSerializer(data=data)

        assert not serializer.is_valid()
        assert 'confirmed_password' in serializer.errors


@pytest.mark.django_db
class TestEmailTokenObtainPairSerializer:
    """Test suite for EmailTokenObtainPairSerializer."""

    @pytest.fixture
    def active_user(self):
        """Create an active user for testing."""
        return User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='SecurePass123!',
            is_active=True
        )

    def test_valid_login_data(self, active_user):
        """Test serializer with valid login data."""
        data = {
            'email': 'testuser@example.com',
            'password': 'SecurePass123!'
        }
        serializer = EmailTokenObtainPairSerializer(data=data)

        assert serializer.is_valid()
        # The serializer should have converted email to username internally
        assert 'access' in serializer.validated_data
        assert 'refresh' in serializer.validated_data

    def test_invalid_email_nonexistent(self):
        """Test validation fails with non-existent email."""
        data = {
            'email': 'nonexistent@example.com',
            'password': 'SecurePass123!'
        }
        serializer = EmailTokenObtainPairSerializer(data=data)

        assert not serializer.is_valid()

    def test_invalid_email_format(self, active_user):
        """Test validation fails with invalid email format."""
        data = {
            'email': 'not-an-email',
            'password': 'SecurePass123!'
        }
        serializer = EmailTokenObtainPairSerializer(data=data)

        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_missing_email(self):
        """Test validation fails with missing email."""
        data = {'password': 'SecurePass123!'}
        serializer = EmailTokenObtainPairSerializer(data=data)

        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_missing_password(self):
        """Test validation fails with missing password."""
        data = {'email': 'testuser@example.com'}
        serializer = EmailTokenObtainPairSerializer(data=data)

        assert not serializer.is_valid()
        assert 'password' in serializer.errors

    def test_empty_credentials(self):
        """Test validation fails with empty credentials."""
        data = {'email': '', 'password': ''}
        serializer = EmailTokenObtainPairSerializer(data=data)

        assert not serializer.is_valid()

    @pytest.mark.django_db
    def test_inactive_user(self):
        """Test validation fails for inactive user."""
        from rest_framework.exceptions import AuthenticationFailed

        inactive_user = User.objects.create_user(
            username='inactive@example.com',
            email='inactive@example.com',
            password='SecurePass123!',
            is_active=False
        )
        data = {
            'email': 'inactive@example.com',
            'password': 'SecurePass123!'
        }
        serializer = EmailTokenObtainPairSerializer(data=data)

        # Inactive users will raise AuthenticationFailed during validation
        with pytest.raises(AuthenticationFailed):
            serializer.is_valid(raise_exception=True)


class TestPasswordResetSerializer:
    """Test suite for PasswordResetSerializer."""

    def test_valid_email(self):
        """Test serializer with valid email."""
        data = {'email': 'testuser@example.com'}
        serializer = PasswordResetSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data['email'] == data['email']

    def test_invalid_email_format(self):
        """Test validation fails with invalid email format."""
        data = {'email': 'not-an-email'}
        serializer = PasswordResetSerializer(data=data)

        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_missing_email(self):
        """Test validation fails with missing email."""
        serializer = PasswordResetSerializer(data={})

        assert not serializer.is_valid()
        assert 'email' in serializer.errors

    def test_empty_email(self):
        """Test validation fails with empty email."""
        data = {'email': ''}
        serializer = PasswordResetSerializer(data=data)

        assert not serializer.is_valid()
        assert 'email' in serializer.errors


class TestPasswordResetConfirmSerializer:
    """Test suite for PasswordResetConfirmSerializer."""

    def test_valid_password_reset_data(self):
        """Test serializer with valid password reset data."""
        data = {
            'new_password': 'NewSecurePass456!',
            'confirm_password': 'NewSecurePass456!'
        }
        serializer = PasswordResetConfirmSerializer(data=data)

        assert serializer.is_valid()
        assert serializer.validated_data['new_password'] == data['new_password']

    def test_password_mismatch(self):
        """Test validation fails when passwords don't match."""
        data = {
            'new_password': 'NewSecurePass456!',
            'confirm_password': 'DifferentPass789!'
        }
        serializer = PasswordResetConfirmSerializer(data=data)

        assert not serializer.is_valid()
        assert 'confirm_password' in serializer.errors

    def test_password_too_short(self):
        """Test validation fails with password shorter than 8 characters."""
        data = {
            'new_password': 'Short1!',
            'confirm_password': 'Short1!'
        }
        serializer = PasswordResetConfirmSerializer(data=data)

        assert not serializer.is_valid()
        assert 'new_password' in serializer.errors

    def test_missing_new_password(self):
        """Test validation fails with missing new_password."""
        data = {'confirm_password': 'NewSecurePass456!'}
        serializer = PasswordResetConfirmSerializer(data=data)

        assert not serializer.is_valid()
        assert 'new_password' in serializer.errors

    def test_missing_confirm_password(self):
        """Test validation fails with missing confirm_password."""
        data = {'new_password': 'NewSecurePass456!'}
        serializer = PasswordResetConfirmSerializer(data=data)

        assert not serializer.is_valid()
        assert 'confirm_password' in serializer.errors

    def test_empty_passwords(self):
        """Test validation fails with empty passwords."""
        data = {
            'new_password': '',
            'confirm_password': ''
        }
        serializer = PasswordResetConfirmSerializer(data=data)

        assert not serializer.is_valid()
