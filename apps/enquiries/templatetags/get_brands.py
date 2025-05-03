from django import template
from apps.brands.models import CategoryBrands
from apps.configuration_master.models import ConfigurationMasterBrands, ConfigurationMasterBase
from apps.panels_and_others.models import PanelMasterBrands

register = template.Library()


@register.simple_tag
def get_brands(pk):
    """
    The function retrieves a list of brands based on a given category primary key.
    
    :param pk: The parameter `pk` is likely an integer representing the primary key of a category in a
    database. It is used to filter the `ConfigurationMasterBrands` objects by their associated category
    :return: a list of ConfigurationMasterBrands objects that belong to a specific category, sorted by
    their id.
    """
    brands = ConfigurationMasterBrands.objects.select_related('category').filter(category=pk).order_by('id')
    brands_list = []
    for brand in brands:
        brands_list.append(brand)
    return brands_list
