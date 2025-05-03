import math
from django import template
from apps.enquiries.models import Estimations, Temp_Estimations
from apps.estimations.models import (
        EstimationMainProductMergeData, 
        EstimationProduct_Associated_Data, 
        MainProductAccessories, 
        MainProductAluminium, 
        MainProductGlass, 
        MainProductAddonCost, 
        EstimationMainProduct, 
        MainProductSilicon,
        PricingOption, 
        Temp_EstimationMainProduct, 
        Temp_EstimationMainProductMergeData, 
        Temp_EstimationProduct_Associated_Data, 
        Temp_MainProductAccessories, 
        Temp_MainProductAddonCost, 
        Temp_MainProductAluminium, 
        Temp_MainProductGlass, 
        Temp_MainProductSilicon, 
        Temp_PricingOption
)

from apps.estimations.templatetags.assocciated_data import have_deducted_associated

register = template.Library()


@register.simple_tag
def material_summary_data(request, pk, flag=None):
    """
    This function calculates the total cost of materials, labour, overhead, and tolerance for a given
    estimation project.
    
    :param request: The HTTP request object containing metadata about the current request
    :param pk: The primary key of an Estimation object, used to retrieve related MainProduct objects for
    calculating material summary data
    :return: a dictionary object named 'data' which contains various key-value pairs representing the
    total cost of different materials and services involved in a construction project. These include the
    total cost of aluminium, glass, silicon, addons, accessories, labour, overhead, and tolerance. The
    'overall_total' key represents the final cost of the project.
    """
    alumin_total = 0
    total_addon_cost = 0
    total_access_price = 0
    addon_cost = 0
    access_price = 0
    unit_price1 = 0
    total_labour = 0
    total_overhead = 0
    total_tolarance = 0
    overall_total = 0
    unit_price = 0
    glass_total1 = 0
    glass_total = 0
    sec_glass_total1 = 0
    sec_glass_total = 0
    galss_price = 0
    galss_price1 = 0
    tolarance_price = 0
    silicon_total = 0
    silicon_price = 0
    silicon_price1 = 0
    tolarance_unit_total = 0
    silicon_total1 = 0
    material_total_total = 0
    total_price = 0
    price = []
    unit_total = 0
    final_price = 0
    unit_labour = 0
    unit_overhead = 0
    merge_total = 0
    
    # de_alumin_total = 0
    # de_total_addon_cost = 0
    # de_total_access_price = 0
    # de_addon_cost = 0
    # de_access_price = 0
    # de_unit_price1 = 0
    # de_total_labour = 0
    # de_total_overhead = 0
    # de_total_tolarance = 0
    # de_overall_total = 0
    # de_unit_price = 0
    # de_glass_total1 = 0
    # de_glass_total = 0
    # de_sec_glass_total1 = 0
    # de_sec_glass_total = 0
    # de_galss_price = 0
    # de_galss_price1 = 0
    # de_tolarance_price = 0
    # de_silicon_total = 0
    # de_silicon_price = 0
    # de_silicon_price1 = 0
    # de_tolarance_unit_total = 0
    # de_silicon_total1 = 0
    # de_material_total_total = 0
    # de_total_price = 0
    # de_price = []
    # de_unit_total = 0
    # de_final_price = 0
    # de_unit_labour = 0
    # de_unit_overhead = 0
    # de_merge_total = 0
    
    quantity = []
    de_quantity = []
    PATHS = [
                '/Estimation/estimation_summary/',
                '/Estimation/material_summary_data/',
                '/Enquiries/product_category_summary/',
                '/Enquiries/open_enquiry/',
                '/Estimation/view_revision_history/',
            ]
                
    if any(path in request.path for path in PATHS):
        MainProduct = EstimationMainProduct
        AluminiumModel = MainProductAluminium
        MainProductGlassModel = MainProductGlass
        PricingOptionModel = PricingOption
        MainProductSiliconModel = MainProductSilicon
        # AssociatedProduct = EstimationProduct_Associated_Data
        if flag:
            MainProduct = Temp_EstimationMainProduct
            AluminiumModel = Temp_MainProductAluminium
            MainProductGlassModel = Temp_MainProductGlass
            PricingOptionModel = Temp_PricingOption
            MainProductSiliconModel = Temp_MainProductSilicon
        
    else:
        
        MainProduct = Temp_EstimationMainProduct
        AluminiumModel = Temp_MainProductAluminium
        MainProductGlassModel = Temp_MainProductGlass
        PricingOptionModel = Temp_PricingOption
        MainProductSiliconModel = Temp_MainProductSilicon
        # AssociatedProduct = Temp_EstimationProduct_Associated_Data
        
    try:
        main_products = MainProduct.objects.select_related('building').filter(building__estimation=pk, disabled=False).order_by('id')
        # associated_product_objs = [associ.associated_product.id for associ in AssociatedProduct.objects.filter(associated_product__building__estimation=pk, is_deducted=True)]
        # deducted_products = MainProduct.objects.select_related('building').filter(pk__in=associated_product_objs).order_by('id')
        
    except:
        main_products = None
        # deducted_products = None
    
    if main_products:
        for main_product in main_products:
            unit_total = 0
            try:
                aluminium_obj = AluminiumModel.objects.get(estimation_product=main_product.id)
            except Exception as e:
                aluminium_obj = None
                
            
            try:
                glass_obj = MainProductGlassModel.objects.get(estimation_product=main_product.id, glass_primary=True)
                second_glass_obj = MainProductGlassModel.objects.select_related('estimation_product').filter(estimation_product=main_product.id, glass_primary=False)
            except:
                glass_obj = None
                second_glass_obj = None
            try:
                silicon_obj = MainProductSiliconModel.objects.get(estimation_product=main_product.id)
            except:
                silicon_obj = None
            try:
                pricing_control = PricingOptionModel.objects.get(estimation_product=main_product.id)
            except Exception as e:
                pricing_control = None
                
            if main_product.building.typical_buildings_enabled:
                typical_building_number = main_product.building.no_typical_buildings
            else:
                typical_building_number = 1

            if aluminium_obj.al_quoted_price:
                unit_price1 = float(aluminium_obj.al_quoted_price)
                unit_price = float(aluminium_obj.al_quoted_price)*float(aluminium_obj.total_quantity)*float(typical_building_number)
            else:
                unit_price = 0
                unit_price1 = 0
            
            alumin_total += unit_price

            if glass_obj:
                if glass_obj.is_glass_cost:
                    if glass_obj.glass_quoted_price:
                        glass_total1 = float(glass_obj.glass_quoted_price)
                        glass_total = float((glass_total1))*float(aluminium_obj.total_quantity)*float(typical_building_number)
                    else:
                        glass_total1 = 0
                        glass_total = 0
                else:
                    glass_total1 = 0
                    glass_total = 0
            else:
                glass_total1 = 0
                glass_total = 0

            if second_glass_obj:
                sec_glass_total1 = 0
                for second_glass in second_glass_obj:
                    sec_glass_totals = float(second_glass.glass_quoted_price)
                    sec_glass_total1 += sec_glass_totals
                sec_glass_total = float((sec_glass_total1))*float(aluminium_obj.total_quantity)*float(typical_building_number)
            else:
                sec_glass_totals = 0
                sec_glass_total1 = 0
                sec_glass_total = 0
                
            galss_price1 = float(float(glass_total1) + float(sec_glass_total1))
            
            galss_price += float(float(glass_total) + float(sec_glass_total))
        
            
            if silicon_obj:
                if silicon_obj.is_silicon:
                    silicon_total1 = float(silicon_obj.silicon_quoted_price)
                    silicon_total = float((silicon_total1))*float(aluminium_obj.total_quantity)*float(typical_building_number)
                else:
                    silicon_total1 = 0
                    silicon_total = 0
            else:
                silicon_total1 = 0
                silicon_total = 0
            silicon_price1 = float(silicon_total)
            silicon_price += float(silicon_total)
            
            if main_product:
                if main_product.enable_addons:
                    total_addon_cost = float((main_product.total_addon_cost))*float(aluminium_obj.total_quantity)*float(typical_building_number)
                else:
                    total_addon_cost = 0
                if main_product.accessory_total and main_product.is_accessory:
                    total_access_price = (float(main_product.accessory_total))*float(aluminium_obj.total_quantity)*float(typical_building_number)
                else:
                    total_access_price = 0
                    
                addon_cost += total_addon_cost
                access_price += total_access_price

            if main_product.accessory_total and main_product.is_accessory:
                
                material_total = float(math.ceil(unit_price1 + galss_price1 + silicon_total1 + float(main_product.accessory_total)))*float(aluminium_obj.total_quantity) 
                unit_total = float(unit_price1 + galss_price1 + silicon_total1) + float(main_product.accessory_total)
            else:
                material_total = float(math.ceil(unit_price1 + galss_price1 + silicon_total1)*float(aluminium_obj.total_quantity)*float(typical_building_number))
                unit_total = float(unit_price1 + galss_price1 + silicon_total1) 
                
            if pricing_control.labour_perce:
                labour_percentage = float(pricing_control.labour_perce) / 100
                labour_percent_price = round(float(material_total) * float(labour_percentage), 4)
                # labour_percent_price = float(math.ceil(material_total)) * float(labour_percentage)
                sub_total = float(math.ceil(material_total)) + float(labour_percent_price)
                unit_labour = ((float((unit_total)) * float(labour_percentage)))
            else:
                labour_percent_price = 0
                unit_labour = 0
                
            total_labour += float(labour_percent_price)
            if pricing_control.overhead_perce:
                overhead_percentage = float(pricing_control.overhead_perce) / 100
                overhead_percent_price = round(float(material_total) * float(overhead_percentage), 4)
                # overhead_percent_price = float(math.ceil(material_total)) * float(overhead_percentage)
                sub_total += (overhead_percent_price)  
                unit_overhead = ((float((unit_total)) * float(overhead_percentage)))
            else:
                overhead_percent_price = 0
                unit_overhead = 0
        
            total_overhead += float(overhead_percent_price)
            if aluminium_obj.aluminium_pricing == 1 or aluminium_obj.aluminium_pricing == 2 or aluminium_obj.aluminium_pricing == 4:
                if main_product.is_tolerance:
                    if main_product.tolerance_type == 1:
                        tolarance = int(main_product.tolerance) / 100
                        tolarance_price = float(math.ceil(aluminium_obj.al_quoted_price)) * tolarance
                    elif main_product.tolerance_type == 2:
                        tolarance_price = float(main_product.tolerance)*float(aluminium_obj.total_quantity)*float(typical_building_number)
                    else:
                        tolarance_price = 0
                        tolarance_unit_total = 0
                        
                    tolarance_unit_total = (float(tolarance_price)*float(aluminium_obj.total_quantity)*float(typical_building_number))
                else:
                    tolarance_unit_total = 0
                    tolarance_price = 0
            else:
                tolarance_unit_total = 0
                tolarance_price = 0
                unit_total += 0
            total_tolarance += tolarance_unit_total
            
            if main_product.have_merge:
                merge_total += (float(main_product.merge_price))
                quantity.append(float(aluminium_obj.total_quantity)*float(typical_building_number))
                price.append(float(main_product.merge_price))
                
            else:
                if main_product.product_type == 2:
                    if not main_product.main_product.have_merge:
                        quantity.append(float(aluminium_obj.total_quantity)*float(typical_building_number))
                        if main_product.after_deduction_price:
                            price.append((float(main_product.after_deduction_price))/(float(aluminium_obj.total_quantity)*float(typical_building_number)))
                        else: 
                            price.append((float(unit_total)+float(unit_labour)+float(unit_overhead)+float(main_product.total_addon_cost)+float(tolarance_price)))
                    else:
                        quantity.append(0)
                        price.append(0)
                else:
                    if main_product.main_product.have_merge:
                        quantity.append(0)
                        price.append(0)
                    else:
                        quantity.append(float(aluminium_obj.total_quantity)*float(typical_building_number))
                        if main_product.after_deduction_price:
                            price.append((float(main_product.after_deduction_price)))
                        else:
                            price.append((float(unit_total)+float(unit_labour)+float(unit_overhead)+float(main_product.total_addon_cost)+float(tolarance_price)))
                
            if not main_product.have_merge:
                if not main_product.after_deduction_price:
                    overall_total = (float(alumin_total)+float(galss_price)+float(silicon_price)+float(addon_cost)+float(access_price)+float(total_labour)+float(total_overhead)+float(total_tolarance))
                    # round_overall_total = math.ceil(overall_total)
                else:
                    overall_total = overall_total
                    # round_overall_total = math.ceil(overall_total)
            else:
                overall_total = float(main_product.merge_price)*float(aluminium_obj.quantity)
                # round_overall_total = math.ceil(overall_total)
        
        price = [math.ceil(round(x, 2)) for x in price]
        for i in range(len(price)):
            final_price += math.ceil((price[i])*float(quantity[i]))
    
    
    data = {
        'alumin_total': float(alumin_total),
        'glass_total': float(galss_price),
        'silicon_total': float(silicon_price),
        'addon_cost': float(addon_cost),
        'access_price': float(access_price),
        'overall_total': float(final_price),
        'total_labour': float(total_labour),
        'total_overhead': float(total_overhead),
        'total_tolarance': float(total_tolarance),
        # 'round_overall_total': float(alumin_total)+float(galss_price)+float(silicon_price)+float(addon_cost)+float(access_price)+float(total_labour)+float(total_overhead)+float(total_tolarance),
        'round_overall_total': float(final_price),
        
        # 'de_alumin_total': float(de_alumin_total),
        # 'de_glass_total': float(de_galss_price),
        # 'de_silicon_total': float(de_silicon_price),
        # 'de_addon_cost': float(de_addon_cost),
        # 'de_access_price': float(de_access_price),
        # 'de_overall_total': float(de_final_price),
        # 'de_total_labour': float(de_total_labour),
        # 'de_total_overhead': float(de_total_overhead),
        # 'de_total_tolarance': float(de_total_tolarance),
        # 'de_round_overall_total': float(de_final_price),
    }
    return data


@register.simple_tag
def deducted_consolidate_summary(request, pk):
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
            '/Estimation/building_price_print/',
            '/Estimation/scope_view/', 
            '/Estimation/scope_with_material/',
            '/Estimation/estimation_product_delete/',
            '/Project/import_from_scope/',
            '/Estimation/deduction_material_summary/',
            '/Estimation/material_summary_data/',
        ]
    
    if any(path in request.path for path in PATHS):
        Estimation = Estimations
        EstimationMainProductModel = EstimationMainProduct
    else:
        Estimation = Temp_Estimations
        EstimationMainProductModel = Temp_EstimationMainProduct

    estimation_obj = Estimation.objects.get(pk=pk)
    products_objs = EstimationMainProductModel.objects.filter(building__estimation=estimation_obj, disabled=False)
    
    alumin_price = 0
    infill_price = 0
    sealant_price = 0
    accessories_price = 0
    addons_price = 0
    subtotal_price = 0
    labour_price = 0
    overhead_price = 0
    tolerance_price = 0
    total_price = 0
    
    for product in products_objs:
        # print("product==>", product)
        data = have_deducted_associated(request=request, pk=product.id)
        alumin_price += data['new_alumn'] 
        infill_price += data['new_infill'] 
        sealant_price += data['new_sealant'] 
        accessories_price += data['new_accessories'] 
        addons_price += data['addons_price'] 
        subtotal_price += data['new_sub_total'] 
        labour_price += data['new_labour'] 
        overhead_price += data['new_overhead'] 
        tolerance_price += data['tolarance_price']
        
        if data['new_total_price']:
            total_price += data['new_total_price'] 
    
    context = {
        "alumin_price": alumin_price,
        "infill_price": infill_price,
        "sealant_price": sealant_price,
        "accessories_price": accessories_price,
        "addons_price": addons_price,
        "subtotal_price": subtotal_price,
        "labour_price": labour_price,
        "overhead_price": overhead_price,
        "total_price": total_price,
        "tolerance_price": tolerance_price,
    }
    
    return context
    
