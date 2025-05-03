
from django import template

from apps.brands.models import CategoryBrands
register = template.Library()


@register.simple_tag
def get_category_brands(pk):
    brands = CategoryBrands.objects.filter(category=pk)
    return brands