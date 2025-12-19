"""
Pytest configuration and shared fixtures for auth_app tests.
"""
import pytest
from django.core.management import call_command
from rest_framework.test import APIClient


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """
    Setup test database with migrations.
    This fixture runs once per test session.
    """
    with django_db_blocker.unblock():
        call_command('migrate', '--noinput')


@pytest.fixture
def api_client():
    """
    Provides a DRF API client for testing.
    """
    return APIClient()


@pytest.fixture(autouse=True)
def email_backend_setup(settings):
    """
    Configure email backend for testing.
    This fixture runs automatically for all tests.
    """
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'


@pytest.fixture(autouse=True)
def clear_mail_outbox():
    """
    Clear Django's email outbox before each test.
    """
    from django.core import mail
    mail.outbox = []
    """
    Clear Django's email outbox before each test.
    """
    from django.core import mail
    mail.outbox = []
