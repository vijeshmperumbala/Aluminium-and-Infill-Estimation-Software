from django import template
from apps.panels_and_others.models import PanelMasterSpecifications

register = template.Library()


@register.simple_tag
def get_panel_details(pk):
    """
    The function retrieves the panel master specifications object with the given primary key.
    
    :param pk: pk stands for "primary key" and is a unique identifier for a specific record in a
    database table. In this case, the function is using the primary key to retrieve a specific record
    from the PanelMasterSpecifications table
    :return: an object of the `PanelMasterSpecifications` model with the primary key `pk`.
    """
    data_obj = PanelMasterSpecifications.objects.get(pk=pk)
    return data_obj
    