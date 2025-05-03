from django import template
import math
from apps.estimations.models import (
        MainProductAluminium, 
        MainProductGlass, 
        MainProductAddonCost, 
        EstimationMainProduct, 
        MainProductSilicon,
        PricingOption, 
        Temp_EstimationMainProduct, 
        Temp_MainProductAddonCost, 
        Temp_MainProductAluminium, 
        Temp_MainProductGlass, 
        Temp_MainProductSilicon, 
        Temp_PricingOption
        )

register = template.Library()


@register.simple_tag
def quotation_product_data(request, pk):
    """
    This function calculates the cost and pricing information for a quotation product based on various
    inputs and returns the data in a dictionary format.
    
    :param request: The HTTP request object that contains information about the current request, such as
    the user making the request and any data submitted with the request
    :param pk: The primary key of the EstimationMainProduct or Temp_EstimationMainProduct object being
    queried
    :return: a dictionary containing data related to a quotation product, including the main product,
    aluminium object, unit price, total price, and rate per square meter.
    """
    material_cost = 0
    labour_percent_price = 0
    overhead_percent_price = 0
    total_addon_cost = 0
    PATHS = [
                    '/Enquiries/view_quotations/', 
                    '/Enquiries/edit_quotation/', 
                    '/Estimation/quotation_by_boq_enquiry/',              
                    '/Estimation/quotation_print_by_customer/', 
                    '/Estimation/quotation_print/', 
                    '/Estimation/quotation_print_boq/',              
                    '/Estimation/quotation_print_by_customer_boq/', 
                    '/Enquiries/create_quotation_base/',
                    '/Estimation/building_price_print/',
                    '/Enquiries/new_quotaion_customers/',
                    '/Estimation/sync_quotation/',
                    '/Enquiries/get_customer_data/',
                    '/Estimation/submit_estimation/',
                    '/Estimation/estimation_quotations_list/',
                    '/Estimation/quotation_by_boq_enquiry/',
                    '/Estimation/quotation_unit_price/',

                ]

    if any(path in request.path for path in PATHS):
        MainProduct = EstimationMainProduct
        AluminiumModel = MainProductAluminium
        MainProductAddonCostModel = MainProductAddonCost
        MainProductGlassModel = MainProductGlass
        PricingOptionModel = PricingOption
        MainProductSiliconModel = MainProductSilicon
    else:
        MainProduct = Temp_EstimationMainProduct
        AluminiumModel = Temp_MainProductAluminium
        MainProductAddonCostModel = Temp_MainProductAddonCost
        MainProductGlassModel = Temp_MainProductGlass
        PricingOptionModel = Temp_PricingOption
        MainProductSiliconModel = Temp_MainProductSilicon


    try:
        main_product = MainProduct.objects.get(pk=pk)
    except Exception:
        main_product = None
    try:
        aluminium_obj = AluminiumModel.objects.get(estimation_product=pk)
    except Exception:
        aluminium_obj = None
    try:
        glass_obj = MainProductGlassModel.objects.get(estimation_product=pk, glass_primary=True)
        second_glass_obj = MainProductGlassModel.objects.select_related('estimation_product').filter(estimation_product=pk, glass_primary=False)
    except Exception:
        glass_obj = None
        second_glass_obj = None
    try:
        silicon_obj = MainProductSiliconModel.objects.get(estimation_product=pk)
    except Exception:
        silicon_obj = None
    try:
        pricing_control = PricingOptionModel.objects.get(estimation_product=pk)
    except Exception as e:
        pricing_control = None

    if aluminium_obj and aluminium_obj.al_quoted_price:
        material_cost += float(aluminium_obj.al_quoted_price)
        
    if main_product.deduction_method == 2:
        deducted_area = float(aluminium_obj.area) - float(main_product.deducted_area)
        unit_area = round(deducted_area, 2)
    else:
        unit_area = round(float(aluminium_obj.area), 2)

    if glass_obj and (glass_obj.is_glass_cost and glass_obj.glass_quoted_price):
        material_cost += float(glass_obj.glass_quoted_price)

    if second_glass_obj:
        for second_glass in second_glass_obj:
            material_cost += float(second_glass.glass_quoted_price)

    if silicon_obj and silicon_obj.is_silicon:
        material_cost += float(silicon_obj.silicon_quoted_price)
    if main_product and (main_product.accessory_total and main_product.is_accessory):
        material_cost += float(main_product.accessory_total)
    if pricing_control:
        if pricing_control.labour_perce:
            labour_percentage = float(pricing_control.labour_perce)/100
            labour_percent_price = round(float(material_cost)*float(labour_percentage), 4)

        if pricing_control.overhead_perce:
            overhead_percentage = float(pricing_control.overhead_perce)/100
            overhead_percent_price = round(float(material_cost)*float(overhead_percentage), 4)

    sub_total = (material_cost+labour_percent_price+overhead_percent_price+float(main_product.total_addon_cost))
    
    if aluminium_obj.aluminium_pricing in [1, 2, 4]:
        if main_product:
            if main_product.is_tolerance and main_product.tolerance_type == 1:
                tolarance = int(main_product.tolerance) / 100
                tolarance_price = float(aluminium_obj.al_quoted_price) * tolarance
            elif main_product.is_tolerance and main_product.tolerance_type == 2:
                tolarance_price = main_product.tolerance
            else:
                tolarance_price = 0
        else:
            tolarance_price = 0
    else:
        tolarance_price = 0
        
    if not main_product.have_merge: 
        if not main_product.after_deduction_price:
            rpu = round((float(sub_total)+float(tolarance_price)), 2)
        else: 
            temp = float(main_product.after_deduction_price)
            rpu = round(temp, 2)

        total = (float(rpu)*float(aluminium_obj.total_quantity))
        round_total = round((math.ceil(float(rpu))*float(aluminium_obj.total_quantity)), 2)
        if main_product.after_deduction_price:
            rate_per_sqm = float(rpu)/(float(aluminium_obj.area)-float(main_product.deducted_area))
        else:
            rate_per_sqm = float(rpu)/float(aluminium_obj.area)
    else:
        rpu = float(round(main_product.merge_price, 2))
        total = float(main_product.merge_price)*float(aluminium_obj.total_quantity)
        round_total = math.ceil(float(main_product.merge_price)*float(aluminium_obj.total_quantity))
        if main_product.after_deduction_price:
            rate_per_sqm = float(rpu)/(float(aluminium_obj.area)-float(main_product.deducted_area))
        else:
            rate_per_sqm = float(rpu)/float(aluminium_obj.area)
    
    return {
        'main_product': main_product,
        'aluminium_obj': aluminium_obj,
        'rpu': round(rpu, 2),
        'round_rpu': math.ceil(round(rpu, 2)),
        'total': total,
        'round_total': round_total,
        'rate_per_sqm': math.ceil(round(rate_per_sqm, 2)),
        'unit_area': unit_area,
    }