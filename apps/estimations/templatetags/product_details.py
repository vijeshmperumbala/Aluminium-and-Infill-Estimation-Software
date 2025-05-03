

from django import template
import math
from apps.estimations.models import (
    EstimationMainProductMergeData,
    MainProductAluminium,
    MainProductGlass,
    MainProductAddonCost,
    EstimationMainProduct,
    MainProductSilicon,
    PricingOption,
    Temp_EstimationMainProduct,
    Temp_EstimationMainProductMergeData,
    Temp_MainProductAluminium,
    Temp_MainProductGlass,
    Temp_MainProductSilicon,
    Temp_PricingOption
)

register = template.Library()

DETAILS_URLS = [
    '/Estimation/estimation_pricing_summary/',
    '/Estimation/estimation_list_enquiry/',
    '/Estimation/estimation_list_by_boq_enquiry/',
    '/Project/project_scop/',
    '/Project/project_budgeting/',
    '/Project/project_accounts/',
    '/Estimation/building_category_summary/',
    '/Estimation/export_csv_estimation_socpe/',
    '/Estimation/export_csv_estimation_socpe_boq/',
    '/Project/project_contract_items/',
    '/Project/proccess_quotation/',
    '/Project/update_quotation_item/',
    '/Project/add_eps_item/',
    '/Project/create_eps/',
    '/Estimation/building_price_print/',
    '/Estimation/edit_estimation_pricing/',
    '/Estimation/update_pricing_summary/',
    '/Estimation/scope_view/',
    '/Estimation/scope_with_material/',
    '/Project/create_glass_eps/',
    '/Project/eps_collaps_data/',
    '/Project/glass_eps_collaps_data/',
    '/Project/import_from_scope/',
    '/Estimation/disable_products/',
    '/Estimation/disabled_scope_view/',
]


@register.simple_tag
def product_details(request, pk):
    main_product = None
    aluminium_obj = None
    glass_obj = None
    second_glass_obj = None
    silicon_obj = None
    pricing_control = None
    try:
        if any(path in request.path for path in DETAILS_URLS):
            MainProduct = EstimationMainProduct
            AluminiumModel = MainProductAluminium
            MainProductGlassModel = MainProductGlass
            PricingOptionModel = PricingOption
            MainProductSiliconModel = MainProductSilicon
        else:
            MainProduct = Temp_EstimationMainProduct
            AluminiumModel = Temp_MainProductAluminium
            MainProductGlassModel = Temp_MainProductGlass
            PricingOptionModel = Temp_PricingOption
            MainProductSiliconModel = Temp_MainProductSilicon


        main_product = MainProduct.objects.get(pk=pk)
        aluminium_obj = AluminiumModel.objects.get(estimation_product=pk)
        try:
            glass_obj = MainProductGlassModel.objects.get(estimation_product=pk, glass_primary=True)
        except Exception as e:
            glass_obj = None
        second_glass_obj = MainProductGlassModel.objects.select_related('estimation_product').filter(estimation_product=pk, glass_primary=False)
        try:
            silicon_obj = MainProductSiliconModel.objects.get(estimation_product=pk)
        except Exception as e:
            silicon_obj = None
        try:
            pricing_control = PricingOptionModel.objects.get(estimation_product=pk)
        except Exception as e:
            print('EXC==>', e)

    except (EstimationMainProduct.DoesNotExist,
            MainProductAluminium.DoesNotExist,
            MainProductGlass.DoesNotExist,
            MainProductSilicon.DoesNotExist,
            PricingOption.DoesNotExist,
            Temp_EstimationMainProduct.DoesNotExist,
            Temp_MainProductAluminium.DoesNotExist,
            Temp_MainProductGlass.DoesNotExist,
            Temp_MainProductSilicon.DoesNotExist,
            Temp_PricingOption.DoesNotExist) as e:
        print('EXCE==>', e)
        ...

    unit_price = 0
    labour_percentage = 0
    labour_percent_price = 0
    overhead_percentage = 0
    overhead_percent_price = 0
    unit_total_price = 0
    tolarance = 0
    tolarance_price = 0
    estimated_value = 0
    total_price = 0
    quantity = 0
    unit_area = 0
    total_area = 0
    dimension = 0
    aluminium_price = None
    infill_price = None
    sealant_price = None
    if aluminium_obj and main_product.category.handrail:
        dimension = str(int(aluminium_obj.width))
    elif aluminium_obj:
        dimension = str(int(aluminium_obj.width)) + '*' + str(int(aluminium_obj.height))
    quantity = aluminium_obj.total_quantity
    
    if main_product.have_merge and main_product.deduction_method == 3:
        unit_area = float(aluminium_obj.area)
        estimated_value = float(main_product.merge_price) 
    else:
        if main_product.deduction_method == 2:
            deducted_area = float(aluminium_obj.area) - float(main_product.deducted_area)
            unit_area = deducted_area
        else:
            unit_area = float(aluminium_obj.area)
            
        unit_price = 0
        if aluminium_obj.al_quoted_price:
            unit_price += float(aluminium_obj.al_quoted_price)
            aluminium_price = float(aluminium_obj.al_quoted_price)
        if glass_obj and glass_obj.is_glass_cost and glass_obj.glass_quoted_price:
            unit_price += float(glass_obj.glass_quoted_price)
            infill_price = float(glass_obj.glass_quoted_price)
        if second_glass_obj:
            for second_glass in second_glass_obj:
                if second_glass.glass_quoted_price:
                    unit_price += float(second_glass.glass_quoted_price)
        if silicon_obj and silicon_obj.is_silicon:
            unit_price += float(silicon_obj.silicon_quoted_price)
            sealant_price = float(silicon_obj.silicon_quoted_price)
            
        if main_product.is_accessory and main_product.accessory_total:
            unit_price += float(main_product.accessory_total)
        labour_percent_price = 0
        overhead_percent_price = 0
        tolarance_price = 0


        if pricing_control:
            if pricing_control.labour_perce:
                labour_percentage = float(pricing_control.labour_perce) / 100
                labour_percent_price = round(float(unit_price) * float(labour_percentage), 4)
            if pricing_control.overhead_perce:
                overhead_percentage = float(pricing_control.overhead_perce) / 100
                overhead_percent_price = round(float(unit_price) * float(overhead_percentage), 4)
                
        if aluminium_obj.aluminium_pricing in [1, 2, 4] and main_product.is_tolerance:
            if main_product.tolerance_type == 1: # percentage
                tolarance = int(main_product.tolerance) / 100
                tolarance_price = float(aluminium_obj.al_quoted_price) * tolarance
            elif main_product.tolerance_type == 2:
                tolarance_price = float(main_product.tolerance)
        estimated_values = float(unit_price) + float(overhead_percent_price) + float(labour_percent_price) + float(tolarance_price) + float(main_product.total_addon_cost)
        # estimated_value = float(main_product.after_deduction_price)+float(main_product.total_addon_cost) if main_product.after_deduction_price else math.ceil(estimated_values)
        estimated_value = float(main_product.after_deduction_price) if main_product.after_deduction_price else round(estimated_values, 2)
    total_area = float(unit_area) * float(quantity)
    total_price = round(math.ceil(float(estimated_value) * int(quantity)), 2)
    round_total_price = math.ceil(total_price)
    
    try:
        rp_sqm = total_price / total_area
    except Exception:
        rp_sqm = 0
    
    data = {
        'dimension': dimension,
        'unit_area': float(unit_area),
        'quantity': float(quantity),
        'total_area': total_area,
        'unit_price': estimated_value,
        'round_unit_price': float(math.ceil(estimated_value)),
        'total_price': float(estimated_value)*float(quantity),
        # 'round_total_price': round_total_price,
        'round_total_price': float(math.ceil(estimated_value))*float(quantity),
        'main_pro': main_product,
        'rp_sqm': round(float(estimated_value)/float(unit_area), 2),
        # "rp_sqm": rp_sqm,
        "aluminium_price": aluminium_price,
        "infill_price": infill_price,
        "sealant_price": sealant_price,
    }
    return data