
import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from django.test import Client, override_settings

@pytest.mark.django_db
@override_settings(MIDDLEWARE=[
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
])
def test_header_injection_in_export_data():
    client = Client()
    admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'password')
    client.force_login(admin_user)

    # Try to inject a malicious filename
    malicious_type = 'orders"; filename="malicious.exe'
    response = client.get(reverse('admin_export_data'), {'type': malicious_type})

    assert response.status_code == 200

    content_disposition = response.get('Content-Disposition')
    print(f"\nContent-Disposition: {content_disposition}")

    # Verify that the malicious filename is sanitized/removed
    assert 'malicious.exe' not in content_disposition
    # Verify that it falls back to 'orders'
    assert 'orders' in content_disposition
