"""
Celery configuration for VIBE E-Commerce.

This module configures Celery for background task processing.
"""
import os

try:
    from celery import Celery

    # Set the default Django settings module for Celery
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

    app = Celery('vibe_ecommerce')

    # Use Django settings for Celery configuration
    app.config_from_object('django.conf:settings', namespace='CELERY')

    # Auto-discover tasks in all registered Django apps
    app.autodiscover_tasks()

    @app.task(bind=True, ignore_result=True)
    def debug_task(self):
        """A debug task to verify Celery is working."""
        print(f'Request: {self.request!r}')

    # Celery beat schedule for periodic tasks
    app.conf.beat_schedule = {
        'check-low-stock-hourly': {
            'task': 'store.tasks.check_low_stock_alerts',
            'schedule': 3600.0,
        },
        'clean-expired-sessions-daily': {
            'task': 'store.tasks.clean_expired_sessions',
            'schedule': 86400.0,
        },
        'update-vendor-analytics-daily': {
            'task': 'store.tasks.update_vendor_analytics',
            'schedule': 86400.0,
        },
    }

except ImportError:
    # Celery not installed
    app = None  # pylint: disable=invalid-name
