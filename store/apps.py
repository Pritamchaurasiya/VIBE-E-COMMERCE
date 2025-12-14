"""
Store app configuration.
"""
from django.apps import AppConfig


class StoreConfig(AppConfig):
    """Configuration for the store app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'
    verbose_name = 'VIBE E-Commerce Store'

    def ready(self):
        """Import signals when the app is ready."""
        # pylint: disable=import-outside-toplevel,unused-import
        from . import signals  # noqa: F401
