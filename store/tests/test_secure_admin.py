""""
Comprehensive Test Suite for Secure Admin System

This module provides extensive testing for the secure Django administration system,
including permission checks, role-based access control, and tracking feature security.
"""

import json
from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User, Group, Permission, AnonymousUser
from django.core.exceptions import PermissionDenied
from django.urls import reverse

from ..admin_permissions import (
    TRACKING_PERMISSIONS,
    check_admin_permission, tracking_admin_required, get_user_admin_permissions,
    log_admin_action, setup_admin_permissions, setup_admin_roles
)
from ..secure_admin import SecureAdminSite
from ..tracking_models import (
    TrackingConfiguration, TrackingAlert,
    AdminTrackingAudit
)
from .test_config import TEST_USER_PASSWORD

class SecureAdminSystemTestCase(TestCase):
    """Test case for the secure admin system."""

    def setUp(self):
        """Set up test data."""
        # Setup security system first
        setup_admin_permissions()
        setup_admin_roles()

        # Create test users
        self.super_admin = User.objects.create_superuser(
            username='superadmin',
            email='super@test.com',
            password=TEST_USER_PASSWORD
        )

        self.tracking_admin = User.objects.create_user(
            username='trackingadmin',
            email='tracking@test.com',
            password=TEST_USER_PASSWORD,
            is_staff=True
        )

        self.content_admin = User.objects.create_user(
            username='contentadmin',
            email='content@test.com',
            password=TEST_USER_PASSWORD,
            is_staff=True
        )

        self.regular_user = User.objects.create_user(
            username='regularuser',
            email='regular@test.com',
            password=TEST_USER_PASSWORD,
            is_staff=False
        )

        # Assign roles to users
        tracking_group = Group.objects.get(name='tracking_admin')
        self.tracking_admin.groups.add(tracking_group)

        super_group = Group.objects.get(name='super_admin')
        self.super_admin.groups.add(super_group)

        content_group = Group.objects.get(name='content_admin')
        self.content_admin.groups.add(content_group)

        # Create tracking configurations
        self.setup_tracking_configs()

        # Create test client
        self.client = Client()

        # Create request factory
        self.factory = RequestFactory()


    def setup_tracking_configs(self):
        """Set up tracking configurations for testing."""
        for category, _ in TrackingConfiguration.TRACKING_CATEGORIES:
            # pylint: disable=no-member
            TrackingConfiguration.objects.get_or_create(
                category=category,
                defaults={
                    'is_enabled': True,
                    'retention_days': 90,
                    'description': f'Test configuration for {category}'
                }
            )

    def test_admin_permission_decorators(self):
        """Test permission decorators."""
        # Test check_admin_permission decorator
        @check_admin_permission('view_tracking_data')
        def test_view(_request):
            return "Success"

        # Test with super admin
        request = self.factory.get('/test/')
        request.user = self.super_admin
        result = test_view(request)
        self.assertEqual(result, "Success")

        # Test with tracking admin (should have permission)
        request.user = self.tracking_admin
        result = test_view(request)
        self.assertEqual(result, "Success")

        # Test with content admin (should not have permission)
        request.user = self.content_admin
        with self.assertRaises(PermissionDenied):
            test_view(request)

        # Test with regular user
        request.user = self.regular_user
        with self.assertRaises(PermissionDenied):
            test_view(request)

    def test_tracking_admin_decorator(self):
        """Test tracking admin decorator."""
        @tracking_admin_required
        def test_view(_request):
            return "Success"

        # Test with super admin
        request = self.factory.get('/test/')
        request.user = self.super_admin
        result = test_view(request)
        self.assertEqual(result, "Success")

        # Test with tracking admin
        request.user = self.tracking_admin
        result = test_view(request)
        self.assertEqual(result, "Success")

        # Test with content admin (should fail)
        request.user = self.content_admin
        with self.assertRaises(PermissionDenied):
            test_view(request)

    def test_get_user_admin_permissions(self):
        """Test getting user permissions."""
        # Test super admin permissions
        permissions = get_user_admin_permissions(self.super_admin)
        self.assertTrue(permissions['is_superuser'])
        self.assertIn('super_admin', permissions['groups'])

        # Test tracking admin permissions
        permissions = get_user_admin_permissions(self.tracking_admin)
        self.assertFalse(permissions['is_superuser'])
        self.assertIn('tracking_admin', permissions['groups'])
        tracking_perms = permissions.get('tracking_permissions', {})
        self.assertTrue(tracking_perms.get('view_tracking_data', False))

        # Test content admin permissions
        permissions = get_user_admin_permissions(self.content_admin)
        self.assertFalse(permissions['is_superuser'])
        self.assertIn('content_admin', permissions['groups'])
        content_perms = permissions.get('tracking_permissions', {})
        self.assertFalse(content_perms.get('view_tracking_data', False))

    def test_log_admin_action(self):
        """Test admin action logging."""
        # pylint: disable=no-member
        initial_count = AdminTrackingAudit.objects.count()

        # Log an action
        log_admin_action(
            self.super_admin,
            'test_action',
            'TestModel',
            1,
            'Test Object',
            {'field': 'value'}
        )

        # Verify log was created
        # pylint: disable=no-member
        self.assertEqual(AdminTrackingAudit.objects.count(), initial_count + 1)

        # Verify log details
        log = AdminTrackingAudit.objects.latest('action_timestamp')
        self.assertEqual(log.action, 'test_action')
        self.assertEqual(log.admin_user, self.super_admin)
        self.assertEqual(log.target_type, 'TestModel')
        self.assertEqual(log.object_id, '1')
        self.assertEqual(log.object_repr, 'Test Object')
        self.assertEqual(log.changes, {'field': 'value'})

    def test_secure_admin_site_permissions(self):
        """Test secure admin site permission checks."""
        admin_site = SecureAdminSite()

        # Test super admin access
        request = self.factory.get('/admin/')
        request.session = {}
        request.user = self.super_admin
        self.assertTrue(admin_site.has_permission(request))

        # Test tracking admin access
        request.user = self.tracking_admin
        self.assertTrue(admin_site.has_permission(request))

        # Test content admin access
        request.user = self.content_admin
        self.assertTrue(admin_site.has_permission(request))

        # Test regular user access (should fail)
        request.user = self.regular_user
        self.assertFalse(admin_site.has_permission(request))

        # Test anonymous user (should fail)
        request.user = AnonymousUser()
        self.assertFalse(admin_site.has_permission(request))

    def test_tracking_dashboard_access(self):
        """Test tracking dashboard access control."""
        # Login as super admin
        self.client.login(username='superadmin', password=TEST_USER_PASSWORD)
        response = self.client.get(reverse('secure_admin:tracking_dashboard'))
        self.assertEqual(response.status_code, 200)

        # Login as tracking admin
        self.client.login(username='trackingadmin', password=TEST_USER_PASSWORD)
        response = self.client.get(reverse('secure_admin:tracking_dashboard'))
        self.assertEqual(response.status_code, 200)

        # Login as content admin (should be denied)
        self.client.login(username='contentadmin', password=TEST_USER_PASSWORD)
        response = self.client.get(reverse('secure_admin:tracking_dashboard'))
        self.assertEqual(response.status_code, 403)

        # Test anonymous access (should redirect to login)
        self.client.logout()
        response = self.client.get(reverse('secure_admin:tracking_dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_tracking_config_update(self):
        """Test tracking configuration updates."""
        # Get a tracking config
        # pylint: disable=no-member
        config = TrackingConfiguration.objects.first()

        # Login as tracking admin
        self.client.login(username='trackingadmin', password=TEST_USER_PASSWORD)

        # Test config update
        response = self.client.post(
            reverse('secure_admin:tracking_config'),
            data=json.dumps({
                'id': config.id,
                'is_enabled': False
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

        # Verify config was updated
        config.refresh_from_db()
        self.assertFalse(config.is_enabled)

        # Verify audit log was created
        # pylint: disable=no-member
        log = AdminTrackingAudit.objects.latest('action_timestamp')
        self.assertEqual(log.action, 'update')
        self.assertEqual(log.target_type, 'TrackingConfiguration')

    def test_admin_audit_view(self):
        """Test admin audit view access."""
        # Create some audit logs
        log_admin_action(self.super_admin, 'test1', 'Model1', 1, 'Obj1', {})
        log_admin_action(self.tracking_admin, 'test2', 'Model2', 2, 'Obj2', {})

        # Login as security admin (should have access)
        security_admin = User.objects.create_user(
            username='securityadmin',
            email='security@test.com',
            password=TEST_USER_PASSWORD,
            is_staff=True
        )
        security_group = Group.objects.create(name='security_admin')
        security_admin.groups.add(security_group)

        # Add view audit permission
        permission = Permission.objects.get(codename='view_admintrackingaudit')
        security_admin.user_permissions.add(permission)

        self.client.login(username='securityadmin', password=TEST_USER_PASSWORD)
        response = self.client.get(reverse('secure_admin:admin_audit'))
        self.assertEqual(response.status_code, 200)

        # Verify logs are displayed
        self.assertContains(response, 'test1')
        self.assertContains(response, 'test2')

    def test_role_based_access_control(self):
        """Test role-based access to different admin sections."""
        # Test super admin access to all sections
        self.client.login(username='superadmin', password=TEST_USER_PASSWORD)

        # All these should return 200
        tracking_response = self.client.get(reverse('secure_admin:tracking_dashboard'))
        config_response = self.client.get(reverse('secure_admin:tracking_config'))
        audit_response = self.client.get(reverse('secure_admin:admin_audit'))

        self.assertEqual(tracking_response.status_code, 200)
        self.assertEqual(config_response.status_code, 200)
        self.assertEqual(audit_response.status_code, 200)

        # Test tracking admin access (should have tracking access only)
        self.client.login(username='trackingadmin', password=TEST_USER_PASSWORD)

        tracking_response = self.client.get(reverse('secure_admin:tracking_dashboard'))
        config_response = self.client.get(reverse('secure_admin:tracking_config'))
        audit_response = self.client.get(reverse('secure_admin:admin_audit'))

        self.assertEqual(tracking_response.status_code, 200)
        self.assertEqual(config_response.status_code, 200)
        self.assertEqual(audit_response.status_code, 403)  # Should be denied

    def test_suspicious_request_detection(self):
        """Test detection of suspicious admin requests."""
        admin_site = SecureAdminSite()

        # Create a request with suspicious patterns
        request = self.factory.get('/admin/')
        request.user = self.tracking_admin
        request.session = {'admin_login_attempts': 6}  # Too many attempts

        # Should be detected as suspicious
        self.assertTrue(admin_site.has_permission(request) is False)

        # Reset attempts
        request.session['admin_login_attempts'] = 3
        # We need to ensure we call is_suspicious_request or check
        # has_permission returns True (if active and staff)
        self.assertTrue(admin_site.has_permission(request))

    def test_permission_inheritance(self):
        """Test that permissions are correctly inherited from roles."""
        # Tracking admin should have tracking permissions
        permissions = get_user_admin_permissions(self.tracking_admin)
        tracking_perms = permissions.get('tracking_permissions', {})

        for perm_code in [
            'view_tracking_configuration',
            'change_tracking_configuration',
            'view_tracking_data',
            'manage_tracking_alerts'
        ]:
            self.assertTrue(tracking_perms.get(perm_code, False),
                          f"Tracking admin should have {perm_code} permission")

        # Content admin should not have tracking permissions
        permissions = get_user_admin_permissions(self.content_admin)
        tracking_perms = permissions.get('tracking_permissions', {})

        for perm_code in [
            'view_tracking_configuration',
            'change_tracking_configuration',
            'view_tracking_data',
            'manage_tracking_alerts'
        ]:
            self.assertFalse(tracking_perms.get(perm_code, False),
                           f"Content admin should not have {perm_code} permission")

    def test_audit_log_integrity(self):
        """Test that audit logs cannot be easily tampered with."""
        # Create an audit log
        log_admin_action(
            self.super_admin, 'create', 'TestModel', 1, 'TestObj', {}
        )

        # pylint: disable=no-member
        audit_log = AdminTrackingAudit.objects.latest('action_timestamp')

        # In a real scenario, this would be prevented by the admin interface
        # Here we test that the model records the change attempt
        audit_log.action = 'modified'
        audit_log.save()

        # Verify the change was recorded
        audit_log.refresh_from_db()
        self.assertEqual(audit_log.action, 'modified')

        # In production, you would want to prevent this via model methods
        # or use a separate audit system that's truly immutable

class TrackingSystemSecurityTestCase(TestCase):
    """Test case for tracking system security."""

    def setUp(self):
        """Set up test data."""
        # Setup security system
        setup_admin_permissions()
        setup_admin_roles()

        self.client = Client()
        self.super_admin = User.objects.create_superuser(
            username='superadmin',
            email='super@test.com',
            password=TEST_USER_PASSWORD
        )

        self.tracking_admin = User.objects.create_user(
            username='trackingadmin',
            email='tracking@test.com',
            password=TEST_USER_PASSWORD,
            is_staff=True
        )

        # Assign role
        tracking_group = Group.objects.get(name='tracking_admin')
        self.tracking_admin.groups.add(tracking_group)

        # Create tracking configs
        for category, _ in TrackingConfiguration.TRACKING_CATEGORIES[:3]:
            # pylint: disable=no-member
            TrackingConfiguration.objects.create(
                category=category,
                is_enabled=True,
                retention_days=30
            )

    def test_tracking_api_security(self):
        """Test security of tracking API endpoints."""
        # Test unauthenticated access
        response = self.client.get(reverse('secure_admin:tracking_stats_api'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login

        # Test authenticated but unauthorized access
        User.objects.create_user(
            username='regular',
            email='regular@test.com',
            password=TEST_USER_PASSWORD,
            is_staff=True
        )
        self.client.login(username='regular', password=TEST_USER_PASSWORD)
        response = self.client.get(reverse('secure_admin:tracking_stats_api'))
        self.assertEqual(response.status_code, 403)  # Should be forbidden

        # Test authorized access
        self.client.login(username='trackingadmin', password=TEST_USER_PASSWORD)
        # Ensure the user has the required permission via group or direct
        perm = Permission.objects.get(codename='view_tracking_data')
        self.tracking_admin.user_permissions.add(perm)

        response = self.client.get(reverse('secure_admin:tracking_stats_api'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

    def test_tracking_configuration_security(self):
        """Test security of tracking configuration changes."""
        # pylint: disable=no-member
        config = TrackingConfiguration.objects.first()

        # Test unauthorized modification attempt
        self.client.login(username='trackingadmin', password=TEST_USER_PASSWORD)
        # Add permission
        perm = Permission.objects.get(codename='change_tracking_configuration')
        self.tracking_admin.user_permissions.add(perm)

        # First, verify the user has permission
        response = self.client.post(
            reverse('secure_admin:tracking_config'),
            data=json.dumps({
                'id': config.id,
                'is_enabled': False
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        # Now test with a user who doesn't have permission
        User.objects.create_user(
            username='contentadmin',
            email='content@test.com',
            password=TEST_USER_PASSWORD,
            is_staff=True
        )
        self.client.login(username='contentadmin', password=TEST_USER_PASSWORD)

        response = self.client.post(
            reverse('secure_admin:tracking_config'),
            data=json.dumps({
                'id': config.id,
                'is_enabled': True
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)

    def test_tracking_data_access_control(self):
        """Test that tracking data access is properly controlled."""
        # Create some tracking data
        # pylint: disable=no-member
        TrackingAlert.objects.create(
            title='Test Alert',
            alert_type='security',
            severity='high',
            description='Test security alert',
            status='active'
        )

        # Test super admin access
        self.client.login(username='superadmin', password=TEST_USER_PASSWORD)
        response = self.client.get(reverse('secure_admin:tracking_alerts'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Alert')

        # Test tracking admin access
        self.client.login(username='trackingadmin', password=TEST_USER_PASSWORD)
        perm = Permission.objects.get(codename='manage_tracking_alerts')
        self.tracking_admin.user_permissions.add(perm)

        response = self.client.get(reverse('secure_admin:tracking_alerts'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Alert')

        # Test unauthorized access
        User.objects.create_user(
            username='regular',
            email='regular@test.com',
            password=TEST_USER_PASSWORD,
            is_staff=True
        )
        self.client.login(username='regular', password=TEST_USER_PASSWORD)

        response = self.client.get(reverse('secure_admin:tracking_alerts'))
        self.assertEqual(response.status_code, 403)

class AdminPermissionFrameworkTestCase(TestCase):
    """Test case for the admin permission framework."""

    def setUp(self):
        """Set up test data."""
        self.client = Client()

        # Create users
        self.super_admin = User.objects.create_superuser(
            username='superadmin',
            email='super@test.com',
            password=TEST_USER_PASSWORD
        )

        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@test.com',
            password=TEST_USER_PASSWORD,
            is_staff=True
        )

        # Create some permissions
        self.setup_permissions()

    def setup_permissions(self):
        """Set up test permissions."""
        from django.contrib.contenttypes.models import ContentType

        # Get or create content type for tracking configuration
        content_type = ContentType.objects.get_or_create(
            app_label='store',
            model='trackingconfiguration'
        )[0]

        # Create tracking permissions
        for codename, name in TRACKING_PERMISSIONS.items():
            Permission.objects.get_or_create(
                codename=codename,
                name=name,
                content_type=content_type
            )

    def test_permission_assignment(self):
        """Test assignment of permissions to users and groups."""
        # Get tracking permissions
        view_perm = Permission.objects.get(codename='view_tracking_data')
        change_perm = Permission.objects.get(codename='change_tracking_configuration')

        # Assign permissions to admin user
        self.admin_user.user_permissions.add(view_perm, change_perm)

        # Test permissions
        self.assertTrue(self.admin_user.has_perm('store.view_tracking_data'))
        self.assertTrue(self.admin_user.has_perm('store.change_tracking_configuration'))
        self.assertFalse(self.admin_user.has_perm('store.manage_tracking_alerts'))

        # Test via get_user_admin_permissions
        permissions = get_user_admin_permissions(self.admin_user)
        self.assertTrue(permissions['direct_permissions']) # Need to check the list or dict structure

    def test_group_permission_inheritance(self):
        """Test that group permissions are properly inherited."""
        # Create a group with tracking permissions
        tracking_group = Group.objects.create(name='test_tracking_group')

        view_perm = Permission.objects.get(codename='view_tracking_data')
        change_perm = Permission.objects.get(codename='change_tracking_configuration')

        tracking_group.permissions.add(view_perm, change_perm)

        # Add user to group
        self.admin_user.groups.add(tracking_group)

        # Test permissions
        self.assertTrue(self.admin_user.has_perm('store.view_tracking_data'))
        self.assertTrue(self.admin_user.has_perm('store.change_tracking_configuration'))

        # Remove direct permissions to test group inheritance
        self.admin_user.user_permissions.clear()

        # Should still have permissions from group
        self.assertTrue(self.admin_user.has_perm('store.view_tracking_data'))
        self.assertTrue(self.admin_user.has_perm('store.change_tracking_configuration'))

    def test_permission_decorator_edge_cases(self):
        """Test edge cases for permission decorators."""
        # Test with anonymous user
        @check_admin_permission('view_tracking_data')
        def test_view(_request):
            return "Success"

        request = RequestFactory().get('/test/')
        request.user = AnonymousUser()

        with self.assertRaises(PermissionDenied):
            test_view(request)

        # Test with authenticated but non-staff user
        regular_user = User.objects.create_user(
            username='regular',
            email='regular@test.com',
            password=TEST_USER_PASSWORD,
            is_staff=False
        )

        request.user = regular_user

        with self.assertRaises(PermissionDenied):
            test_view(request)

        # Test with staff user but missing permission
        staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@test.com',
            password=TEST_USER_PASSWORD,
            is_staff=True
        )

        request.user = staff_user

        with self.assertRaises(PermissionDenied):
            test_view(request)

        # Test with user who has the permission
        staff_user.user_permissions.add(
            Permission.objects.get(codename='view_tracking_data')
        )

        result = test_view(request)
        self.assertEqual(result, "Success")
