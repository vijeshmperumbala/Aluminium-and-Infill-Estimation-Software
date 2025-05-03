from django import template

from apps.projects.models import (
            Eps_Product_Details, Eps_infill_Temp, ProjectContractItems
            )
register = template.Library()


@register.simple_tag
def check_EPS_Product_created(request, pk, type=None):
    """
    This function checks if an EPS product has been created for a given main product ID.
    
    """
    if type:
        try:
            product = Eps_infill_Temp.objects.filter(main_product=pk)
            
        except Eps_infill_Temp.DoesNotExist:
            product = None
    else:
        try:
            product = Eps_Product_Details.objects.filter(main_product=pk)
        except Eps_Product_Details.DoesNotExist:
            product = None
    
    return product