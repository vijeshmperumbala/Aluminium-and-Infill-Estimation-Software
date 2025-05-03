from django import template
from apps.accessories_kit.models import AccessoriesKitItem
from apps.accessories_master.models import Accessories
from apps.product_master.models import Product_Accessories_Kit
register = template.Library()


@register.simple_tag
def product_accessory(pk):
    items = Product_Accessories_Kit.objects.filter(product_accessory=pk).order_by('-id')
    return items

