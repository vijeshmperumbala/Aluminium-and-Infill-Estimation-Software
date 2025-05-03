from django import template
from apps.estimations.models import (
        MainProductAluminium, 
        MainProductGlass, 
        EstimationMainProduct, 
        Temp_EstimationMainProduct, 
        Temp_MainProductAluminium, 
        Temp_MainProductGlass
)

register = template.Library()

@register.simple_tag
def get_product_pricing_type(request, pk):
    """
    The function retrieves the pricing type of a product based on its attributes and returns the pricing
    types for aluminum and glass components.
    """
    PATHS = [
        '/Estimation/product_merge_summary/',
        '/Estimation/merge_summary_print/',
        '/Enquiries/product_category_summary/', 
        '/Estimation/merge_summary_print_2/',
        '/Estimation/costing_summary/',
        '/Estimation/cost_summary_details/',
        '/Estimation/estimation_comparing_summary/',
        '/Estimation/comparing_data/',
        '/Estimation/comparing_data_with_q_id/',
    ]
    if any(path in request.path for path in PATHS):
        EstimationMainProductModel = EstimationMainProduct
        MainProductAluminiumModel = MainProductAluminium
        MainProductGlassModel = MainProductGlass
    else:
        EstimationMainProductModel = Temp_EstimationMainProduct
        MainProductAluminiumModel = Temp_MainProductAluminium
        MainProductGlassModel = Temp_MainProductGlass
        
    product = EstimationMainProductModel.objects.get(pk=pk)
    al_pricing_type = None
    gl_pricing_type = None
    
    try:
        aluminium_obj = MainProductAluminiumModel.objects.get(estimation_product=product.id)
    except Exception:
        aluminium_obj = None
    try:
        glass_obj = MainProductGlassModel.objects.get(estimation_product=product.id, glass_primary=True)
    except Exception:
        glass_obj = None
            
    if aluminium_obj.aluminium_pricing == 1:
        if aluminium_obj.al_price_per_unit:
            al_pricing_type = 'PRE_UNIT'
        elif aluminium_obj.al_price_per_sqm:
            al_pricing_type = 'PRE_SQM'
        elif aluminium_obj.al_weight_per_unit:
            al_pricing_type = 'PRE_KG'
        else:
            al_pricing_type = None
    elif aluminium_obj.aluminium_pricing == 2:
        if aluminium_obj.pricing_unit == 1:
            al_pricing_type = 'CUSTOM_SQM'
        elif aluminium_obj.pricing_unit == 2:
            al_pricing_type = 'CUSTOM_UNIT'
        elif aluminium_obj.pricing_unit == 3:
            al_pricing_type = 'CUSTOM_KG'
        else:
            al_pricing_type = None
    elif aluminium_obj.aluminium_pricing == 4:
        al_pricing_type = 'FORMULA_KG'
    else:
        al_pricing_type = None
    
    if glass_obj:
        if glass_obj.glass_pricing_type == 1:
            gl_pricing_type = 'PRE_SQM'
        elif glass_obj.glass_pricing_type == 2:
            gl_pricing_type = 'CUSTOM_SQM'
        else:
            gl_pricing_type = None
    
    if al_pricing_type and gl_pricing_type:
        context = {
            'al_pricing_type': al_pricing_type,
            'gl_pricing_type': gl_pricing_type
        }
    elif al_pricing_type and not gl_pricing_type:
        context = {
            'al_pricing_type': al_pricing_type,
        }
    elif not al_pricing_type and gl_pricing_type:
        context = {
            'gl_pricing_type': gl_pricing_type
        }
    else:
        context = {
            'al_pricing_type': None,
            'gl_pricing_type': None
        }
        
    
    return context