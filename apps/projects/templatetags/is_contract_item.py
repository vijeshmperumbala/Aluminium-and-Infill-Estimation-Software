from django import template

from apps.projects.models import ProjectContractItems
register = template.Library()


@register.simple_tag
def is_contract_item(request, pk, project):
    """
    This function checks if a specific product is a contract item for a given project.
    """
    try:
        products = ProjectContractItems.objects.get(product=pk, project=project)
    except Exception as e:
        products = None
    return bool(products)

