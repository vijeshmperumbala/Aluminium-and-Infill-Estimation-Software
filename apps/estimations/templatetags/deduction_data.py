from django import template
from apps.estimations.models import (
        EstimationMainProduct, 
        Temp_EstimationMainProduct, 
)

register = template.Library()


@register.simple_tag
def deduction_data(request, product_id):
    """
    The function returns a boolean value indicating whether a deduction value exists for a given product
    ID in either the EstimationMainProduct or Temp_EstimationMainProduct models, depending on the
    request path.
    
    :param request: an HTTP request object that contains information about the current request being
    made to the server
    :param product_id: The ID of the product for which the deduction data is being retrieved
    :return: a boolean value (True or None) based on whether the deducted area for a given product ID
    exists or not in either the EstimationMainProduct or Temp_EstimationMainProduct models, depending on
    the path of the request.
    """
    PATHS = [
        '/Estimation/estimation_list_enquiry/',
        '/Estimation/edit_estimation_pricing/',
        '/Estimation/estimation_list_by_boq_enquiry/',
        '/Estimation/export_csv_estimation_socpe/',
        '/Estimation/export_csv_estimation_socpe_boq/',
        '/Estimation/scope_view/',
        '/Estimation/scope_with_material/',
        '/Project/import_from_scope/',
        '/Estimation/disable_products/',
        '/Estimation/disabled_scope_view/',
        '/Project/proccess_quotation/',
    ]
    if any(path in request.path for path in PATHS):
        EstimationMainProductModel = EstimationMainProduct
    else:
        EstimationMainProductModel = Temp_EstimationMainProduct
        
    deduct = EstimationMainProductModel.objects.get(pk=product_id).deducted_area
   
    if deduct or deduct == '0.00':
        data = True
    else:
        data = None
    
    return data
        