
from django import template

from apps.brands.models import AccessoriesBrands
register = template.Library()


@register.simple_tag
def get_accessory_brands(pk):
    brands = AccessoriesBrands.objects.filter(category=pk)
    return brands