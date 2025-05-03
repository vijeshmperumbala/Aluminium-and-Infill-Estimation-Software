from django import template
from apps.accessories_master.models import Accessories
# from apps.accessories_kit.models import AccessoriesKitItem
register = template.Library()


@register.simple_tag
def get_brand(pk):
    # answers = AccessoriesKitItem.objects.filter(accessory_kit=pk)
    # return answers if answers else None
    return None