"""
Custom template filters for the store app.
"""
from django import template

register = template.Library()

@register.filter
def get(dictionary, key):
    """Get value from dictionary by key."""
    if not dictionary:
        return 0
    return dictionary.get(key, 0)

@register.filter
def mul(value, arg):
    """Multiply value by arg."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def div(value, arg):
    """Divide value by arg."""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def to_int(value):
    """Convert to integer."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0
