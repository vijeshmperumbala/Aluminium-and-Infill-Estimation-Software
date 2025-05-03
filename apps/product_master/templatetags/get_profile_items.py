import re
from django import template
from apps.product_parts.models import Profile_items
register = template.Library()

    
@register.simple_tag
def get_profile_items(pk):
    """
    This function retrieves all profile items associated with a given profile kit and orders them by
    their ID.
    
    :param pk: The parameter "pk" is likely an abbreviation for "primary key". In this context, it is
    probably referring to the primary key of a Profile object, which is being used to filter and
    retrieve a queryset of related Profile_items objects
    :return: The function `get_profile_items` returns a queryset of `Profile_items` objects that belong
    to a specific profile kit, sorted by their `id`.
    """
    kit_items = Profile_items.objects.filter(profile_kit=pk).order_by('id')
    return kit_items