"""
Config package initialization for VIBE E-Commerce.

This module imports the Celery app if available.
"""
try:
    from .celery import app as celery_app
    if celery_app is not None:
        __all__ = ('celery_app',)
    else:
        __all__ = ()
except ImportError:
    __all__ = ()
