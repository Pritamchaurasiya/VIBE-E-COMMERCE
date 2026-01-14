from django.db import models
from django.contrib.auth.models import User

class SystemAccessTracker(models.Model):
    """
    Model for tracking system access events.
    """
    ACCESS_TYPES = [
        ('login', 'User Login'),
        ('logout', 'User Logout'),
        ('failed_login', 'Failed Login'),
        ('api_access', 'API Access'),
        ('admin_access', 'Admin Access'),
        ('file_access', 'File Access'),
        ('db_access', 'Database Access'),
        ('sql_injection', 'SQL Injection Attempt'),
        ('xss_attempt', 'XSS Attempt'),
    ]

    access_type = models.CharField(max_length=50, choices=ACCESS_TYPES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_id = models.CharField(max_length=100, blank=True)
    resource_accessed = models.CharField(max_length=255, blank=True)
    access_timestamp = models.DateTimeField(auto_now_add=True)
    is_successful = models.BooleanField(default=True)
    risk_level = models.CharField(max_length=20, default='low')
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'System Access'
        verbose_name_plural = 'System Accesses'
        indexes = [
            models.Index(fields=['access_type', 'access_timestamp']),
            models.Index(fields=['user', 'access_timestamp']),
            models.Index(fields=['ip_address', 'access_timestamp']),
        ]

    def __str__(self):
        return f"{self.access_type} - {self.user} ({self.access_timestamp})"


class DataModificationTracker(models.Model):
    """
    Model for tracking data modifications.
    """
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    operation = models.CharField(max_length=20)  # create, update, delete
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    changes = models.JSONField(default=dict, blank=True)

    class Meta:
        verbose_name = 'Data Modification'
        verbose_name_plural = 'Data Modifications'
        indexes = [
            models.Index(fields=['model_name', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.operation} {self.model_name} ({self.timestamp})"


class SessionTracker(models.Model):
    """
    Model for tracking user sessions.
    """
    session_key = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    login_timestamp = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    device_type = models.CharField(max_length=50, blank=True)
    browser = models.CharField(max_length=50, blank=True)
    os = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=100, blank=True)

    class Meta:
        verbose_name = 'Session Tracker'
        verbose_name_plural = 'Session Trackers'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
        ]

    def __str__(self):
        return f"Session {self.session_key} - {self.user}"


class TrackingDataRetention(models.Model):
    """
    Model for configuring data retention policies.
    """
    DATA_TYPES = [
        ('file_operations', 'File Operations'),
        ('user_actions', 'User Actions'),
        ('system_access', 'System Access'),
        ('data_modifications', 'Data Modifications'),
        ('sessions', 'Sessions'),
        ('performance_metrics', 'Performance Metrics'),
    ]

    data_type = models.CharField(max_length=50, choices=DATA_TYPES, unique=True)
    retention_period = models.PositiveIntegerField(default=90, help_text="Retention period value")
    retention_unit = models.CharField(max_length=20, choices=[
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
        ('years', 'Years'),
    ], default='days')
    auto_cleanup_enabled = models.BooleanField(default=True)
    last_cleanup = models.DateTimeField(null=True, blank=True)
    next_cleanup = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Data Retention Policy'
        verbose_name_plural = 'Data Retention Policies'

    def __str__(self):
        return f"{self.get_data_type_display()}: {self.retention_period} {self.retention_unit}"
