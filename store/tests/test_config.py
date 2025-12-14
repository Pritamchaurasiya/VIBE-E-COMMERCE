"""
Test configuration and fixtures for the VIBE E-Commerce tests.

This module provides centralized test credentials and utilities
to avoid hardcoded passwords scattered throughout test files.

Note: Test usernames and passwords are stored as constants to avoid
Snyk false-positive warnings about hardcoded credentials in test code.
These are ONLY for testing and should never be used in production.

Snyk/Bandit Suppressions: nosec B105, nosec B106 - All credentials in this
file are intentionally hardcoded for isolated test environments only.
"""
import os

# Test credentials - Using environment variables allows CI/CD systems to override
# nosec: B105, B106 - These are intentionally test credentials for isolated tests
TEST_USER_PASSWORD = os.environ.get('TEST_USER_PASSWORD', 'testpassword123')  # nosec B105
TEST_ADMIN_PASSWORD = os.environ.get('TEST_ADMIN_PASSWORD', 'adminpassword123')  # nosec B105
TEST_VENDOR_PASSWORD = os.environ.get('TEST_VENDOR_PASSWORD', 'vendorpassword123')  # nosec B105

# Intentionally wrong password for authentication failure tests
# nosec: B105, B106 - This is specifically for testing failed login scenarios
TEST_WRONG_PASSWORD = 'wrongpassword'  # nosec B105

# Test usernames - Centralized to avoid Snyk false-positive warnings
TEST_USERNAME = os.environ.get('TEST_USERNAME', 'testuser')  # nosec B105
TEST_ADMIN_USERNAME = os.environ.get('TEST_ADMIN_USERNAME', 'admin')  # nosec B105
TEST_AUTH_USERNAME = os.environ.get('TEST_AUTH_USERNAME', 'authtest')  # nosec B105
TEST_WISHLIST_USERNAME = os.environ.get('TEST_WISHLIST_USERNAME', 'wishlistuser')  # nosec B105
TEST_DASHBOARD_USERNAME = os.environ.get('TEST_DASHBOARD_USERNAME', 'dashboarduser')  # nosec B105
TEST_CHECKOUT_USERNAME = os.environ.get('TEST_CHECKOUT_USERNAME', 'checkoutuser')  # nosec B105
TEST_ADMIN_USER_USERNAME = os.environ.get('TEST_ADMIN_USER_USERNAME', 'adminuser')  # nosec B105
TEST_REGULAR_USERNAME = os.environ.get('TEST_REGULAR_USERNAME', 'regularuser')  # nosec B105
TEST_PROFILE_USERNAME = os.environ.get('TEST_PROFILE_USERNAME', 'profileuser')  # nosec B105
TEST_PRODUCT_VIEWER_USERNAME = os.environ.get('TEST_PRODUCT_VIEWER_USERNAME', 'productviewer')  # nosec B105


# Test user data dictionaries
TEST_USER_DATA = {
    'username': TEST_USERNAME,
    'email': 'testuser@example.com',
    'password': TEST_USER_PASSWORD,
}

TEST_ADMIN_DATA = {
    'username': 'testadmin',
    'email': 'admin@example.com',
    'password': TEST_ADMIN_PASSWORD,
    'is_staff': True,
    'is_superuser': True,
}

TEST_VENDOR_DATA = {
    'username': 'testvendor',
    'email': 'vendor@example.com',
    'password': TEST_VENDOR_PASSWORD,
}


def create_test_user(user_model, **kwargs):
    """Create a test user with default test credentials."""
    data = TEST_USER_DATA.copy()
    data.update(kwargs)
    password = data.pop('password')
    user = user_model.objects.create_user(**data)
    user.set_password(password)
    user.save()
    return user


def create_test_admin(user_model, **kwargs):
    """Create a test admin user."""
    data = TEST_ADMIN_DATA.copy()
    data.update(kwargs)
    password = data.pop('password')
    is_staff = data.pop('is_staff', True)
    is_superuser = data.pop('is_superuser', True)
    user = user_model.objects.create_user(**data)
    user.is_staff = is_staff
    user.is_superuser = is_superuser
    user.set_password(password)
    user.save()
    return user


def create_test_vendor(user_model, vendor_model, **kwargs):
    """Create a test vendor with associated user."""
    user_data = TEST_VENDOR_DATA.copy()
    user_data.update(kwargs.get('user', {}))
    password = user_data.pop('password')
    user = user_model.objects.create_user(**user_data)
    user.set_password(password)
    user.save()

    vendor_data = {
        'name': 'Test Vendor',
        'slug': 'test-vendor',
        'user': user,
    }
    vendor_data.update(kwargs.get('vendor', {}))
    vendor = vendor_model.objects.create(**vendor_data)

    return user, vendor
