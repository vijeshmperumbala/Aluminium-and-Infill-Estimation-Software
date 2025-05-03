import re
from django import template
from apps.product_parts.models import Product_Parts_Kit_Items, Profile_items
register = template.Library()


@register.simple_tag
def get_kit_items(pk):
    """
    This function retrieves all the kit items associated with a given product parts kit.
    
    :param pk: pk stands for "primary key" and it is a unique identifier for a specific record in a
    database table. In this case, it is used to filter the Product_Parts_Kit_Items objects based on the
    product_parts_kit field, which is likely a foreign key to another table representing a kit
    :return: The function `get_kit_items` returns a queryset of `Product_Parts_Kit_Items` objects that
    belong to a specific `product_parts_kit` identified by the primary key `pk`. The queryset is ordered
    by the `id` field.
    """
    kit_items = Product_Parts_Kit_Items.objects.filter(product_parts_kit=pk).order_by('id')
    return kit_items