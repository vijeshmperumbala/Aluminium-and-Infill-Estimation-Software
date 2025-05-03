from django import template
from django.db.models import Q
from apps.enquiries.models import EnquirySpecifications
from apps.estimations.models import (
                MainProductAluminium, 
                MainProductGlass, 
                EstimationMainProduct, 
                Temp_EstimationMainProduct,
)
register = template.Library()

PATHS = [
        '/Estimation/estimation_pricing_summary/',
        '/Estimation/estimation_list_enquiry/',
        '/Enquiries/product_category_summary/',
        '/Enquiries/view_quotations/',
        '/Enquiries/edit_quotation/',
        '/Estimation/estimation_list_enquiry/',
        '/Estimation/estimation_detail_summary/',
        '/Project/project_scop/',
        '/Project/project_budgeting/',
        '/Project/project_accounts/',
        '/Estimation/quotation_print_by_customer/',
        '/Estimation/quotation_print/',
        '/Enquiries/create_quotation_base/',
        '/Estimation/building_category_summary/',
        '/Estimation/export_csv_estimation_socpe/',
        '/Estimation/export_category_summary_building/',
        '/Project/proccess_quotation/',
        '/Project/import_from_scope/',
        '/Project/project_contract_items/',
        '/Estimation/building_price_print/',
        '/Estimation/sync_quotation/',
        '/Estimation/building_summary/',
        '/Estimation/building_scope_summary_print/',
        '/Enquiries/get_customer_data/',
        '/Estimation/scope_with_material/',
        '/Estimation/consolidate_scope_summary_print/',
        '/Estimation/submit_estimation/',
        '/Enquiries/new_quotaion_customers/',
        '/Estimation/estimation_quotations_list/',
        '/Estimation/quotation_by_boq_enquiry/',
        '/Estimation/quotation_unit_price/',
        '/Estimation/spec_wise_building/',
        '/Estimation/disable_products/',
        
    ]


@register.simple_tag
def estimation_data(request, pk):
    """
    The function returns a queryset of EstimationMainProduct or Temp_EstimationMainProduct objects based
    on the request path and a given primary key.
    
    """
    
    try:
        if any(path in request.path for path in PATHS):
            # main_product = EstimationMainProduct.objects.select_related('building').filter(building=pk, disabled=False).order_by('associated_key', 'id')
            main_product = EstimationMainProduct.objects.select_related('building').filter(building=pk, disabled=False).order_by('product_index')
        else:
            # main_product = Temp_EstimationMainProduct.objects.select_related('building').filter(building=pk, disabled=False).order_by('associated_key', 'id')
            main_product = Temp_EstimationMainProduct.objects.select_related('building').filter(building=pk, disabled=False).order_by('product_index')
            
    except Exception as e:
        main_product = None
    return main_product

@register.simple_tag
def estimation_data_disabled(request, pk):
    """
    The function returns a queryset of EstimationMainProduct or Temp_EstimationMainProduct objects based
    on the request path and a given primary key.
    
    """
    
    try:
        if any(path in request.path for path in PATHS):
            main_product = EstimationMainProduct.objects.select_related('building').filter(building=pk).order_by('associated_key', 'id')
        else:
            main_product = Temp_EstimationMainProduct.objects.select_related('building').filter(building=pk).order_by('associated_key', 'id')
    except Exception as e:
        main_product = None
    return main_product


@register.simple_tag
def scope_summary(request, pk):
    """
    The function `scope_summary` retrieves a distinct set of main products based on the given request
    and primary key.
    
    :param request: The `request` parameter is an object that represents the HTTP request made by the
    client. It contains information such as the request method, headers, and path
    :param pk: The "pk" parameter is the primary key of the building object. It is used to filter the
    main products based on the building
    :return: the variable "main_product".
    """
    try:
        if any(path in request.path for path in PATHS):
            main_product = EstimationMainProduct.objects.select_related('building').filter(building=pk).distinct('category')
        else:
            main_product = Temp_EstimationMainProduct.objects.select_related('building').filter(building=pk).distinct('category')
    except Exception as e:
        
        main_product = None
        
    return main_product


@register.simple_tag
def scope_summary_spec(request, pk):
   
    try:
        if any(path in request.path for path in PATHS):
            specifications = EnquirySpecifications.objects.filter(pk__in=[product.specification_Identifier.id for product in EstimationMainProduct.objects.select_related('building').filter(building=pk).distinct('specification_Identifier')])
        else:
            specifications = EnquirySpecifications.objects.filter(pk__in=[product.specification_Identifier.id for product in Temp_EstimationMainProduct.objects.select_related('building').filter(building=pk).distinct('specification_Identifier')])
    except Exception as e:
        
        specifications = None
        
    return specifications