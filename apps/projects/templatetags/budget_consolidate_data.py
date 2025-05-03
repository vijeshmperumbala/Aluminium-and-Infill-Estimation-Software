from django import template
from apps.estimations.models import MainProductAluminium, MainProductGlass, EstimationMainProduct, Temp_EstimationMainProduct
from apps.projects.models import SalesOrderItems
register = template.Library()


@register.simple_tag
def budget_consolidate_data(request, pk):
    """
    The function consolidates data from EstimationMainProduct objects based on a list of primary keys.
    
    """
    datas = []
    main_product = SalesOrderItems.objects.filter(sales_group__in=pk).order_by('id') 
    datas.append(main_product)
    
    for data in datas:    
        return data


