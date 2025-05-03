from django import template
from django.db.models import Sum, Q, Count
from apps.enquiries.models import Enquiries
from apps.estimations.models import EstimationBuildings, Quotations

from apps.projects.models import ProjectContractItems
register = template.Library()


@register.simple_tag
def get_contract_product(request, pk):
    """
    This function returns all project contract items that belong to a building specified by its primary
    key.
    
    """
    # return ProjectContractItems.objects.filter(Q(product__sales_group=pk) &~Q(product__product_type=3))
    return ProjectContractItems.objects.filter(product__sales_group=pk)


@register.simple_tag
def get_projectcontract_item(pk):
    try:
        product = ProjectContractItems.objects.get(product=pk)
    except Exception as e:
        print("EE==>", e)
        product = None
    return product


@register.simple_tag
def get_quotation_number(pk, group_name):
    try:
        enquiry_obj = Enquiries.objects.get(pk=pk)
        building = EstimationBuildings.objects.get(estimation__enquiry=enquiry_obj, building_name=group_name)
        quotation_data = Quotations.objects.get(estimations=building.estimation.id)
        quotation_id = quotation_data.quotation_id
    except Exception as e:
        quotation_id = None
        
    return quotation_id