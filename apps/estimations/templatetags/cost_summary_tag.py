import math
from django import template

from apps.estimations.models import (
        EstimationMainProduct, 
        MainProductAluminium, 
        MainProductSilicon, 
        PricingOption, 
        Temp_EstimationMainProduct, 
        Temp_MainProductAluminium, 
        MainProductGlass, 
        Temp_MainProductGlass, 
        Temp_MainProductSilicon, 
        Temp_PricingOption,
)
from django.db.models import (
        Count, 
        DecimalField, 
        F, 
        IntegerField, 
        Func, 
        Q,
)

register = template.Library()
        
    
@register.simple_tag
def cost_summary_data(request, pk, version):
    """
        This function retrieves cost summary data for different types of products based on certain filters.
        
        :param request: The HTTP request object containing metadata about the request being made
        :param pk: pk is a parameter that represents the specification identifier of a product. It is used
        to filter the EstimationMainProduct or Temp_EstimationMainProduct objects based on this identifier
        :param version: The version parameter is likely referring to a specific version or iteration of an
        estimation or cost summary. It is used to filter the EstimationMainProduct or
        Temp_EstimationMainProduct objects based on the version specified
        :return: a dictionary containing three keys: 'curtain_wall_products', 'other_products', and
        'glass_only_products'. The values for each key are QuerySets of EstimationMainProduct or
        Temp_EstimationMainProduct objects filtered by certain conditions.
    """
    PATHS = [
        '/Estimation/costing_summary/',
        '/Estimation/cost_summary_details/',
        '/Estimation/estimation_comparing_summary/',
        '/Estimation/comparing_data/',
        '/Estimation/comparing_data_with_q_id/',
    ]

    if any(path in request.path for path in PATHS):
        curtain_wall_products = EstimationMainProduct.objects.filter(
            Q(category__is_curtain_wall=True) &
            Q(building__estimation=version) &
            Q(specification_Identifier=pk) &
            Q(main_product_aluminium__pricing_unit__isnull=False) &
            Q(disabled=False)
        ).distinct('main_product_aluminium__pricing_unit')

        other_products = EstimationMainProduct.objects.filter(
                    Q(category__is_curtain_wall=False) &
                    Q(building__estimation=version) & 
                    Q(specification_Identifier=pk) &
                    Q(main_product_aluminium__pricing_unit__isnull=False) &
                    Q(disabled=False)
                ).distinct('main_product_aluminium__pricing_unit')

        glass_only_products = EstimationMainProduct.objects.filter(
                    Q(category__is_curtain_wall=False) &
                    Q(building__estimation=version) & 
                    Q(specification_Identifier=pk) &
                    Q(main_product_aluminium__pricing_unit__isnull=True) &
                    Q(disabled=False)
                ).distinct('main_product_aluminium__pricing_unit')
        
        
    else:

        curtain_wall_products = Temp_EstimationMainProduct.objects.filter(
            Q(category__is_curtain_wall=True) &
            Q(building__estimation=version) &
            Q(specification_Identifier=pk) &
            Q(main_product_aluminium_temp__pricing_unit__isnull=False) &
            Q(disabled=False)
        ).distinct( 'main_product_aluminium_temp__pricing_unit')

        other_products = Temp_EstimationMainProduct.objects.filter(
                    Q(category__is_curtain_wall=False) &
                    Q(building__estimation=version) & 
                    Q(specification_Identifier=pk) &
                    Q(main_product_aluminium_temp__pricing_unit__isnull=False) &
                    Q(disabled=False)
                ).distinct('main_product_aluminium_temp__pricing_unit')

        glass_only_products =  Temp_EstimationMainProduct.objects.filter(
                    Q(category__is_curtain_wall=False) &
                    Q(building__estimation=version) & 
                    Q(specification_Identifier=pk) &
                    Q(main_product_aluminium_temp__pricing_unit__isnull=True) &
                    Q(disabled=False)
                ).distinct('main_product_aluminium_temp__pricing_unit')
        
    
    return {
        'curtain_wall_products': curtain_wall_products,
        'other_products': other_products,
        'glass_only_products': glass_only_products,
    }


@register.simple_tag
def costing_summary_price_control(
                                    request, 
                                    specification, 
                                    price_type, 
                                    curtain_wall_type=None,
                                ):
    
    """
        COSTING SUMMARY FUNCTION
    """
    
    if price_type == 'CUSTOM_KG':
        pricing_unit = 3
        uom = "KG"
    elif price_type == 'CUSTOM_UNIT':
         pricing_unit = 2
         uom = "No's"
    elif price_type == 'CUSTOM_SQM':
         pricing_unit = 1
         uom = "SqM"
    elif price_type == 'PRE_UNIT':
         pricing_unit = 2
         uom = "No's"
    elif price_type == 'PRE_SQM':
         pricing_unit = 1
         uom = "SqM"
    elif price_type == 'PRE_KG':
         pricing_unit = 3
         uom = "KG"
    elif price_type == 'FORMULA_KG':
         pricing_unit = 3
         uom = "KG"
    else:
        pricing_unit = None
        uom = "Lm"
    
    PATHS = [
        '/Estimation/costing_summary/',
        '/Estimation/cost_summary_details/',
        '/Estimation/estimation_comparing_summary/',
        '/Estimation/comparing_data/',
        '/Estimation/comparing_data_with_q_id/',
    ]
    
    if any(path in request.path for path in PATHS):
        curtain_wall_products = EstimationMainProduct.objects.filter(
                                                                        specification_Identifier=specification, 
                                                                        main_product_aluminium__pricing_unit=pricing_unit,
                                                                        disabled=False
                                                                    )
        
        MainProductAluminiumModel = MainProductAluminium
        MainProductGlassModel = MainProductGlass
        MainProductSiliconModel = MainProductSilicon
        PricingOptionModel = PricingOption
        products = EstimationMainProduct.objects.filter(
                                                            specification_Identifier=specification,
                                                            main_product_aluminium__pricing_unit=pricing_unit,
                                                            disabled=False
                                                        )
       
    else:
        curtain_wall_products = Temp_EstimationMainProduct.objects.filter(
                                                                            specification_Identifier=specification, 
                                                                            main_product_aluminium_temp__pricing_unit=pricing_unit,
                                                                            disabled=False
                                                                        )
        MainProductAluminiumModel = Temp_MainProductAluminium
        MainProductGlassModel = Temp_MainProductGlass
        MainProductSiliconModel = Temp_MainProductSilicon
        PricingOptionModel = Temp_PricingOption
        products = Temp_EstimationMainProduct.objects.filter(
                                                                specification_Identifier=specification,
                                                                main_product_aluminium_temp__pricing_unit=pricing_unit,
                                                                disabled=False
                                                            )
    
    
        
    aluminium_unit_base_rate = 0
    aluminium_quantity = 0
    aluminium_markup = 0
    alum_unit_qty = 0
    area = 0
    
    aluminium_quote_rate = 0
    aluminium_quote_value = 0
    total_product_area = 0
    
    infill_base_rate = 0
    infill_quote_value = 0
    infill_area = 0
    infill_markup = 0
    infill_quote_rate = 0
    total_product_quantity = 0
    sec_infill = None
    sealant_price = 0
    accesory_price = 0
    tolerance_price = 0
    loh = 0
    loh_percentage = 0
    
    addon_price = 0
    rate_per_sqm = 0
    aluminium_unit_surface = 0
    total_price = 0
    unit_price = 0
    labour_percentage = 0
    overhead_percentage = 0
    labour_percentage_list = []
    overhead_percentage_list = []
    labour_flag = None
    overhead_flag = None
    cost_of_materials = 0
    
    
    
    for product in products:
        if product.building.typical_buildings_enabled:
            typical_building = product.building.no_typical_buildings
        else:
            typical_building = 1
            
        try:
            aluminium = MainProductAluminiumModel.objects.get(estimation_product=product.id)
        except:
            aluminium = None
            
        try:
            infill = MainProductGlassModel.objects.get(estimation_product=product.id, glass_primary=True)
            sec_infill = MainProductGlassModel.objects.filter(estimation_product=product.id, glass_primary=False)
        except:
            infill = None
            sec_infill = None
        
        try:
            sealant_data = MainProductSiliconModel.objects.get(estimation_product=product.id)
        except:
            sealant_data = None

        try:
            pricing_option = PricingOptionModel.objects.get(estimation_product=product.id)
        except:
            pricing_option = None
            
        if pricing_option:
            labour_percentage = pricing_option.labour_perce
            labour_percentage_list.append(pricing_option.labour_perce)
            overhead_percentage = pricing_option.overhead_perce
            overhead_percentage_list.append(pricing_option.overhead_perce)
            labour_flag = all(element == labour_percentage_list[0] for element in labour_percentage_list)
            overhead_flag = all(element == overhead_percentage_list[0] for element in overhead_percentage_list)
            
        if aluminium:
            if aluminium.surface_finish:
                aluminium_unit_surface = aluminium.surface_finish.surface_finish_price
            aluminium_markup = aluminium.al_markup
            area += aluminium.area
            if aluminium.aluminium_pricing == 4:
                aluminium_unit_base_rate = aluminium.price_per_kg
                # if aluminium.total_weight:
                aluminium_quantity += float(aluminium.total_weight)*float(typical_building)
                alum_unit_qty = float(aluminium.weight_per_unit)*float(typical_building)
                aluminium_quote_rate = (float(aluminium_unit_base_rate)*(float(aluminium_markup)/100))+float(aluminium_unit_base_rate)+float(aluminium_unit_surface)
            elif aluminium.aluminium_pricing == 2:
                if aluminium.pricing_unit == 1:
                    aluminium_unit_base_rate = aluminium.custom_price
                    aluminium_quantity += float(aluminium.total_area)*float(typical_building)
                    alum_unit_qty = float(aluminium.area)*float(typical_building)
                    aluminium_quote_rate = (float(aluminium_unit_base_rate)*(float(aluminium_markup)/100))+float(aluminium_unit_base_rate)
                elif aluminium.pricing_unit == 2:
                    aluminium_unit_base_rate = aluminium.custom_price
                    aluminium_quantity += float(aluminium.total_quantity)*float(typical_building)
                    alum_unit_qty = 1*float(typical_building)
                    aluminium_quote_rate = (float(aluminium_unit_base_rate)*(float(aluminium_markup)/100))+float(aluminium_unit_base_rate)
                elif aluminium.pricing_unit == 3:
                    aluminium_unit_base_rate = aluminium.price_per_kg
                    aluminium_quantity += float(aluminium.total_weight)*float(typical_building)
                    alum_unit_qty = float(aluminium.weight_per_unit)*float(typical_building)
                    aluminium_quote_rate = (float(aluminium_unit_base_rate)*(float(aluminium_markup)/100))+float(aluminium_unit_base_rate)+float(aluminium_unit_surface)
                else:
                    aluminium_quantity += 0
                    alum_unit_qty = 0
                    aluminium_unit_base_rate = 0
                    aluminium_quote_rate = 0
            elif aluminium.aluminium_pricing == 1:
                if aluminium.al_price_per_unit:
                    aluminium_unit_base_rate = aluminium.al_price_per_unit
                    aluminium_quantity += float(aluminium.total_quantity)*float(typical_building)
                    alum_unit_qty = 1*float(typical_building)
                    aluminium_quote_rate = (float(aluminium_unit_base_rate)*(float(aluminium_markup)/100))+float(aluminium_unit_base_rate)
                elif aluminium.al_price_per_sqm:
                    aluminium_unit_base_rate = aluminium.al_price_per_sqm
                    aluminium_quantity += float(aluminium.total_area)*float(typical_building)
                    alum_unit_qty = float(aluminium.area)*float(typical_building)
                    aluminium_quote_rate = (float(aluminium_unit_base_rate)*(float(aluminium_markup)/100))+float(aluminium_unit_base_rate)
                elif aluminium.al_weight_per_unit:
                    aluminium_unit_base_rate = aluminium.price_per_kg
                    aluminium_quantity += float(aluminium.total_weight)*float(typical_building)
                    alum_unit_qty = float(aluminium.weight_per_unit)*float(typical_building)
                    aluminium_quote_rate = (float(aluminium_unit_base_rate)*(float(aluminium_markup)/100))+float(aluminium_unit_base_rate)+float(aluminium_unit_surface)
                else:
                    aluminium_quantity += 0
                    alum_unit_qty = 0
                    aluminium_unit_base_rate = 0
                    aluminium_quote_rate = 0
                
            total_product_quantity += float(aluminium.total_quantity)*float(typical_building)
            if product.deduction_method == 2 or product.deduction_method == 1:
                total_product_area += (float(aluminium.total_area) - (float(product.deducted_area)*float(aluminium.total_quantity)))*float(typical_building)
            else:
                total_product_area += float(aluminium.area) * float(aluminium.total_quantity)*float(typical_building)
            
            aluminium_quote_value += round(round(float(alum_unit_qty)*float(aluminium_quote_rate)*float(aluminium.total_quantity), 2), 2)
            
            
            if infill and infill.is_glass_cost:
                infill_base_rate = infill.glass_base_rate
                infill_markup = infill.glass_markup_percentage
                infill_area += float(infill.total_area_glass)*float(aluminium.total_quantity)*float(typical_building)
                infill_quote_rate = ((float(infill_base_rate)*float(infill_markup)/100)+float(infill_base_rate))
                infill_quote_value += (float(infill_quote_rate)*(float(infill.total_area_glass))*float(aluminium.total_quantity)*float(typical_building))
            
            sec_infill_quote_value = 0 
            if sec_infill:   
                for sec_infill_item in sec_infill:
                    sec_infill_quote_value += (((float(sec_infill_item.glass_base_rate)*(float(sec_infill_item.glass_markup_percentage)/100))+float(sec_infill_item.glass_base_rate))*float(sec_infill_item.total_area_glass)*float(aluminium.total_quantity)*float(typical_building))
        
            addon_price += (float(product.total_addon_cost))*float(aluminium.total_quantity)*float(typical_building)
        
            if product.is_accessory:
                accesory_price += round(float(product.accessory_total)*float(aluminium.total_quantity)*float(typical_building), 2)
            else:
                accesory_price += 0
            
            if sealant_data.is_silicon:
                sealant_price += round((float(sealant_data.silicon_quoted_price))*float(aluminium.total_quantity)*float(typical_building), 2)
            
            if product.is_tolerance:
                if product.tolerance_type == 1:
                    tolerance_price += ((float(alum_unit_qty)*float(aluminium_quote_rate)*float(aluminium.total_quantity))*float(product.tolerance)/100)*float(typical_building)
                    tolerance = ((float(alum_unit_qty)*float(aluminium_quote_rate)*float(aluminium.total_quantity))*float(product.tolerance)/100)*float(typical_building)
                else:
                    tolerance_price += float(product.tolerance)*float(aluminium.total_quantity)*float(typical_building)
                    tolerance = float(product.tolerance)*float(aluminium.total_quantity)*float(typical_building)
            else:
                tolerance = 0
                
            
            cost_of_materials = aluminium_quote_value+(infill_area*infill_quote_rate)+sec_infill_quote_value+sealant_price+accesory_price
            if pricing_option:
                alum_loh = (round(float(alum_unit_qty)*float(aluminium_quote_rate), 4)*float(aluminium.total_quantity))
                if infill and infill.is_glass_cost:
                    infill_loh = (infill_quote_rate*float(infill.total_area_glass)*float(aluminium.total_quantity)*float(typical_building))
                else:
                    infill_loh = 0
                sec_infill_quote_loh = (sec_infill_quote_value)
                if sealant_data.is_silicon:
                    sealant_price_loh = (float(sealant_data.silicon_quoted_price)*float(aluminium.total_quantity)*float(typical_building))
                else:
                    sealant_price_loh = 0
                    
                if product.is_accessory:
                    accesory_price_loh = (float(product.accessory_total)*float(aluminium.total_quantity)*float(typical_building))
                else:
                    accesory_price_loh = 0
                    
                cost_loh = (alum_loh+infill_loh+sec_infill_quote_loh+sealant_price_loh+accesory_price_loh)
                # cost_loh2 = math.ceil(alum_loh)+math.ceil(infill_loh)+math.ceil(sec_infill_quote_loh)+math.ceil(sealant_price_loh)+math.ceil(accesory_price_loh)
                cost_loh2 = (alum_loh)+(infill_loh)+(sec_infill_quote_loh)+(sealant_price_loh)+(accesory_price_loh)
                labour_price = (float((pricing_option.labour_perce)/100)*cost_loh)
                overhead_price = (float((pricing_option.overhead_perce)/100)*cost_loh)
                loh_percentage = float(pricing_option.labour_perce) + float(pricing_option.overhead_perce)
            
                
                loh += float(labour_price+overhead_price)
                
            # sub_total = (cost_loh2+math.ceil(labour_price)+math.ceil(overhead_price)+math.ceil(float(product.total_addon_cost)*float(aluminium.total_quantity)*float(typical_building))+tolerance)
            sub_total = (cost_loh2+(labour_price)+(overhead_price)+(float(product.total_addon_cost)*float(aluminium.total_quantity)*float(typical_building))+tolerance)
            
            unit_price = sub_total
            
            if not product.have_merge:
                if not product.after_deduction_price:
                    total_price += (unit_price)
                    rate_per_sqm = float(total_price)/float(total_product_area)
                else:
                    total_price += ((float(product.after_deduction_price)))*float(aluminium.total_quantity)
                    rate_per_sqm = total_price/total_product_area
            else:
                total_price += (unit_price)
                rate_per_sqm = float(total_price)/float(total_product_area)
        
    return {
        'aluminium_unit_base_rate': aluminium_unit_base_rate,
        'aluminium_markup': aluminium_markup,
        'aluminium_quantity': round(aluminium_quantity, 2),
        'aluminium_quote_rate': aluminium_quote_rate,
        'aluminium_quote_value': round(aluminium_quote_value, 2),
        "sealant_price": round(sealant_price, 2),
        'total_product_quantity': total_product_quantity,
        'area': round(area, 2),
        'aluminium_surface': aluminium_unit_surface,
        'infill_base_rate': infill_base_rate,
        'infill_markup': infill_markup,
        'infill_area': round(infill_area, 2),
        'infill_quote_rate': infill_quote_rate,
        'sec_infill': sec_infill,
        'accesory_price': round(accesory_price, 2),
        "tolerance_price": round(tolerance_price, 2),
        "loh": round(loh, 2),
        "addon_price": round(addon_price, 2), 
        "rate_per_sqm": round(rate_per_sqm, 2),
        'total_product_area': round(total_product_area, 2),
        # 'total_price': math.ceil(round(total_price, 2)),
        'total_price': (round(total_price, 2)),
        'product_uom': uom,
        'labour_percentage': labour_percentage,
        'overhead_percentage': overhead_percentage,
        'labour_flag':labour_flag,
        'overhead_flag':overhead_flag,
        'loh_percentage': round(loh_percentage, 2),
        'cost_of_materials': cost_of_materials,
    }