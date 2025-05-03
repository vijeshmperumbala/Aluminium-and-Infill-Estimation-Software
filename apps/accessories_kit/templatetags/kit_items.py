from django import template
from apps.accessories_kit.models import AccessoriesKitItem
from apps.accessories_master.models import Accessories
from apps.product_master.models import Product_Accessories_Kit
register = template.Library()


@register.simple_tag
def kit_items(pk):
    items = AccessoriesKitItem.objects.filter(accessory_kit=pk).order_by('-id')
    return items

