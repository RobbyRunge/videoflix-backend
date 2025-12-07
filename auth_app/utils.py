from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


def send_activation_email(user, uidb64, token):
    """
    Send activation email to the user with the activation link.
    """
    activation_link = f"{settings.BACKEND_URL}/api/activate/{uidb64}/{token}/"

    context = {
        'user_name': user.email,
        'activation_link': activation_link,
    }

    html_message = render_to_string(
        'activation_email.html', context)

    send_mail(
        subject='Activate Your Videoflix Account',
        message=f'Please activate your account by clicking the following link: {activation_link}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )
