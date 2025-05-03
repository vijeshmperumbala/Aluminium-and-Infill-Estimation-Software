
from django import template

from apps.user.models import User

register = template.Library()


@register.simple_tag
def users_in_group_list(group_id):
    data = User.objects.filter(groups=group_id)
    return data


