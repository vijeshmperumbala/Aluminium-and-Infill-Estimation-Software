from django import template

from apps.estimations.models import EstimationMainProduct, EstimationMainProductMergeData, Temp_EstimationMainProduct, Temp_EstimationMainProductMergeData

register = template.Library()


@register.simple_tag
def merge_product(request, pk, main):
    """
    The function checks if a certain path is in the request path and returns a value based on the
    existence of a certain product.
    
    :param request: The HTTP request object containing metadata about the current request
    :param pk: The primary key of the EstimationMainProductModel object
    :param main: The main product that the user is trying to merge
    :return: the value of the variable 'product', which is either None or the value of the 'have_merge'
    attribute of an instance of the EstimationMainProduct or Temp_EstimationMainProduct model, depending
    on the conditions specified in the function.
    """
    PATHS = [
        '/Estimation/edit_estimation_pricing/',
        '/Estimation/view_side_summary/',
        '/Estimation/estimation_list_enquiry/',
        '/Estimation/estimation_list_by_boq_enquiry/',
        '/Estimation/export_csv_estimation_socpe/',
        '/Enquiries/product_category_summary/',
        '/Estimation/merge_summary_print_2/',
        '/Estimation/merge_summary_print/',
        '/Estimation/export_category_summary_building/',
        '/Estimation/export_category_summary/',
        '/Estimation/export_category_summary_boq/',
        '/Estimation/estimation_quotations_list/',
        '/Enquiries/view_quotations/',
        '/Estimation/quotation_print_by_customer/',
        '/Estimation/quotation_print_by_customer_boq/',
        '/Estimation/quotation_print_boq/',
        '/Estimation/quotation_print/',
        '/Enquiries/edit_quotation/', 
        '/Enquiries/create_quotation_base/', 
        '/Estimation/merge_summary_update/',
        '/Estimation/building_price_print/',
        '/Estimation/export_csv_estimation_socpe_boq/',
        '/Estimation/consolidate_aluminium_update/',
        '/Estimation/category_wise_product/',
        '/Estimation/consolidate_sealant_update/',
        '/Estimation/consolidate_sealant_products/',
        '/Estimation/consolidate_loh_update/',
        '/Estimation/spec_data_loh/',
        '/Estimation/consolidate_unitprice_update/',
        '/Estimation/consolidate_unit_product/',
        '/Enquiries/get_customer_data/',
        '/Estimation/sync_quotation/',
        '/Estimation/submit_estimation/',
        '/Enquiries/new_quotaion_customers/',
        '/Estimation/quotation_by_boq_enquiry/',
        '/Estimation/deduction_material_summary/',
        
    ]
    
    if any(path in request.path for path in PATHS):
        EstimationMainProductModel = EstimationMainProduct
    else:
        EstimationMainProductModel = Temp_EstimationMainProduct
    try:
        
        product = EstimationMainProductModel.objects.get(pk=pk, main_product=main, product_type=2).main_product.have_merge
    except Exception as e:
        product = None
    return product