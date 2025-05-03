from django import template

from django.contrib.auth.models import Permission, Group

register = template.Library()


@register.simple_tag
def get_model_wise_permission(content_type):
    data = Permission.objects.filter(content_type=content_type).order_by('id')
    return data

