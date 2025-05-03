from django import template
import math
from apps.estimations.models import (
        MainProductAccessories, 
        MainProductAluminium, 
        MainProductGlass, 
        MainProductAddonCost, 
        EstimationMainProduct, 
        MainProductSilicon,
        PricingOption, 
        Temp_EstimationMainProduct, 
        Temp_MainProductAccessories, 
        Temp_MainProductAddonCost, 
        Temp_MainProductAluminium, 
        Temp_MainProductGlass, 
        Temp_MainProductSilicon, 
        Temp_PricingOption
)

register = template.Library()


@register.simple_tag
def category_summary_data(request, pk):
    """
    This function calculates and returns various data related to a product category summary.
    
    :param request: The HTTP request object containing metadata about the current request
    :param pk: The primary key of the MainProduct object
    :return: a dictionary named 'data' which contains various calculated values and objects retrieved
    from the database based on the input parameter 'pk'.
    """
    PATHS = [
        '/Enquiries/product_category_summary/',
        '/Estimation/product_merge_summary/',
        '/Estimation/product_merge_summary/',
        '/Estimation/merge_summary_print/',
        '/Estimation/merge_summary_print_2/',
        '/Estimation/export_category_summary/',
        '/Estimation/export_category_summary_building/',
        '/Estimation/export_category_summary_boq/',
    ]
        
    if any(path in request.path for path in PATHS):
        MainProduct = EstimationMainProduct
        AluminiumModel = MainProductAluminium
        MainProductGlassModel = MainProductGlass
        MainProductAddonCostModel = MainProductAddonCost
        MainProductSiliconModel = MainProductSilicon
        PricingOptionModel = PricingOption
        MainProductAccessoriesModel = MainProductAccessories
    else:
        MainProduct = Temp_EstimationMainProduct
        AluminiumModel = Temp_MainProductAluminium
        MainProductGlassModel = Temp_MainProductGlass
        MainProductAddonCostModel = Temp_MainProductAddonCost
        MainProductSiliconModel = Temp_MainProductSilicon
        PricingOptionModel = Temp_PricingOption
        MainProductAccessoriesModel = Temp_MainProductAccessories
        
    try:
        main_product = MainProduct.objects.get(pk=pk)
    except:
        main_product = None
    try:
        aluminium_obj = AluminiumModel.objects.get(estimation_product=pk)
    except:
        aluminium_obj = None
    try:
        glass_obj = MainProductGlassModel.objects.get(estimation_product=pk, glass_primary=True)
        second_glass_obj = MainProductGlassModel.objects.select_related('estimation_product').filter(estimation_product=pk, glass_primary=False)
    except:
        glass_obj = None
        second_glass_obj = None
    try:
        silicon_obj = MainProductSiliconModel.objects.get(estimation_product=pk)
    except:
        silicon_obj = None
    try:
        pricing_control = PricingOptionModel.objects.get(estimation_product=pk)
    except Exception as e:
        pricing_control = None
    addons = MainProductAddonCostModel.objects.select_related('estimation_product').filter(estimation_product=pk)
    
        
    total_addon_cost = 0
    total_access_price = 0
    unit_price = 0
    glass_total = 0
    sec_glass_total = 0
    alumin_total = 0
    silicon_total = 0
    labour_percent_price = 0
    overhead_percent_price = 0
    tolarance_price = 0
    total_area = 0
    rate_per_sqm_without_addons = 0
    typical_buildings = 1
    deducted_area_out = 0
    
    unit_area = float(aluminium_obj.area)
    quantity = aluminium_obj.total_quantity
    if main_product.building.typical_buildings_enabled:
        typical_buildings = main_product.building.no_typical_buildings
    
    if main_product.deduction_method == 2 or main_product.deduction_method == 1:
        deducted_area = (float(aluminium_obj.area) - (float(main_product.deducted_area)))
        total_area = float(deducted_area) * float(quantity)
        deducted_area_out = (float(main_product.deducted_area)* float(quantity))
    else:
        total_area = float(unit_area) * float(quantity)
        
        # deducted_area_out += total_area
    
    if aluminium_obj.product_configuration or aluminium_obj.custom_price or aluminium_obj.price_per_kg:    
        if aluminium_obj.al_quoted_price:
            alumin_total = float(aluminium_obj.al_quoted_price)
        aluminium_markup_perce = aluminium_obj.al_markup
    else:
        aluminium_markup_perce = 0
        
    if glass_obj:
        if glass_obj.is_glass_cost and glass_obj.glass_base_rate:
            glass_total += float(glass_obj.glass_quoted_price)
        glass_markup_perce = glass_obj.glass_markup_percentage
    else:
        glass_markup_perce = 0
    if second_glass_obj:
        for second_glass in second_glass_obj:
            if second_glass.is_glass_cost and second_glass.glass_base_rate :
                sec_glass_total += float(second_glass.glass_quoted_price)
                
    glass_total = glass_total + sec_glass_total
        
    if silicon_obj and silicon_obj.is_silicon:
        silicon_total += float(silicon_obj.silicon_quoted_price)
            
    if main_product:
        if main_product.enable_addons:
            total_addon_cost += float(main_product.total_addon_cost)
            
        if main_product.accessory_total and main_product.is_accessory:
            total_access_price += float(main_product.accessory_total)

    material_total = (alumin_total + glass_total + total_access_price + silicon_total)
    if pricing_control.labour_perce:
        labour_percentage = float(pricing_control.labour_perce)/100
        labour_percent_price = round(float(material_total)*float(labour_percentage), 4)

    if pricing_control.overhead_perce:
        overhead_percentage = float(pricing_control.overhead_perce)/100
        overhead_percent_price = round(float(material_total)*float(overhead_percentage), 4)
    l_oh_perce = float(pricing_control.overhead_perce)+float(pricing_control.labour_perce)
    
    sub_total = ((float(overhead_percent_price)+float(labour_percent_price)))+material_total
    
    if aluminium_obj.aluminium_pricing == 1 or aluminium_obj.aluminium_pricing == 2 or aluminium_obj.aluminium_pricing == 4:
        if main_product.is_tolerance:
            if main_product.tolerance_type == 1:
                tolarance = int(main_product.tolerance)/100
                tolarance_price = (float(aluminium_obj.al_quoted_price))*tolarance
            elif main_product.tolerance_type == 2:
                tolarance_price = float(main_product.tolerance)
            else:
                tolarance_price = 0
        else:
            tolarance_price = 0
    else:
        tolarance_price = 0
        
        
    if not main_product.have_merge:
        if not main_product.after_deduction_price:
            rate_per_unit = float(material_total)+float(tolarance_price)+float(labour_percent_price)+\
                                                float(overhead_percent_price)+float(total_addon_cost)
                                                
            line_total = float(math.ceil(rate_per_unit))*float(aluminium_obj.total_quantity)
            round_line_total = (float(math.ceil(rate_per_unit)))*float(aluminium_obj.total_quantity)
    
        else:
            rate_per_unit = float(main_product.after_deduction_price)
            line_total = float(rate_per_unit)*float(aluminium_obj.total_quantity)
            round_line_total = float(math.ceil(rate_per_unit))*float(aluminium_obj.total_quantity)
                
    else:
        # rate_per_unit = float(main_product.merge_price)
        # line_total = float(rate_per_unit)
        # round_line_total = float(math.ceil(line_total))*float(aluminium_obj.total_quantity)
        rate_per_unit = float(material_total)+float(tolarance_price)+float(labour_percent_price)+\
                                                float(overhead_percent_price)+float(total_addon_cost)
                                                
        line_total = float(math.ceil(rate_per_unit))*float(aluminium_obj.total_quantity)
        round_line_total = (float(math.ceil(rate_per_unit)))*float(aluminium_obj.total_quantity)
    try:
        rate_per_sqm = round_line_total/total_area
        if not main_product.have_merge:
            if not main_product.after_deduction_price:
                temp = (float(material_total)+float(labour_percent_price)+float(overhead_percent_price))*float(aluminium_obj.total_quantity)
                rate_per_sqm_without_addons = temp/total_area
            else:
                temp = ((float(main_product.after_deduction_price)) - (float(tolarance_price)+float(total_addon_cost)))*float(aluminium_obj.total_quantity)
                rate_per_sqm_without_addons = temp/total_area
        else:
            # temp = (float(main_product.merge_price) - ((float(tolarance_price)+float(total_addon_cost))))*float(aluminium_obj.total_quantity)
            # rate_per_sqm_without_addons = temp/total_area
            temp = (float(material_total)+float(labour_percent_price)+float(overhead_percent_price))*float(aluminium_obj.total_quantity)
            rate_per_sqm_without_addons = temp/total_area
            
    except Exception as e:
        rate_per_sqm = 0
        rate_per_sqm_without_addons = 0
        
    
    data = {
        'line_total': float(line_total)*float(typical_buildings),
        'round_line_total': float(round_line_total)*float(typical_buildings),
        'rate_per_unit': rate_per_unit,
        'round_rate_per_unit': math.ceil(rate_per_unit),
        'tolarance_price': float(tolarance_price),
        # 'sub_total': round(sub_total, 2),
        'overhead_percent_price': overhead_percent_price,
        'labour_percent_price': labour_percent_price,
        'l_o': labour_percent_price+overhead_percent_price,
        'material_total': material_total,
        'unit_price': unit_price,
        'addons': addons,
        'main_product': main_product,
        'aluminium_obj': aluminium_obj,
        'glass_obj': glass_obj,
        'silicon_obj': silicon_obj,
        'silicon_total': silicon_total,
        'pricing_control': pricing_control,
        'rate_per_sqm': round(rate_per_sqm, 2),
        'second_glass_obj': second_glass_obj,
        
        'aluminium_markup_perce': aluminium_markup_perce,
        'glass_markup_perce': glass_markup_perce,
        'l_oh_perce': l_oh_perce,
        'rate_per_sqm_without_addons': rate_per_sqm_without_addons,
        'total_access_price': total_access_price,
        'sub_total': sub_total,
        'total_addon_cost': total_addon_cost,
    }
    return data
