
from django import template

from apps.projects.models import ContractItems
register = template.Library()


@register.simple_tag
def get_contract_quantity(request, pk, project, product):
    """
    This function retrieves the contract quantity for a given product associated with a specific project
    and contract.
    
    """
    try:
        item = ContractItems.objects.get(associated_product=pk, project_contract__project=project, project_contract__product=product)
    except Exception as e:
        item = None
        
    return item
    