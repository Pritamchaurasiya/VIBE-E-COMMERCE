from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class TrackingConfiguration(models.Model):
    """
    Model for configuring which tracking features are enabled.
    This allows admins to granularly control what gets tracked.
    """
    TRACKING_CATEGORIES = [
        ('file_operations', 'File Operations Tracking'),
        ('user_actions', 'User Action Monitoring'),
        ('system_access', 'System Access Patterns'),
        ('data_modifications', 'Data Modification Tracking'),
        ('login_sessions', 'Login/Session Monitoring'),
        ('performance_metrics', 'Performance Metrics'),
        ('security_events', 'Security Events'),
        ('api_calls', 'API Call Tracking'),
        ('database_queries', 'Database Query Tracking'),
        ('error_tracking', 'Error Tracking'),
    ]

    category = models.CharField(max_length=30, choices=TRACKING_CATEGORIES, unique=True)
    is_enabled = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    config_data = models.JSONField(default=dict, blank=True)
    retention_days = models.PositiveIntegerField(default=90)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tracking Configuration'
        verbose_name_plural = 'Tracking Configurations'

    def __str__(self):
        return f"{self.get_category_display()}: {'Enabled' if self.is_enabled else 'Disabled'}"


class TrackingAlert(models.Model):
    """
    Model for storing system and security alerts.
    """
    ALERT_TYPES = [
        ('security', 'Security Alert'),
        ('performance', 'Performance Alert'),
        ('system', 'System Alert'),
        ('compliance', 'Compliance Alert'),
    ]

    SEVERITY_LEVELS = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('high', 'High Priority'),
        ('critical', 'Critical'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
        ('ignored', 'Ignored'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS, default='info')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    # Metadata
    source = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    triggered_by = models.JSONField(default=dict, blank=True)

    # Resolution tracking
    acknowledged_by = models.ForeignKey(
        User, related_name='acknowledged_alerts',
        on_delete=models.SET_NULL, null=True, blank=True
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        User, related_name='resolved_alerts',
        on_delete=models.SET_NULL, null=True, blank=True
    )
    resolved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Tracking Alert'
        verbose_name_plural = 'Tracking Alerts'
        indexes = [
            models.Index(fields=['status', 'severity']),
            models.Index(fields=['alert_type', 'created_at']),
        ]

    def __str__(self):
        return f"[{self.get_severity_display()}] {self.title}"


class AdminTrackingAudit(models.Model):
    """
    Audit log for sensitive admin actions.
    """
    action = models.CharField(max_length=50)
    admin_user = models.ForeignKey(
        User, related_name='admin_audit_logs',
        on_delete=models.SET_NULL, null=True, blank=True
    )
    target_type = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100, null=True, blank=True)
    object_repr = models.CharField(max_length=255, blank=True)

    changes = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    is_successful = models.BooleanField(default=True)
    error_message = models.TextField(blank=True)

    action_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Admin Audit Log'
        verbose_name_plural = 'Admin Audit Logs'
        indexes = [
            models.Index(fields=['action', 'action_timestamp']),
            models.Index(fields=['admin_user', 'action_timestamp']),
            models.Index(fields=['target_type']),
        ]

    def __str__(self):
        return f"{self.admin_user} - {self.action} ({self.action_timestamp})"


class SystemFileTracker(models.Model):
    """
    Model for tracking file operations across the system.
    """
    FILE_OPERATIONS = [
        ('create', 'File Created'),
        ('read', 'File Read'),
        ('update', 'File Updated'),
        ('delete', 'File Deleted'),
        ('upload', 'File Uploaded'),
        ('download', 'File Downloaded'),
        ('move', 'File Moved'),
        ('copy', 'File Copied'),
    ]

    operation = models.CharField(max_length=10, choices=FILE_OPERATIONS)
    file_path = models.CharField(max_length=500)
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField(null=True, blank=True)
    file_type = models.CharField(max_length=50, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    request_path = models.CharField(max_length=255, blank=True)
    operation_timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)
    is_sensitive = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'File Operation'
        verbose_name_plural = 'File Operations'
        indexes = [
            models.Index(fields=['operation', 'operation_timestamp']),
            models.Index(fields=['user', 'operation_timestamp']),
            models.Index(fields=['file_path']),
            models.Index(fields=['ip_address', 'operation_timestamp']),
        ]

    def __str__(self):
        return f"{self.operation} - {self.file_name}"


class PerformanceMetric(models.Model):
    """
    Model for tracking system performance metrics.
    """
    metric_type = models.CharField(max_length=50)
    metric_value = models.FloatField()
    metric_unit = models.CharField(max_length=20, default='count')
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Performance Metric'
        verbose_name_plural = 'Performance Metrics'
        indexes = [
            models.Index(fields=['metric_type', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.metric_type}: {self.metric_value} {self.metric_unit}"


class UserActionTracker(models.Model):
    """
    Model for tracking detailed user actions and behaviors.
    """
    ACTION_TYPES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('page_view', 'Page View'),
        ('button_click', 'Button Click'),
        ('form_submit', 'Form Submit'),
        ('search', 'Search Query'),
        ('filter_apply', 'Filter Applied'),
        ('sort_apply', 'Sort Applied'),
        ('download', 'Download'),
        ('upload', 'Upload'),
        ('purchase', 'Purchase'),
        ('cart_add', 'Add to Cart'),
        ('cart_remove', 'Remove from Cart'),
        ('wishlist_add', 'Add to Wishlist'),
        ('wishlist_remove', 'Remove from Wishlist'),
        ('review_submit', 'Review Submitted'),
        ('profile_update', 'Profile Updated'),
        ('password_change', 'Password Changed'),
        ('email_change', 'Email Changed'),
        ('custom_action', 'Custom Action'),
    ]

    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_id = models.CharField(max_length=100, default='')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    page_url = models.URLField(blank=True, default='')
    page_title = models.CharField(max_length=255, blank=True)
    element_id = models.CharField(max_length=100, blank=True)
    element_class = models.CharField(max_length=100, blank=True)
    action_timestamp = models.DateTimeField(auto_now_add=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True)
    scroll_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    mouse_x = models.PositiveIntegerField(null=True, blank=True)
    mouse_y = models.PositiveIntegerField(null=True, blank=True)
    exit_intent_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="AI-estimated intent to leave the website based on mouse movements")
    heat_map_data = models.JSONField(default=dict, blank=True)
    performance_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="AI-estimated page performance score based on user actions")
    heat_map_timestamp = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'User Action'
        verbose_name_plural = 'User Actions'
        indexes = [
            models.Index(fields=['action_type', 'action_timestamp']),
            models.Index(fields=['user', 'action_timestamp']),
            models.Index(fields=['session_id', 'action_timestamp']),
            models.Index(fields=['page_url', 'action_timestamp']),
        ]

    def __str__(self):
        return f"{self.action_type} - {self.user.username if self.user else 'Anonymous'} ({self.action_timestamp})"


class SystemAccessTracker(models.Model):
    """
    Model for tracking system access attempts and security events.
    """
    access_type = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    resource_accessed = models.CharField(max_length=255)
    is_successful = models.BooleanField(default=True)
    risk_level = models.CharField(max_length=20, default='low')
    metadata = models.JSONField(default=dict, blank=True)
    access_timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'System Access'
        verbose_name_plural = 'System Accesses'
        indexes = [
            models.Index(fields=['access_timestamp']),
            models.Index(fields=['risk_level']),
        ]

    def __str__(self):
        return f"{self.access_type} - {self.user} ({self.risk_level})"


class DataModificationTracker(models.Model):
    """
    Model for tracking data modifications (CRUD operations) for audit.
    """
    operation_type = models.CharField(max_length=20)
    model_name = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    record_id = models.CharField(max_length=100, blank=True)
    changes = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Data Modification'
        verbose_name_plural = 'Data Modifications'
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['model_name']),
        ]

    def __str__(self):
        return f"{self.operation_type} {self.model_name} by {self.user}"


class SessionTracker(models.Model):
    """
    Model for tracking user sessions.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_id = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)
    login_timestamp = models.DateTimeField(auto_now_add=True)
    logout_timestamp = models.DateTimeField(null=True, blank=True)
    device_type = models.CharField(max_length=50, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Session'
        verbose_name_plural = 'Sessions'
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['login_timestamp']),
        ]

    def __str__(self):
        return f"Session {self.session_id} - {self.user}"


class TrackingDataRetention(models.Model):
    """
    Model for configuring data retention policies for tracking data.
    """
    data_type = models.CharField(max_length=50, choices=[
        ('file_operations', 'File Operations'),
        ('user_actions', 'User Actions'),
        ('system_access', 'System Access'),
        ('data_modifications', 'Data Modifications'),
        ('sessions', 'Sessions'),
        ('performance_metrics', 'Performance Metrics'),
    ])
    retention_period = models.PositiveIntegerField(help_text="Number of units to retain data")
    retention_unit = models.CharField(max_length=10, choices=[
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
        ('years', 'Years'),
    ])
    auto_cleanup_enabled = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    last_cleanup = models.DateTimeField(null=True, blank=True)
    next_cleanup = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Data Retention Policy'
        verbose_name_plural = 'Data Retention Policies'

    def __str__(self):
        return f"Retention Policy for {self.get_data_type_display()}"
