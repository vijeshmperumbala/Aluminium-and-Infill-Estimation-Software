import math
from django import template

from apps.estimations.models import (
            EstimationMainProduct, 
            EstimationProduct_Associated_Data,
            MainProductAccessories,
            MainProductAddonCost,
            MainProductAluminium,
            MainProductGlass,
            MainProductSilicon,
            PricingOption, 
            Temp_EstimationMainProduct, 
            Temp_EstimationProduct_Associated_Data,
            Temp_MainProductAccessories,
            Temp_MainProductAddonCost,
            Temp_MainProductAluminium,
            Temp_MainProductGlass,
            Temp_MainProductSilicon,
            Temp_PricingOption
)
from apps.helper import round_half_even

register = template.Library()


@register.simple_tag
def assocciated_data(request, pk):
    """
    The function returns associated data based on the request path and primary key.
    
    :param request: The HTTP request object that contains information about the current request, such as
    the path and any data submitted with the request
    :param pk: pk is a parameter that represents the primary key of a model instance. It is used to
    retrieve a specific instance from the database. In this code, it is used to filter the
    EstimationMainProduct or Temp_EstimationMainProduct objects based on their main_product and
    product_type fields
    :return: a queryset of EstimationMainProduct or Temp_EstimationMainProduct objects depending on the
    condition in the if-else statement. The queryset is filtered based on the value of the pk parameter
    and the product_type attribute of the objects.
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
                '/Estimation/building_price_print/',
                '/Estimation/scope_view/', 
                '/Estimation/scope_with_material/',
                '/Estimation/estimation_product_delete/',
                '/Project/import_from_scope/',
             ]
    if any(path in request.path for path in PATHS):
        assocciated_data = EstimationMainProduct.objects.filter(main_product=pk, product_type=2, disabled=False)
    else:
        assocciated_data = Temp_EstimationMainProduct.objects.filter(main_product=pk, product_type=2, disabled=False)
        
    return assocciated_data


# @register.simple_tag
# def have_deducted_associated(request, pk):
#     PATHS = [
#             '/Estimation/edit_estimation_pricing/',
#             '/Estimation/view_side_summary/',
#             '/Estimation/estimation_list_enquiry/',
#             '/Estimation/estimation_list_by_boq_enquiry/',
#             '/Estimation/export_csv_estimation_socpe/',
#             '/Enquiries/product_category_summary/',
#             '/Estimation/merge_summary_print_2/',
#             '/Estimation/merge_summary_print/',
#             '/Estimation/export_category_summary_building/',
#             '/Estimation/export_category_summary/',
#             '/Estimation/export_category_summary_boq/',
#             '/Estimation/estimation_quotations_list/',
#             '/Enquiries/view_quotations/',
#             '/Estimation/quotation_print_by_customer/',
#             '/Estimation/quotation_print_by_customer_boq/',
#             '/Estimation/quotation_print_boq/',
#             '/Estimation/quotation_print/',
#             '/Enquiries/edit_quotation/', 
#             '/Enquiries/create_quotation_base/',
#             '/Estimation/building_price_print/',
#             '/Estimation/scope_view/', 
#             '/Estimation/scope_with_material/',
#             '/Estimation/estimation_product_delete/',
#             '/Project/import_from_scope/',
#             '/Estimation/deduction_material_summary/',
#             '/Estimation/material_summary_data/',
            
#             '/Estimation/add_estimation_pricing/',
#             '/Enquiries/product_duplicate/',
#             '/Enquiries/edit_enq_specifications/',
#             '/Enquiries/building_duplicate/',
#             '/Estimation/add_associated_product/',
#             '/Estimation/add_typical_buildings/',
#             '/Estimation/typical_togle_update/',
#             '/Estimation/consolidate_aluminium_update/',
#             '/Estimation/consolidate_price_update/',
#             '/Estimation/consolidate_addon_update/',
#             '/Estimation/consolidate_sealant_update/',
#             '/Estimation/consolidate_loh_update/',
#             '/Estimation/consolidate_unitprice_update/',
#             '/Estimation/merge_summary_update_spec/',
#             '/Estimation/merge_summary_update/',
#             '/Estimation/reset_merge/',
#             '/Estimation/product_merge/',
#             '/Estimation/sync_associated_data_full/',
#             '/Estimation/building_delete/',
#             '/Estimation/reset_sync_data/',
#             '/Estimation/disable_products/',
#         ]

#     if any(path in request.path for path in PATHS):
#         EstimationMainProductModel = EstimationMainProduct
#         MainProductAluminiumModel = MainProductAluminium
#         MainProductGlassModel = MainProductGlass
#         MainProductSiliconModel = MainProductSilicon
#         PricingOptionModel = PricingOption
#         MainProductAddonCostModel = MainProductAddonCost
#         MainProductAccessoriesModel = MainProductAccessories
#         AssociatedProduct = EstimationProduct_Associated_Data
        
#     else:
#         EstimationMainProductModel = Temp_EstimationMainProduct
#         MainProductAluminiumModel = Temp_MainProductAluminium
#         MainProductGlassModel = Temp_MainProductGlass
#         MainProductSiliconModel = Temp_MainProductSilicon
#         PricingOptionModel = Temp_PricingOption
#         MainProductAddonCostModel = Temp_MainProductAddonCost
#         MainProductAccessoriesModel = Temp_MainProductAccessories
#         AssociatedProduct = Temp_EstimationProduct_Associated_Data

#     try:
#         product_obj = EstimationMainProductModel.objects.get(pk=pk)
#     except Exception:
#         product_obj = None
    
#     if product_obj:
#         assocciated_data = EstimationMainProductModel.objects.filter(main_product__in=[associated.estimation_main_product.id for associated in AssociatedProduct.objects.filter(estimation_main_product=product_obj, is_deducted=True)], product_type=2)
#     else:
#         assocciated_data = None
    
#     main_aluminium_price = 0
#     main_aluminium_price_2 = 0
    
#     main_glass_price = 0
#     main_glass_price_2 = 0
    
#     main_accessory_price = 0
#     main_accessory_price_2 = 0
    
#     main_sealant_price = 0
#     main_sealant_price_2 = 0
    
#     overhead_perce = 0
#     labour_perce = 0
#     addons_price = 0
#     tolarance_price = 0
#     tolarance_price_2 = 0
#     quantity = 0
#     aluminium_price = 0
#     glass_price = 0
#     sealant_price = 0
#     assocciated_area = 0
#     main_area = 0
#     deducted_area = 1
    
#     # Main Product Calculations
#     if product_obj:
#         try:
#             main_aluminium_obj = MainProductAluminiumModel.objects.get(estimation_product=product_obj.id)
#         except Exception:
#             main_aluminium_obj = None
#         try:
#             main_glass_obj = MainProductGlassModel.objects.get(estimation_product=product_obj.id, glass_primary=True)
#             main_second_glass_obj = MainProductGlassModel.objects.select_related('estimation_product').filter(estimation_product=product_obj.id, glass_primary=False)
#         except Exception:
#             main_glass_obj = None
#             main_second_glass_obj = None
        
#         try:
#             main_silicon_obj = MainProductSiliconModel.objects.get(estimation_product=product_obj.id)
#         except Exception:
#             main_silicon_obj = None
            
#         main_addons = MainProductAddonCostModel.objects.select_related('estimation_product').filter(estimation_product=product_obj.id)
        
#         try:
#             main_pricing_control = PricingOptionModel.objects.get(estimation_product=product_obj.id)
#         except Exception as e:
#             main_pricing_control = None
            
#         if product_obj.building.typical_buildings_enabled:
#             typical_building_number = product_obj.building.no_typical_buildings
#         else:
#             typical_building_number = 1
        
#         main_area = float(main_aluminium_obj.total_area)
#         quantity = float(main_aluminium_obj.total_quantity)*float(typical_building_number)
        
#         if product_obj.deduction_method == 2:
#             deducted_area = float(main_aluminium_obj.area) - float(product_obj.deducted_area)
#         else:
#             deducted_area = float(main_aluminium_obj.total_area)
        
#         if main_second_glass_obj:
#             for sec_glass in main_second_glass_obj:
#                 main_glass_price += float(sec_glass.glass_quoted_price) * float(main_aluminium_obj.total_quantity)*float(typical_building_number)
#                 main_glass_price_2 += float(sec_glass.glass_quoted_price) #* float(main_aluminium_obj.total_quantity)*float(typical_building_number)
                
#         if main_glass_obj and main_glass_obj.is_glass_cost and main_glass_obj.glass_quoted_price:
#             main_glass_price += float(main_glass_obj.glass_quoted_price) * float(main_aluminium_obj.total_quantity)*float(typical_building_number)
#             main_glass_price_2 += float(main_glass_obj.glass_quoted_price) #* float(main_aluminium_obj.total_quantity)*float(typical_building_number)
        
#         if main_aluminium_obj.al_quoted_price:
#             main_aluminium_price += float(main_aluminium_obj.al_quoted_price) * float(main_aluminium_obj.total_quantity)*float(typical_building_number)
#             main_aluminium_price_2 += float(main_aluminium_obj.al_quoted_price) #* float(main_aluminium_obj.total_quantity)*float(typical_building_number)
#         if product_obj.accessory_total and (product_obj.accessory_total and product_obj.is_accessory):
#             main_accessory_price += float(product_obj.accessory_total) * float(main_aluminium_obj.total_quantity)*float(typical_building_number)
#             main_accessory_price_2 += float(product_obj.accessory_total) #* float(main_aluminium_obj.total_quantity)*float(typical_building_number)
        
#         if main_silicon_obj and main_silicon_obj.is_silicon:
#             main_sealant_price += float(main_silicon_obj.silicon_quoted_price) * float(main_aluminium_obj.total_quantity)*float(typical_building_number)
#             main_sealant_price_2 += float(main_silicon_obj.silicon_quoted_price) #* float(main_aluminium_obj.total_quantity)*float(typical_building_number)
        
#         if main_aluminium_obj.aluminium_pricing in [1, 2, 4] and product_obj.is_tolerance:
#             if product_obj.tolerance_type == 1: # percentage
#                 tolarance = int(product_obj.tolerance) / 100
#                 tolarance_price = float(float(main_aluminium_obj.al_quoted_price) * tolarance) * float(main_aluminium_obj.total_quantity)*float(typical_building_number)
#                 tolarance_price_2 = float(float(main_aluminium_obj.al_quoted_price) * tolarance) #* float(main_aluminium_obj.total_quantity)*float(typical_building_number)
#             elif product_obj.tolerance_type == 2:
#                 tolarance_price = float(float(product_obj.tolerance)) * float(main_aluminium_obj.total_quantity)*float(typical_building_number)
#                 tolarance_price_2 = float(float(product_obj.tolerance)) #* float(main_aluminium_obj.total_quantity)*float(typical_building_number)
#             else:
#                 tolarance_price = 0
#                 tolarance_price_2 = 0
                
#         overhead_perce = main_pricing_control.overhead_perce
#         labour_perce = main_pricing_control.labour_perce
#         addons_price = float(product_obj.total_addon_cost) * float(main_aluminium_obj.total_quantity)*float(typical_building_number)
#         addons_price_2 = float(product_obj.total_addon_cost) #*float(main_aluminium_obj.total_quantity)*float(typical_building_number)
        
#     # Assocciated Product Calculations
#     if assocciated_data:
#         for assocciated_product in assocciated_data:
#             try:
#                 aluminium_obj = MainProductAluminiumModel.objects.get(estimation_product=assocciated_product.id)
#             except Exception:
#                 aluminium_obj = None
    
#             assocciated_area += aluminium_obj.total_area
        
#     cost_of_material = main_aluminium_price_2 + main_glass_price_2 + main_accessory_price_2 + main_sealant_price_2
    
#     # print("main_aluminium_price==>", main_aluminium_price)
#     overhead_price = (float(overhead_perce/100)*float(cost_of_material)) #* float(main_aluminium_obj.total_quantity) * float(typical_building_number) 
#     labour_price =  (float(labour_perce/100)*float(cost_of_material)) #* float(main_aluminium_obj.total_quantity) * float(typical_building_number)
    
#     actual_total = math.ceil(round(cost_of_material + overhead_price + labour_price +  tolarance_price_2 + addons_price_2, 2)) \
#                     * float(main_aluminium_obj.total_quantity) * float(typical_building_number) 
    
#     sqm_alum_price = round((float(main_aluminium_price)/float(main_area))*float(assocciated_area), 2)
#     sqm_glass_price = round((float(main_glass_price)/float(main_area))*float(assocciated_area), 2)
#     sqm_main_sealant_price = round((float(main_sealant_price)/float(main_area))*float(assocciated_area), 2)
#     sqm_main_accessories_price = round((float(main_accessory_price)/float(main_area))*float(assocciated_area), 2)
    
#     new_alumn = (float(main_aluminium_price) - float(sqm_alum_price))
#     new_infill = (float(main_glass_price) - float(sqm_glass_price))
#     new_sealant = (float(main_sealant_price) - float(sqm_main_sealant_price))
#     new_accessories = (float(main_accessory_price) - float(sqm_main_accessories_price))
    
#     new_com = round(float(new_alumn) + float(new_infill) + float(new_sealant) + float(new_accessories), 2)
    
#     new_overhead = ((float(overhead_perce)/100)*float(new_com))
#     new_labour = ((float(labour_perce)/100)*float(new_com))
    
#     # new_sub_total = math.ceil(round(float(new_com) + float(new_overhead) + float(new_labour), 2))
    
#     new_sub_total = float(new_com) + float(new_overhead) + float(new_labour)
#     # new_sub_total = round_half_even(float(new_com) + float(new_overhead) + float(new_labour))
#     new_sqm_price = round(float(new_sub_total)/float(deducted_area), 2)
        
#     # new_unit_price = round_half_even((float(new_sub_total) + float(addons_price) + float(tolarance_price))/float(quantity))
    
#     new_unit_price = math.ceil(round((float(new_sub_total) + float(addons_price) + float(tolarance_price))/float(quantity), 2))
#     new_total_price = math.ceil(round((float(new_unit_price)*float(quantity)), 2))
#     new_addon_sqm_price = math.ceil(round(float(new_sub_total) + float(addons_price), 2) / float(deducted_area))
#     difference = float(actual_total) - float(new_total_price)
    
#     if not product_obj.deduction_method:
#         difference = None
#         # new_total_price = None
        
    
#     context = {
#         "new_alumn": round(new_alumn, 2),
#         "new_infill": new_infill,
#         "new_sealant": new_sealant,
#         "new_accessories": new_accessories,
#         "new_com": new_com,
#         "new_overhead": round(new_overhead, 2),
#         "new_labour": round(new_labour, 2),
#         "overhead_perce": float(overhead_perce),
#         "labour_perce": float(labour_perce),
#         "new_sub_total": new_sub_total,
#         "new_sqm_price": new_sqm_price,
#         "addons_price": addons_price,
#         "tolarance_price": tolarance_price,
#         "new_unit_price": new_unit_price,
#         "quantity": quantity,
#         "new_total_price": new_total_price,
#         "new_addon_sqm_price": new_addon_sqm_price,
#         "actual_total": actual_total,
#         "difference": difference,
#     }
#     return context


@register.simple_tag
def have_deducted_associated(request, pk):
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
            
            '/Estimation/add_estimation_pricing/',
            '/Enquiries/product_duplicate/',
            '/Enquiries/edit_enq_specifications/',
            '/Enquiries/building_duplicate/',
            '/Estimation/add_associated_product/',
            '/Estimation/add_typical_buildings/',
            '/Estimation/typical_togle_update/',
            '/Estimation/consolidate_aluminium_update/',
            '/Estimation/consolidate_price_update/',
            '/Estimation/consolidate_addon_update/',
            '/Estimation/consolidate_sealant_update/',
            '/Estimation/consolidate_loh_update/',
            '/Estimation/consolidate_unitprice_update/',
            '/Estimation/merge_summary_update_spec/',
            '/Estimation/merge_summary_update/',
            '/Estimation/reset_merge/',
            '/Estimation/product_merge/',
            '/Estimation/sync_associated_data_full/',
            '/Estimation/building_delete/',
            '/Estimation/reset_sync_data/',
            '/Estimation/disable_products/',
        ]

    if any(path in request.path for path in PATHS):
        EstimationMainProductModel = EstimationMainProduct
        MainProductAluminiumModel = MainProductAluminium
        MainProductGlassModel = MainProductGlass
        MainProductSiliconModel = MainProductSilicon
        PricingOptionModel = PricingOption
        MainProductAddonCostModel = MainProductAddonCost
        MainProductAccessoriesModel = MainProductAccessories
        AssociatedProduct = EstimationProduct_Associated_Data
        
    else:
        EstimationMainProductModel = Temp_EstimationMainProduct
        MainProductAluminiumModel = Temp_MainProductAluminium
        MainProductGlassModel = Temp_MainProductGlass
        MainProductSiliconModel = Temp_MainProductSilicon
        PricingOptionModel = Temp_PricingOption
        MainProductAddonCostModel = Temp_MainProductAddonCost
        MainProductAccessoriesModel = Temp_MainProductAccessories
        AssociatedProduct = Temp_EstimationProduct_Associated_Data

    try:
        product_obj = EstimationMainProductModel.objects.get(pk=pk)
    except Exception:
        product_obj = None
    
    if product_obj:
        assocciated_data = EstimationMainProductModel.objects.filter(main_product__in=[associated.estimation_main_product.id for associated in AssociatedProduct.objects.filter(estimation_main_product=product_obj, is_deducted=True)], product_type=2)
    else:
        assocciated_data = None
    
    main_aluminium_price = 0
    main_aluminium_price_2 = 0
    
    main_glass_price = 0
    main_glass_price_2 = 0
    
    main_accessory_price = 0
    main_accessory_price_2 = 0
    
    main_sealant_price = 0
    main_sealant_price_2 = 0
    
    overhead_perce = 0
    labour_perce = 0
    addons_price = 0
    tolarance_price = 0
    tolarance_price_2 = 0
    quantity = 0
    aluminium_price = 0
    glass_price = 0
    sealant_price = 0
    assocciated_area = 0
    main_area = 0
    deducted_area = 1
    
    # Main Product Calculations
    if product_obj:
        try:
            main_aluminium_obj = MainProductAluminiumModel.objects.get(estimation_product=product_obj.id)
        except Exception:
            main_aluminium_obj = None
        try:
            main_glass_obj = MainProductGlassModel.objects.get(
                    estimation_product=product_obj.id, 
                    glass_primary=True
                )
            main_second_glass_obj = MainProductGlassModel.objects.select_related('estimation_product').filter(
                        estimation_product=product_obj.id, 
                        glass_primary=False
                    )
        except Exception:
            main_glass_obj = None
            main_second_glass_obj = None
        
        try:
            main_silicon_obj = MainProductSiliconModel.objects.get(estimation_product=product_obj.id)
        except Exception:
            main_silicon_obj = None
            
        # main_addons = MainProductAddonCostModel.objects.select_related('estimation_product').filter(estimation_product=product_obj.id)
        
        try:
            main_pricing_control = PricingOptionModel.objects.get(estimation_product=product_obj.id)
        except Exception as e:
            main_pricing_control = None
            
        if product_obj.building.typical_buildings_enabled:
            typical_building_number = product_obj.building.no_typical_buildings
        else:
            typical_building_number = 1
        
        main_area = float(main_aluminium_obj.total_area)
        quantity = float(main_aluminium_obj.total_quantity)*float(typical_building_number)
        
        if product_obj.deduction_method == 2:
            deducted_area = float(main_aluminium_obj.area) - float(product_obj.deducted_area)
        else:
            deducted_area = float(main_aluminium_obj.total_area)
        
        if main_second_glass_obj:
            for sec_glass in main_second_glass_obj:
                main_glass_price += float(sec_glass.glass_quoted_price) * float(main_aluminium_obj.total_quantity)*float(typical_building_number)
                main_glass_price_2 += float(sec_glass.glass_quoted_price) #* float(main_aluminium_obj.total_quantity)*float(typical_building_number)
                
        if main_glass_obj and main_glass_obj.is_glass_cost and main_glass_obj.glass_quoted_price:
            main_glass_price += float(math.ceil(main_glass_obj.glass_quoted_price)) * float(main_aluminium_obj.total_quantity)*float(typical_building_number)
            main_glass_price_2 += float(math.ceil(main_glass_obj.glass_quoted_price)) #* float(main_aluminium_obj.total_quantity)*float(typical_building_number)
        
        if main_aluminium_obj.al_quoted_price:
            main_aluminium_price += float(math.ceil(main_aluminium_obj.al_quoted_price)) * float(main_aluminium_obj.total_quantity)*float(typical_building_number)
            main_aluminium_price_2 += float(math.ceil(main_aluminium_obj.al_quoted_price)) #* float(main_aluminium_obj.total_quantity)*float(typical_building_number)
        if product_obj.accessory_total and (product_obj.accessory_total and product_obj.is_accessory):
            main_accessory_price += float(math.ceil(product_obj.accessory_total)) * float(main_aluminium_obj.total_quantity)*float(typical_building_number)
            main_accessory_price_2 += float(math.ceil(product_obj.accessory_total)) #* float(main_aluminium_obj.total_quantity)*float(typical_building_number)
        
        if main_silicon_obj and main_silicon_obj.is_silicon:
            main_sealant_price += float(math.ceil(main_silicon_obj.silicon_quoted_price)) * float(main_aluminium_obj.total_quantity)*float(typical_building_number)
            main_sealant_price_2 += float(math.ceil(main_silicon_obj.silicon_quoted_price)) #* float(main_aluminium_obj.total_quantity)*float(typical_building_number)
        
        if main_aluminium_obj.aluminium_pricing in [1, 2, 4] and product_obj.is_tolerance:
            if product_obj.tolerance_type == 1: # percentage
                tolarance = int(product_obj.tolerance) / 100
                tolarance_price = float(float(math.ceil(main_aluminium_obj.al_quoted_price)) * tolarance) * float(main_aluminium_obj.total_quantity)*float(typical_building_number)
                tolarance_price_2 = float(float(math.ceil(main_aluminium_obj.al_quoted_price)) * tolarance) #* float(main_aluminium_obj.total_quantity)*float(typical_building_number)
            elif product_obj.tolerance_type == 2:
                tolarance_price = float(float(product_obj.tolerance)) * float(main_aluminium_obj.total_quantity)*float(typical_building_number)
                tolarance_price_2 = float(float(product_obj.tolerance)) #* float(main_aluminium_obj.total_quantity)*float(typical_building_number)
            else:
                tolarance_price = 0
                tolarance_price_2 = 0
                
        overhead_perce = main_pricing_control.overhead_perce
        labour_perce = main_pricing_control.labour_perce
        addons_price = float(math.ceil(product_obj.total_addon_cost)) * float(main_aluminium_obj.total_quantity)*float(typical_building_number)
        addons_price_2 = float(math.ceil(product_obj.total_addon_cost)) #*float(main_aluminium_obj.total_quantity)*float(typical_building_number)
        
    # Assocciated Product Calculations
    if assocciated_data:
        for assocciated_product in assocciated_data:
            try:
                aluminium_obj = MainProductAluminiumModel.objects.get(estimation_product=assocciated_product.id)
            except Exception:
                aluminium_obj = None
    
            assocciated_area += aluminium_obj.total_area
        
    cost_of_material = main_aluminium_price_2 + main_glass_price_2 + main_accessory_price_2 + main_sealant_price_2
    
    # print("main_aluminium_price==>", main_aluminium_price)
    overhead_price = (float(overhead_perce/100)*float(cost_of_material)) #* float(main_aluminium_obj.total_quantity) * float(typical_building_number) 
    labour_price =  (float(labour_perce/100)*float(cost_of_material)) #* float(main_aluminium_obj.total_quantity) * float(typical_building_number)
    
    actual_total = math.ceil(round(cost_of_material + overhead_price + labour_price +  tolarance_price_2 + addons_price_2, 2)) \
                    * float(main_aluminium_obj.total_quantity) * float(typical_building_number) 
    
    sqm_alum_price = round((float(main_aluminium_price)/float(main_area))*float(assocciated_area), 2)
    
    sqm_glass_price = round((float(main_glass_price)/float(main_area))*float(assocciated_area), 2)
    sqm_main_sealant_price = round((float(main_sealant_price)/float(main_area))*float(assocciated_area), 2)
    sqm_main_accessories_price = round((float(main_accessory_price)/float(main_area))*float(assocciated_area), 2)
    
    new_alumn = (float(main_aluminium_price) - float(sqm_alum_price))
    new_infill = (float(main_glass_price) - float(sqm_glass_price))
    new_sealant = (float(main_sealant_price) - float(sqm_main_sealant_price))
    new_accessories = (float(main_accessory_price) - float(sqm_main_accessories_price))
    
    new_com = round(float(new_alumn) + float(new_infill) + float(new_sealant) + float(new_accessories), 2)
    new_com_display = round(float(math.ceil(new_alumn)) + float(math.ceil(new_infill)) + float(math.ceil(new_sealant)) + float(math.ceil(new_accessories)), 2)
    
    new_overhead = ((float(overhead_perce)/100)*float(new_com))
    new_labour = ((float(labour_perce)/100)*float(new_com))
    
    # new_sub_total = math.ceil(round(float(new_com) + float(new_overhead) + float(new_labour), 2))
    
    new_sub_total = float(new_com) + float(new_overhead) + float(new_labour)
    # new_sub_total = round_half_even(float(new_com) + float(new_overhead) + float(new_labour))
    new_sqm_price = round(float(new_sub_total)/float(deducted_area), 2)
        
    # new_unit_price = round_half_even((float(new_sub_total) + float(addons_price) + float(tolarance_price))/float(quantity))
    
    new_unit_price = math.ceil(round((float(new_sub_total) + float(addons_price) + float(tolarance_price))/float(quantity), 2))
    new_total_price = math.ceil(round((float(new_unit_price)*float(quantity)), 2))
    new_addon_sqm_price = math.ceil(round(float(new_sub_total) + float(addons_price), 2) / float(deducted_area))
    difference = float(actual_total) - float(new_total_price)
    
    if not product_obj.deduction_method:
        difference = None
        # new_total_price = None
        
    
    context = {
        "new_alumn": round(math.ceil(new_alumn), 2),
        "new_infill": round(math.ceil(new_infill), 2),
        "new_sealant": round(math.ceil(new_sealant), 2),
        "new_accessories": round(math.ceil(new_accessories), 2),
        "new_com": new_com,
        "new_com_display": new_com_display,
        "new_overhead": round(new_overhead, 2),
        "new_labour": round(new_labour, 2),
        "overhead_perce": float(overhead_perce),
        "labour_perce": float(labour_perce),
        "new_sub_total": new_sub_total,
        "new_sqm_price": new_sqm_price,
        "addons_price": addons_price,
        "tolarance_price": tolarance_price,
        "new_unit_price": new_unit_price,
        "quantity": quantity,
        "new_total_price": new_total_price,
        "new_addon_sqm_price": new_addon_sqm_price,
        "actual_total": actual_total,
        "difference": difference,
    }
    return context
