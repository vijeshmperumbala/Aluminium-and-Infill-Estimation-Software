from django import template
from apps.panels_and_others.models import PanelMasterBrands

register = template.Library()


@register.simple_tag
def get_panel_brands(pk):
    """
    This function retrieves a list of panel brands based on a given panel category ID.
    
    :param pk: The parameter "pk" is likely an abbreviation for "primary key". It is likely used as a
    reference to a specific record in a database table, in this case, the "panel_category" table. The
    function is likely retrieving a list of panel brands that belong to the panel category with the
    specified
    :return: a list of PanelMasterBrands objects that belong to a specific panel category, sorted by
    their id.
    """
    panel_brands = PanelMasterBrands.objects.select_related('panel_category').filter(panel_category=pk).order_by('id')
    brands_list = []
    for brand in panel_brands:
        brands_list.append(brand)
    return brands_list