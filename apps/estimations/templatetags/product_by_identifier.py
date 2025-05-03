from django import template
from apps.estimations.models import  EstimationMainProduct, Temp_EstimationMainProduct
from django.db.models import F, Func

register = template.Library()


@register.simple_tag
def product_by_identifier(request, version, pk):
    """
    This function retrieves curtain wall and other products based on version and specification
    identifier.
    
    :param request: The HTTP request object that contains information about the current request, such as
    the path, method, headers, and body
    :param version: It is a parameter that represents the version of an estimation
    :param pk: pk stands for primary key, which is a unique identifier for a specific record in a
    database table. In this context, it is used to filter the EstimationMainProductModel objects based
    on the specification_Identifier field
    :return: a dictionary containing two keys: 'curtain_wall_products' and 'other_products'. The values
    for these keys are querysets of EstimationMainProductModel objects filtered by certain conditions
    and annotated with additional fields.
    """
    PATHS = [
        '/Estimation/product_merge_summary/',
        '/Estimation/merge_summary_print/',
        '/Enquiries/product_category_summary/',
        '/Estimation/merge_summary_print_2/',
        '/Estimation/costing_summary/',
        '/Estimation/comparing_data/',
    ]
    
    if any(path in request.path for path in PATHS):
        EstimationMainProductModel = EstimationMainProduct
    else:
        EstimationMainProductModel = Temp_EstimationMainProduct
        
    curtain_wall_products = EstimationMainProductModel.objects.filter(
        category__is_curtain_wall=True,
        building__estimation=version,
        specification_Identifier=pk,
        disabled=False
    ).annotate(
        product_sqm_price_without_addon_int=Func(F('product_sqm_price_without_addon'), function='FLOOR')
    ).distinct('product_sqm_price_without_addon_int', 'product__product_name')
    other_products = EstimationMainProductModel.objects.filter(category__is_curtain_wall=False, \
        building__estimation=version, specification_Identifier=pk).distinct('product_base_rate', 'product__product_name')
    data = {
        'curtain_wall_products': curtain_wall_products,
        'other_products': other_products,
    }
    return data

