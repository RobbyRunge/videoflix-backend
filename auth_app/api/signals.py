from django.dispatch import receiver, Signal
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import os


# Custom signal for sending activation email with token
user_registered = Signal()

# Custom signal for sending password reset email with token
password_reset_requested = Signal()


@receiver(user_registered)
def send_activation_email(sender, user, token, **kwargs):
    """
    Send activation email to user after registration.
    Receives token from the view to ensure consistency.
    """
    # Build activation link
    uid = user.pk
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5500')
    activation_link = (
        f"{frontend_url}/pages/auth/activate.html"
        f"?uid={uid}&token={token}"
    )

    # Render email template
    html_message = render_to_string('activation_email.html', {
        'user_name': user.email,
        'activation_link': activation_link,
    })

    # Send email
    send_mail(
        subject='Activate Your Videoflix Account',
        message=f'Please activate your account by visiting: {activation_link}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )


@receiver(password_reset_requested)
def send_password_reset_email(sender, user, token, **kwargs):
    """
    Send password reset email to user.
    Receives token from the view to ensure consistency.
    """
    # Build reset link
    uid = user.pk
    frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5500')
    reset_link = (
        f"{frontend_url}/pages/auth/reset_password.html"
        f"?uid={uid}&token={token}"
    )

    # Render email template
    html_message = render_to_string('password_reset_mail.html', {
        'user': user,
        'reset_link': reset_link,
    })

    # Send email
    send_mail(
        subject='Reset Your Videoflix Password',
        message=f'Please reset your password by visiting: {reset_link}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )
