import pytest
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from unittest.mock import patch

from auth_app.api.signals import user_registered, password_reset_requested


@pytest.mark.django_db
class TestUserRegisteredSignal:
    """Test suite for user_registered signal."""

    @pytest.fixture
    def user(self):
        """Create a user for signal testing."""
        return User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='SecurePass123!',
            is_active=False
        )

    def test_activation_email_sent_on_registration(self, user):
        """Test that activation email is sent when user_registered signal is fired."""
        token = default_token_generator.make_token(user)

        # Send signal
        user_registered.send(
            sender=self.__class__,
            user=user,
            token=token
        )

        # Verify email was sent
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == 'Activate Your Videoflix Account'
        assert user.email in mail.outbox[0].to
        assert 'activate.html' in mail.outbox[0].body

    def test_activation_email_contains_correct_user_info(self, user):
        """Test that activation email contains correct user information."""
        token = default_token_generator.make_token(user)

        user_registered.send(
            sender=self.__class__,
            user=user,
            token=token
        )

        email = mail.outbox[0]
        # Check that email contains activation link components
        assert str(user.pk) in email.body
        assert token in email.body

    def test_activation_email_html_message(self, user):
        """Test that activation email includes HTML message."""
        token = default_token_generator.make_token(user)

        user_registered.send(
            sender=self.__class__,
            user=user,
            token=token
        )

        email = mail.outbox[0]
        assert email.alternatives is not None
        assert len(email.alternatives) > 0
        html_content = email.alternatives[0][0]
        assert 'activate.html' in html_content or 'uid=' in html_content

    @patch('auth_app.api.signals.send_mail')
    def test_activation_email_failure_handling(self, mock_send_mail, user):
        """Test handling of email sending failure."""
        mock_send_mail.side_effect = Exception('SMTP error')
        token = default_token_generator.make_token(user)

        # Signal should raise exception if email fails
        with pytest.raises(Exception):
            user_registered.send(
                sender=self.__class__,
                user=user,
                token=token
            )


@pytest.mark.django_db
class TestPasswordResetRequestedSignal:
    """Test suite for password_reset_requested signal."""

    @pytest.fixture
    def user(self):
        """Create a user for password reset testing."""
        return User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password='SecurePass123!',
            is_active=True
        )

    def test_password_reset_email_sent(self, user):
        """Test that password reset email is sent when signal is fired."""
        token = default_token_generator.make_token(user)

        password_reset_requested.send(
            sender=self.__class__,
            user=user,
            token=token
        )

        # Verify email was sent
        assert len(mail.outbox) == 1
        assert mail.outbox[0].subject == 'Reset Your Videoflix Password'
        assert user.email in mail.outbox[0].to
        assert 'confirm_password.html' in mail.outbox[0].body

    def test_password_reset_email_contains_correct_info(self, user):
        """Test that password reset email contains correct information."""
        token = default_token_generator.make_token(user)

        password_reset_requested.send(
            sender=self.__class__,
            user=user,
            token=token
        )

        email = mail.outbox[0]
        assert user.email in email.body or str(user.pk) in email.body
        assert str(user.pk) in email.body
        assert token in email.body

    def test_password_reset_email_html_message(self, user):
        """Test that password reset email includes HTML message."""
        token = default_token_generator.make_token(user)

        password_reset_requested.send(
            sender=self.__class__,
            user=user,
            token=token
        )

        email = mail.outbox[0]
        assert email.alternatives is not None
        assert len(email.alternatives) > 0
        html_content = email.alternatives[0][0]
        assert 'confirm_password.html' in html_content or 'uid=' in html_content

    @patch('auth_app.api.signals.send_mail')
    def test_password_reset_email_failure_handling(self, mock_send_mail, user):
        """Test handling of password reset email failure."""
        mock_send_mail.side_effect = Exception('SMTP error')
        token = default_token_generator.make_token(user)

        # Signal should raise exception if email fails
        with pytest.raises(Exception):
            password_reset_requested.send(
                sender=self.__class__,
                user=user,
                token=token
            )

    def test_multiple_signal_receivers(self, user):
        """Test that multiple receivers can handle the same signal."""
        token = default_token_generator.make_token(user)

        # Send both signals
        user_registered.send(
            sender=self.__class__,
            user=user,
            token=token
        )

        password_reset_requested.send(
            sender=self.__class__,
            user=user,
            token=token
        )

        # Both emails should be sent
        assert len(mail.outbox) == 2
