"""
ikrweb/templatetags/custom_filters.py

Custom Django template filters for the IKR portfolio.
"""

from django import template

register = template.Library()


@register.filter(name='split')
def split(value, delimiter=','):
    """
    Splits a string by a delimiter and returns a list of stripped tokens.
    Usage: {{ project.technologies|split:"," }}
    """
    if not value:
        return []
    return [item.strip() for item in value.split(delimiter) if item.strip()]


@register.filter(name='percentage')
def percentage(value, total):
    """
    Returns value as a percentage of total, rounded to 0 decimal places.
    Usage: {{ count|percentage:total }}
    """
    try:
        return int((float(value) / float(total)) * 100)
    except (ValueError, ZeroDivisionError):
        return 0