from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
import os


@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    """
    Send activation email to user after registration.
    Only triggers when user is newly created and inactive.
    """
    if created and not instance.is_active:
        # Generate activation token and uid
        uid = instance.pk
        token = default_token_generator.make_token(instance)

        # Build activation link
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5500')
        activation_link = (
            f"{frontend_url}/pages/auth/activate.html"
            f"?uid={uid}&token={token}"
        )

        # Render email template
        html_message = render_to_string('activation_email.html', {
            'user_name': instance.email,
            'activation_link': activation_link,
        })

        # Send email
        send_mail(
            subject='Activate Your Videoflix Account',
            message=f'Please activate your account by visiting: {activation_link}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.email],
            html_message=html_message,
            fail_silently=False,
        )
