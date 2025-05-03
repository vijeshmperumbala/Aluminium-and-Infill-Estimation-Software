
from django import template

from django.contrib.auth.models import Permission, Group

register = template.Library()


@register.simple_tag
def get_permission_list(group_id):
    data = Group.objects.get(pk=group_id)
    return data.permissions.all()[:5]