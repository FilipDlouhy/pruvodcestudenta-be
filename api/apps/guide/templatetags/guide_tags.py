from django import template

from apps.guide.services import dashboard_service

register = template.Library()


@register.simple_tag
def dashboard_counts():
    """Counts of sections, topics and locations for the admin dashboard."""
    return dashboard_service.get_counts()
