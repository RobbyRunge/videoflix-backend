from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator

from .utils import send_activation_email


@receiver(post_save, sender=User)
def send_activation_email_on_user_creation(sender, instance, created, **kwargs):
    """
    Signal handler that sends activation email when a new user is created.
    Only triggers for newly created inactive users.
    """
    if created and not instance.is_active:
        uidb64 = urlsafe_base64_encode(force_bytes(instance.pk))
        activation_token = default_token_generator.make_token(instance)

        try:
            send_activation_email(instance, uidb64, activation_token)
        except Exception as e:
            print(
                f"Failed to send activation email to {instance.email}: {str(e)}")
