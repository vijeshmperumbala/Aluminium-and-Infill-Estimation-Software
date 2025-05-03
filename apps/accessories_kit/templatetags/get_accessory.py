from django import template
from apps.accessories_master.models import Accessories
register = template.Library()


@register.simple_tag
def get_accessory(pk):
    items = Accessories.objects.get(pk=pk)
    data = {
        "name": items.accessory_name,
        "brand": items.accessory_brand
    }
    return data

