"""
Admin Interface for the Tracking System

This module provides Django admin interface for managing the tracking system.
"""
from datetime import timedelta

from django.contrib import admin
from django.db.models import Count, Avg
from django.utils import timezone

from .models import (
    TrackingConfiguration, SystemFileTracker, UserActionTracker,
    PerformanceMetric, TrackingAlert, AdminTrackingAudit
)
# The following models are missing in store/models.py, temporarily commented out
# SystemAccessTracker, DataModificationTracker, SessionTracker,
# TrackingDataRetention, TrackingExport


@admin.register(TrackingConfiguration)
class TrackingConfigurationAdmin(admin.ModelAdmin):
    """
    Admin interface for managing tracking configurations.
    """
    list_display = ['category', 'is_enabled', 'retention_days', 'created_at', 'updated_at']
    list_filter = ['is_enabled', 'category']
    search_fields = ['category', 'description']

    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'is_enabled', 'description')
        }),
        ('Configuration', {
            'fields': ('config_data', 'retention_days'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of tracking configurations."""
        return False


@admin.register(SystemFileTracker)
class SystemFileTrackerAdmin(admin.ModelAdmin):
    """
    Admin interface for viewing file operation logs.
    """
    list_display = ['operation', 'file_name', 'user', 'ip_address', 'operation_timestamp']
    list_filter = ['operation', 'is_sensitive', 'operation_timestamp']
    search_fields = ['file_name', 'file_path', 'user__username', 'ip_address']
    date_hierarchy = 'operation_timestamp'

    def get_readonly_fields(self, request, obj=None):
        """Return all field names as readonly."""
        # pylint: disable=protected-access
        return [field.name for field in self.model._meta.fields]

    def has_add_permission(self, request):
        """Prevent manual addition of file tracking records."""
        return False

    def has_change_permission(self, request, obj=None):
        """Prevent manual modification of file tracking records."""
        return False


@admin.register(UserActionTracker)
class UserActionTrackerAdmin(admin.ModelAdmin):
    """
    Admin interface for viewing user action logs.
    """
    list_display = ['action_type', 'user', 'page_title', 'action_timestamp']
    list_filter = ['action_type', 'is_sensitive', 'action_timestamp']
    search_fields = ['user__username', 'page_url', 'page_title', 'element_id']
    date_hierarchy = 'action_timestamp'

    def get_readonly_fields(self, request, obj=None):
        """Return all field names as readonly."""
        # pylint: disable=protected-access
        return [field.name for field in self.model._meta.fields]

    def has_add_permission(self, request):
        """Prevent manual addition of user action records."""
        return False

    def has_change_permission(self, request, obj=None):
        """Prevent manual modification of user action records."""
        return False


# @admin.register(SystemAccessTracker)
# class SystemAccessTrackerAdmin(admin.ModelAdmin):
#     """
#     Admin interface for viewing system access logs.
#     """
#     list_display = [
#         'access_type', 'user', 'ip_address', 'risk_level',
#         'is_successful', 'access_timestamp'
#     ]
#     list_filter = ['access_type', 'risk_level', 'is_successful', 'access_timestamp']
#     search_fields = ['user__username', 'ip_address', 'resource_accessed']
#     date_hierarchy = 'access_timestamp'
#
#     def get_readonly_fields(self, request, obj=None):
#         """Return all field names as readonly."""
#         # pylint: disable=protected-access
#         return [field.name for field in self.model._meta.fields]
#
#     def has_add_permission(self, request):
#         """Prevent manual addition of access tracking records."""
#         return False
#
#     def has_change_permission(self, request, obj=None):
#         """Prevent manual modification of access tracking records."""
#         return False


# @admin.register(DataModificationTracker)
# class DataModificationTrackerAdmin(admin.ModelAdmin):
#     """
#     Admin interface for viewing data modification logs.
#     """
#     list_display = ['operation_type', 'model_name', 'object_repr', 'user', 'timestamp']
#     list_filter = ['operation_type', 'is_sensitive', 'timestamp']
#     search_fields = ['model_name', 'object_repr', 'user__username']
#     date_hierarchy = 'timestamp'
#
#     def get_readonly_fields(self, request, obj=None):
#         """Return all field names as readonly."""
#         # pylint: disable=protected-access
#         return [field.name for field in self.model._meta.fields]
#
#     def has_add_permission(self, request):
#         """Prevent manual addition of data modification records."""
#         return False
#
#     def has_change_permission(self, request, obj=None):
#         """Prevent manual modification of data modification records."""
#         return False


# @admin.register(SessionTracker)
# class SessionTrackerAdmin(admin.ModelAdmin):
#     """
#     Admin interface for viewing session logs.
#     """
#     list_display = ['user', 'session_id', 'ip_address', 'login_timestamp', 'is_active']
#     list_filter = ['status', 'login_method', 'is_active', 'login_timestamp']
#     search_fields = ['user__username', 'session_id', 'ip_address']
#     date_hierarchy = 'login_timestamp'
#
#     def get_readonly_fields(self, request, obj=None):
#         """Return all field names as readonly."""
#         # pylint: disable=protected-access
#         return [field.name for field in self.model._meta.fields]
#
#     def has_add_permission(self, request):
#         """Prevent manual addition of session records."""
#         return False
#
#     def has_change_permission(self, request, obj=None):
#         """Prevent manual modification of session records."""
#         return False


@admin.register(PerformanceMetric)
class PerformanceMetricAdmin(admin.ModelAdmin):
    """
    Admin interface for viewing performance metrics.
    """
    list_display = ['metric_type', 'metric_value', 'metric_unit', 'timestamp']
    list_filter = ['metric_type', 'timestamp']
    # search_fields = ['endpoint'] # endpoint field missing in model
    date_hierarchy = 'timestamp'

    def get_readonly_fields(self, request, obj=None):
        """Return all field names as readonly."""
        # pylint: disable=protected-access
        return [field.name for field in self.model._meta.fields]

    def has_add_permission(self, request):
        """Prevent manual addition of performance metrics."""
        return False

    def has_change_permission(self, request, obj=None):
        """Prevent manual modification of performance metrics."""
        return False


@admin.register(TrackingAlert)
class TrackingAlertAdmin(admin.ModelAdmin):
    """
    Admin interface for managing tracking alerts.
    """
    list_display = ['title', 'alert_type', 'severity', 'status', 'created_at']
    list_filter = ['alert_type', 'severity', 'status', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('Alert Information', {
            'fields': ('alert_type', 'title', 'description', 'severity', 'status')
        }),
        ('Trigger Information', {
            # 'fields': ('triggered_by',), # Missing field
            'fields': (),
            'classes': ('collapse',)
        }),
        ('Resolution', {
            'fields': ('acknowledged_by', 'acknowledged_at', 'resolved_by', 'resolved_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_acknowledged', 'mark_as_resolved']

    def mark_as_acknowledged(self, request, queryset):
        """Mark selected alerts as acknowledged."""
        updated = queryset.update(
            status='acknowledged',
            acknowledged_by=request.user,
            acknowledged_at=timezone.now()
        )
        self.message_user(request, f'{updated} alerts marked as acknowledged.')
    mark_as_acknowledged.short_description = 'Mark selected alerts as acknowledged'

    def mark_as_resolved(self, request, queryset):
        """Mark selected alerts as resolved."""
        updated = queryset.update(
            status='resolved',
            resolved_by=request.user,
            resolved_at=timezone.now()
        )
        self.message_user(request, f'{updated} alerts marked as resolved.')
    mark_as_resolved.short_description = 'Mark selected alerts as resolved'


# @admin.register(TrackingDataRetention)
# class TrackingDataRetentionAdmin(admin.ModelAdmin):
#     """
#     Admin interface for managing data retention policies.
#     """
#     list_display = [
#         'data_type', 'retention_period', 'retention_unit',
#         'auto_cleanup_enabled', 'is_active'
#     ]
#     list_filter = ['retention_unit', 'auto_cleanup_enabled', 'is_active']
#     search_fields = ['data_type']
#     readonly_fields = ['last_cleanup', 'next_cleanup', 'created_at', 'updated_at']


# @admin.register(TrackingExport)
# class TrackingExportAdmin(admin.ModelAdmin):
#     """
#     Admin interface for managing data exports.
#     """
#     list_display = [
#         'export_name', 'data_type', 'format', 'status',
#         'generated_by', 'created_at'
#     ]
#     list_filter = ['data_type', 'format', 'status', 'created_at']
#     search_fields = ['export_name', 'generated_by__username']
#     readonly_fields = ['created_at', 'completed_at', 'file_size', 'record_count']
#
#     def has_change_permission(self, request, obj=None):
#         """Allow changing export status."""
#         return True


@admin.register(AdminTrackingAudit)
class AdminTrackingAuditAdmin(admin.ModelAdmin):
    """
    Admin interface for viewing admin audit logs.
    """
    list_display = ['action', 'admin_user', 'target_type', 'is_successful', 'action_timestamp']
    list_filter = ['action', 'is_successful', 'action_timestamp']
    search_fields = ['admin_user__username', 'target_type']
    date_hierarchy = 'action_timestamp'

    def get_readonly_fields(self, request, obj=None):
        """Return all field names as readonly."""
        # pylint: disable=protected-access
        return [field.name for field in self.model._meta.fields]

    def has_add_permission(self, request):
        """Prevent manual addition of audit records."""
        return False

    def has_change_permission(self, request, obj=None):
        """Prevent manual modification of audit records."""
        return False


class TrackingDashboardAdmin(admin.AdminSite):
    """
    Custom admin site for tracking dashboard.
    """
    index_template = 'admin/tracking_dashboard.html'

    def index(self, request, extra_context=None):
        """
        Custom dashboard index with tracking-specific metrics.
        """
        # Get current tracking status
        # pylint: disable=no-member
        tracking_configs = TrackingConfiguration.objects.all()

        # Get recent alerts
        recent_alerts = TrackingAlert.objects.filter(
            status='active'
        ).order_by('-created_at')[:10]

        # Get performance metrics for last 24 hours
        last_24h = timezone.now() - timedelta(hours=24)
        recent_metrics = PerformanceMetric.objects.filter(
            timestamp__gte=last_24h
        ).values('metric_type').annotate(
            count=Count('id'),
            avg_value=Avg('metric_value')
        )

        # Get security events for last 24 hours
        # SystemAccessTracker is missing, commented out
        # security_events = SystemAccessTracker.objects.filter(
        #     access_timestamp__gte=last_24h,
        #     risk_level__in=['high', 'critical']
        # ).count()
        security_events = 0

        # Get active sessions count
        # SessionTracker is missing, commented out
        # active_sessions = SessionTracker.objects.filter(is_active=True).count()
        active_sessions = 0

        context = {
            'tracking_configs': tracking_configs,
            'recent_alerts': recent_alerts,
            'recent_metrics': recent_metrics,
            'security_events_count': security_events,
            'active_sessions_count': active_sessions,
            'total_configured_categories': len(tracking_configs),
            'enabled_categories': len([c for c in tracking_configs if c.is_enabled]),
        }

        return super().index(request, extra_context=context)


# Create a custom admin site instance
tracking_admin_site = TrackingDashboardAdmin(name='tracking_admin')

# Register all models with the custom admin site
tracking_admin_site.register(TrackingConfiguration, TrackingConfigurationAdmin)
tracking_admin_site.register(SystemFileTracker, SystemFileTrackerAdmin)
tracking_admin_site.register(UserActionTracker, UserActionTrackerAdmin)
# tracking_admin_site.register(SystemAccessTracker, SystemAccessTrackerAdmin)
# tracking_admin_site.register(DataModificationTracker, DataModificationTrackerAdmin)
# tracking_admin_site.register(SessionTracker, SessionTrackerAdmin)
tracking_admin_site.register(PerformanceMetric, PerformanceMetricAdmin)
tracking_admin_site.register(TrackingAlert, TrackingAlertAdmin)
# tracking_admin_site.register(TrackingDataRetention, TrackingDataRetentionAdmin)
# tracking_admin_site.register(TrackingExport, TrackingExportAdmin)
tracking_admin_site.register(AdminTrackingAudit, AdminTrackingAuditAdmin)
