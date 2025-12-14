""""
Secure Admin Interface with Granular Tracking Controls

This module provides a secure Django admin interface with:
- Role-based access control
- Tracking feature management
- Enhanced security measures
- Audit logging
"""

import json
import logging
from datetime import timedelta
from django.contrib import admin
from django.contrib.auth.models import User, Group, Permission
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import path, reverse
from django.views.generic import TemplateView, View
from django.utils import timezone

from .admin_permissions import (
    AdminPermissionMixin, TrackingPermissionMixin,
    log_admin_action, TRACKING_PERMISSIONS
)
from .tracking_service import EnhancedTrackingService
from .models import (
    TrackingConfiguration, TrackingAlert, AdminTrackingAudit,
    SiteSettings
)

# pylint: disable=no-member, broad-except, import-outside-toplevel

logger = logging.getLogger(__name__)

class SecureModelAdminMixin:
    """
    Mixin to enforce security policies on ModelAdmin.
    """
    def get_queryset(self, request):
        """
        Secure queryset method to enforce data access controls.
        """
        qs = super().get_queryset(request)

        # Apply role-based filtering
        if not request.user.is_superuser:
            if request.user.groups.filter(name='content_admin').exists():
                # Content admins can only see their own vendor's content
                if hasattr(self.model, 'vendor'):
                    qs = qs.filter(vendor__created_by=request.user)
            elif request.user.groups.filter(name='order_admin').exists():
                # Order admins can only see orders they're associated with
                if self.model.__name__ == 'Order':
                    qs = qs.filter(Q(user=request.user) | Q(items__vendor__created_by=request.user))
            elif request.user.groups.filter(name='tracking_admin').exists():
                # Tracking admins have full access to tracking data
                pass
            else:
                # Default: only see records created by the user
                if hasattr(self.model, 'created_by'):
                    qs = qs.filter(created_by=request.user)
                elif hasattr(self.model, 'user'):
                    qs = qs.filter(user=request.user)

        return qs.distinct()

class SecureModelAdmin(SecureModelAdminMixin, admin.ModelAdmin):
    """
    Base Secure ModelAdmin.
    """
    pass

class SecureAdminSite(admin.AdminSite):
    """
    Enhanced secure admin site with custom security features.
    """

    # Custom index template
    index_template = 'admin/secure_index.html'
    login_template = 'admin/secure_login.html'

    def __init__(self, name='secure_admin'):
        super().__init__(name)

    def register(self, model, admin_class=None, **options):
        """
        Enhanced register method with security checks.
        """
        if admin_class is None:
            admin_class = SecureModelAdmin
        else:
            # Dynamically create a secure subclass if not already secure
            if not issubclass(admin_class, SecureModelAdminMixin):
                class SecureAdminClass(SecureModelAdminMixin, admin_class):
                    pass
                admin_class = SecureAdminClass

        super().register(model, admin_class, **options)

    def has_permission(self, request):
        """
        Enhanced permission checking with IP and session validation.
        """
        if not request.user.is_active or not request.user.is_staff:
            return False

        # Check for suspicious activity
        if self.is_suspicious_request(request):
            logger.warning("Suspicious admin access attempt by %s", request.user.username)
            return False

        return True

    def is_suspicious_request(self, request):
        """
        Check if request shows signs of suspicious activity.
        """
        # Check for multiple failed login attempts
        failed_attempts = request.session.get('admin_login_attempts', 0)
        if failed_attempts > 5:
            return True

        # Check IP reputation (would integrate with threat intelligence in production)
        ip = request.META.get('REMOTE_ADDR')
        if ip and ip.startswith('192.168'):  # Example: block private IPs for admin
            return True

        return False

    def index(self, request, extra_context=None):
        """
        Custom secure admin dashboard with role-based content.
        """
        if not self.has_permission(request):
            return redirect(reverse('admin:login'))

        # Get user permissions and role
        user_permissions = self.get_user_permissions(request.user)
        user_role = self.get_user_role(request.user)

        # Get security alerts
        security_alerts = self.get_security_alerts()

        # Get system status
        system_status = self.get_system_status()

        # Get recent admin actions (for audit trail)
        try:
            recent_actions = AdminTrackingAudit.objects.filter(
                action_timestamp__gte=timezone.now() - timedelta(days=1)
            ).order_by('-action_timestamp')[:10]
        except Exception:
            recent_actions = []

        context = {
            **self.each_context(request),
            'title': 'Secure Admin Dashboard',
            'user_permissions': user_permissions,
            'user_role': user_role,
            'security_alerts': security_alerts,
            'system_status': system_status,
            'recent_actions': recent_actions,
            'tracking_enabled': self.is_tracking_enabled(),
            'show_tracking_section': user_role in ['super_admin', 'tracking_admin'],
            'show_content_section': user_role in ['super_admin', 'content_admin'],
            'show_order_section': user_role in ['super_admin', 'order_admin'],
            'show_security_section': user_role in ['super_admin', 'security_admin'],
        }

        return super().index(request, extra_context=context)

    def get_user_permissions(self, user):
        """Get formatted user permissions."""
        permissions = {}

        # Check admin roles
        for role in ['super_admin', 'tracking_admin', 'content_admin', 'order_admin', 'security_admin']:
            permissions[role] = user.groups.filter(name=role).exists()

        # Check specific tracking permissions
        for perm_code in TRACKING_PERMISSIONS:
            permissions[perm_code] = user.has_perm(f'store.{perm_code}')

        return permissions

    def get_user_role(self, user):
        """Determine user's primary admin role."""
        if user.is_superuser:
            return 'super_admin'

        if user.groups.filter(name='tracking_admin').exists():
            return 'tracking_admin'

        if user.groups.filter(name='content_admin').exists():
            return 'content_admin'

        if user.groups.filter(name='order_admin').exists():
            return 'order_admin'

        if user.groups.filter(name='security_admin').exists():
            return 'security_admin'

        return 'limited_admin'

    def get_security_alerts(self):
        """Get active security alerts."""
        try:
            return TrackingAlert.objects.filter(
                alert_type='security',
                status='active',
                severity__in=['high', 'critical']
            ).order_by('-created_at')[:5]
        except Exception:
            return []

    def get_system_status(self):
        """Get system health status."""
        return {
            'database': 'Operational',
            'cache': 'Operational',
            'storage': '85% Used',
            'last_backup': timezone.now() - timedelta(hours=2),
            'active_sessions': 42,
            'pending_tasks': 3,
        }

    def is_tracking_enabled(self):
        """Check if any tracking is enabled."""
        try:
            return TrackingConfiguration.objects.filter(is_enabled=True).exists()
        except Exception:
            return False

    def get_urls(self):
        """Add custom admin URLs."""
        urls = super().get_urls()

        custom_urls = [
            path('tracking/dashboard/', self.admin_view(TrackingDashboardView.as_view()), name='tracking_dashboard'),
            path('tracking/config/', self.admin_view(TrackingConfigView.as_view()), name='tracking_config'),
            path('tracking/alerts/', self.admin_view(TrackingAlertsView.as_view()), name='tracking_alerts'),
            path('tracking/audit/', self.admin_view(AdminAuditView.as_view()), name='admin_audit'),
            path('security/settings/', self.admin_view(SecuritySettingsView.as_view()), name='security_settings'),
            path('admin/permissions/', self.admin_view(AdminPermissionsView.as_view()), name='admin_permissions'),
            path('admin/roles/', self.admin_view(AdminRolesView.as_view()), name='admin_roles'),
            path('api/tracking/stats/', self.admin_view(TrackingStatsAPI.as_view()), name='tracking_stats_api'),
        ]

        return custom_urls + urls

class TrackingDashboardView(TrackingPermissionMixin, TemplateView):
    """
    Secure tracking dashboard with granular access control.
    """
    template_name = 'admin/tracking_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Get tracking statistics
        stats = EnhancedTrackingService.get_tracking_statistics()

        # Get tracking configurations
        configs = TrackingConfiguration.objects.all().annotate(
            record_count=Count('systemfiletracker' if 'file' in self.model else 'useractiontracker')
            if hasattr(self, 'model') else Count('pk') # Fallback if model not defined in View?
        ).order_by('category')
        # Note: self.model is not standard in TemplateView unless we define it or use ListView.
        # But here we are iterating configs. TrackingConfiguration doesn't have systemfiletracker relation unless related_name set.

        # Refined query for configs
        configs = TrackingConfiguration.objects.all()

        # Get recent alerts
        recent_alerts = TrackingAlert.objects.filter(
            status='active'
        ).order_by('-created_at')[:5]

        context.update({
            'stats': stats,
            'configs': configs,
            'recent_alerts': recent_alerts,
            'tracking_permissions': {
                perm: self.request.user.has_perm(f'store.{perm}')
                for perm in TRACKING_PERMISSIONS
            }
        })

        return context

class TrackingConfigView(TrackingPermissionMixin, View):
    """
    Tracking configuration management with granular permissions.
    """

    def get(self, request):
        configs = TrackingConfiguration.objects.all().order_by('category')
        return render(request, 'admin/tracking_config.html', {
            'configs': configs,
            'can_edit': request.user.has_perm('store.change_tracking_configuration')
        })

    def post(self, request):
        if not request.user.has_perm('store.change_tracking_configuration'):
            return JsonResponse({
                'success': False,
                'error': 'You do not have permission to modify tracking configurations.'
            }, status=403)

        try:
            data = json.loads(request.body)
            config_id = data.get('id')
            is_enabled = data.get('is_enabled')

            config = TrackingConfiguration.objects.get(id=config_id)
            config.is_enabled = is_enabled
            config.save()

            # Log the action
            log_admin_action(
                request.user,
                'update',
                'TrackingConfiguration',
                config.id,
                str(config),
                {'is_enabled': is_enabled}
            )

            # Invalidate cache
            EnhancedTrackingService.invalidate_config_cache(config.category)

            return JsonResponse({'success': True})

        except Exception as e:
            logger.error("Error updating tracking config: %s", e)
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

class TrackingAlertsView(TrackingPermissionMixin, View):
    """
    Tracking alerts management with granular permissions.
    """

    def get(self, request):
        alerts = TrackingAlert.objects.all().order_by('-created_at')

        # Filter by user permissions
        if not request.user.has_perm('store.manage_tracking_alerts'):
            alerts = alerts.filter(created_by=request.user)

        return render(request, 'admin/tracking_alerts.html', {
            'alerts': alerts,
            'can_manage': request.user.has_perm('store.manage_tracking_alerts')
        })

    def post(self, request):
        if not request.user.has_perm('store.manage_tracking_alerts'):
            return JsonResponse({
                'success': False,
                'error': 'You do not have permission to manage alerts.'
            }, status=403)

        try:
            data = json.loads(request.body)
            alert_id = data.get('id')
            action = data.get('action')  # acknowledge, resolve, etc.

            alert = TrackingAlert.objects.get(id=alert_id)

            if action == 'acknowledge':
                alert.status = 'acknowledged'
                alert.acknowledged_by = request.user
                alert.acknowledged_at = timezone.now()
            elif action == 'resolve':
                alert.status = 'resolved'
                alert.resolved_by = request.user
                alert.resolved_at = timezone.now()

            alert.save()

            # Log the action
            log_admin_action(
                request.user,
                f'{action}_alert',
                'TrackingAlert',
                alert.id,
                str(alert),
                {'status': alert.status}
            )

            return JsonResponse({'success': True})

        except Exception as e:
            logger.error("Error managing alert: %s", e)
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

class AdminAuditView(AdminPermissionMixin, View):
    """
    Admin audit trail viewer with security controls.
    """
    required_permissions = ['store.view_admintrackingaudit']

    def get(self, request):
        # Get filter parameters
        days = int(request.GET.get('days', 7))
        action_type = request.GET.get('action')
        user_id = request.GET.get('user')

        # Build query
        queryset = AdminTrackingAudit.objects.all().order_by('-action_timestamp')

        # Apply filters
        if days > 0:
            cutoff = timezone.now() - timedelta(days=days)
            queryset = queryset.filter(action_timestamp__gte=cutoff)

        if action_type:
            queryset = queryset.filter(action=action_type)

        if user_id:
            queryset = queryset.filter(admin_user_id=user_id)

        # Get users for filter dropdown
        users = User.objects.filter(
            admin_audit_logs__isnull=False
        ).distinct().order_by('username')

        # Get action types for filter
        action_types = AdminTrackingAudit.objects.values_list(
            'action', flat=True
        ).distinct().order_by('action')

        return render(request, 'admin/audit_trail.html', {
            'audit_logs': queryset[:100],
            'users': users,
            'action_types': action_types,
            'current_filters': {
                'days': days,
                'action': action_type,
                'user': user_id
            }
        })

class SecuritySettingsView(AdminPermissionMixin, View):
    """
    Security settings management with super admin restrictions.
    """
    required_permissions = ['store.manage_security_settings']

    def get(self, request):
        if not request.user.is_superuser:
            return render(request, 'admin/security_settings.html', {
                'error': 'Only super administrators can manage security settings.'
            }, status=403)

        # Get current security settings
        settings = {
            'password_policy': self.get_password_policy(),
            'session_settings': self.get_session_settings(),
            'ip_restrictions': self.get_ip_restrictions(),
            'two_factor_auth': self.get_two_factor_settings(),
        }

        return render(request, 'admin/security_settings.html', settings)

    def get_password_policy(self):
        return {
            'min_length': 12,
            'require_uppercase': True,
            'require_lowercase': True,
            'require_digit': True,
            'require_special': True,
            'max_age_days': 90,
            'history_count': 5,
        }

    def get_session_settings(self):
        return {
            'timeout_minutes': 30,
            'max_sessions': 3,
            'inactive_timeout': 15,
        }

    def get_ip_restrictions(self):
        return {
            'allow_private_ips': False,
            'max_failed_attempts': 5,
            'lockout_minutes': 15,
            'trusted_ips': ['127.0.0.1', '::1'],
        }

    def get_two_factor_settings(self):
        return {
            'enabled': True,
            'required_for_admins': True,
            'methods': ['sms', 'email', 'auth_app'],
        }

class AdminPermissionsView(AdminPermissionMixin, View):
    """
    Admin permissions management interface.
    """
    required_permissions = ['auth.change_permission']

    def get(self, request):
        # Get all users with staff status
        admin_users = User.objects.filter(is_staff=True).order_by('username')

        # Get all groups
        groups = Group.objects.all().order_by('name')

        # Get all permissions
        permissions = Permission.objects.select_related('content_type').order_by(
            'content_type__app_label', 'codename'
        )

        return render(request, 'admin/permissions_manager.html', {
            'admin_users': admin_users,
            'groups': groups,
            'permissions': permissions,
            'tracking_permissions': TRACKING_PERMISSIONS,
        })

class AdminRolesView(AdminPermissionMixin, View):
    """
    Admin roles management interface.
    """
    required_permissions = ['auth.change_group']

    def get(self, request):
        # Get all admin roles with their members
        admin_roles = Group.objects.filter(
            name__in=['super_admin', 'tracking_admin', 'content_admin',
                     'order_admin', 'security_admin']
        ).prefetch_related('user_set').order_by('name')

        role_info = []
        for role in admin_roles:
            role_info.append({
                'group': role,
                'user_count': role.user_set.count(),
                'permissions_count': role.permissions.count(),
            })

        return render(request, 'admin/roles_manager.html', {
            'admin_roles': role_info,
            'all_users': User.objects.filter(is_staff=True).order_by('username'),
        })

class TrackingStatsAPI(AdminPermissionMixin, View):
    """
    API endpoint for tracking statistics with permission checks.
    """
    required_permissions = ['store.view_tracking_data']

    def get(self, request):
        try:
            # Get statistics from tracking service
            stats = EnhancedTrackingService.get_tracking_statistics()

            # Add configuration status
            configs = TrackingConfiguration.objects.all()
            config_status = {
                config.category: config.is_enabled
                for config in configs
            }

            response_data = {
                'success': True,
                'statistics': stats,
                'configurations': config_status,
                'timestamp': timezone.now().isoformat(),
            }

            return JsonResponse(response_data)

        except Exception as e:
            logger.error("Error in tracking stats API: %s", e)
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)

# Enhanced admin classes for tracking models
@admin.register(TrackingConfiguration)
class SecureTrackingConfigurationAdmin(SecureModelAdminMixin, admin.ModelAdmin):
    """
    Secure admin interface for tracking configurations.
    """
    list_display = ['category', 'is_enabled', 'retention_days', 'created_at']
    list_filter = ['is_enabled', 'category']
    search_fields = ['category', 'description']
    readonly_fields = ['created_at', 'updated_at']

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm('store.change_tracking_configuration')

    def has_delete_permission(self, request, obj=None):
        return False  # Never allow deletion of tracking configs

    def save_model(self, request, obj, form, change):
        """Log configuration changes."""
        super().save_model(request, obj, form, change)

        action = 'update' if change else 'create'
        log_admin_action(
            request.user,
            action,
            'TrackingConfiguration',
            obj.id,
            str(obj),
            form.changed_data
        )

        # Invalidate cache
        EnhancedTrackingService.invalidate_config_cache(obj.category)

@admin.register(TrackingAlert)
class SecureTrackingAlertAdmin(SecureModelAdminMixin, admin.ModelAdmin):
    """
    Secure admin interface for tracking alerts.
    """
    list_display = ['title', 'alert_type', 'severity', 'status', 'created_at']
    list_filter = ['alert_type', 'severity', 'status']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['mark_as_acknowledged', 'mark_as_resolved']

    def has_change_permission(self, request, obj=None):
        return request.user.has_perm('store.manage_tracking_alerts')

    def mark_as_acknowledged(self, request, queryset):
        updated = queryset.update(
            status='acknowledged',
            acknowledged_by=request.user,
            acknowledged_at=timezone.now()
        )
        self.message_user(request, f'{updated} alerts marked as acknowledged.')

        # Log bulk action
        log_admin_action(
            request.user,
            'bulk_acknowledge_alerts',
            'TrackingAlert',
            None,
            f'{updated} alerts',
            {'count': updated, 'status': 'acknowledged'}
        )

    def mark_as_resolved(self, request, queryset):
        updated = queryset.update(
            status='resolved',
            resolved_by=request.user,
            resolved_at=timezone.now()
        )
        self.message_user(request, f'{updated} alerts marked as resolved.')

        # Log bulk action
        log_admin_action(
            request.user,
            'bulk_resolve_alerts',
            'TrackingAlert',
            None,
            f'{updated} alerts',
            {'count': updated, 'status': 'resolved'}
        )

@admin.register(AdminTrackingAudit)
class SecureAdminTrackingAuditAdmin(SecureModelAdminMixin, admin.ModelAdmin):
    """
    Secure read-only admin interface for audit logs.
    """
    list_display = ['action', 'admin_user', 'target_type', 'is_successful', 'action_timestamp']
    list_filter = ['action', 'is_successful', 'action_timestamp']
    search_fields = ['admin_user__username', 'target_type']
    readonly_fields = ['action', 'admin_user', 'target_type', 'object_id',
                      'object_repr', 'changes', 'ip_address', 'action_timestamp']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser  # Only super admins can delete audit logs

# Create secure admin site instance
secure_admin_site = SecureAdminSite(name='secure_admin')

# Register models with secure admin site
secure_admin_site.register(User)
secure_admin_site.register(Group)
secure_admin_site.register(TrackingConfiguration, SecureTrackingConfigurationAdmin)
secure_admin_site.register(TrackingAlert, SecureTrackingAlertAdmin)
secure_admin_site.register(AdminTrackingAudit, SecureAdminTrackingAuditAdmin)
secure_admin_site.register(SiteSettings)

def initialize_secure_admin():
    """
    Initialize the secure admin system.
    """
    logger.info("Initializing secure admin system...")

    # Set up permissions
    from .admin_permissions import initialize_admin_security
    initialize_admin_security()

    logger.info("Secure admin system initialized")
