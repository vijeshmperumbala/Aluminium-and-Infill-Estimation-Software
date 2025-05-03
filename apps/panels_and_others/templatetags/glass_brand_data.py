
from django import template

from apps.panels_and_others.models import PanelMasterConfiguration
register = template.Library()


@register.simple_tag
def glass_brand_data(request, pk):
    """
        This function returns a queryset of PanelMasterConfiguration objects filtered by the brand specified
        by the primary key.
    """
    return PanelMasterConfiguration.objects.filter(
        panel_specification__series__brands=pk
    )