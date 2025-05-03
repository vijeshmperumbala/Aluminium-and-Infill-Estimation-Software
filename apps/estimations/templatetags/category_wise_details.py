import math
from django import template
from apps.Categories.models import Category
from apps.enquiries.models import Estimations, Temp_Estimations
from apps.estimations.models import (
    EstimationMainProduct,
    MainProductAddonCost,
    MainProductAluminium,
    MainProductGlass,
    PricingOption,
    Temp_EstimationMainProduct,
    Temp_MainProductAddonCost,
    Temp_MainProductAluminium,
    Temp_MainProductGlass,
    Temp_PricingOption,
    
)
from apps.functions import product_unit_price
from apps.projects.models import SalesOrderItems, SalesOrderSpecification

register = template.Library()


@register.simple_tag
def category_data(request, version, category_id):
    """
    This function calculates and returns various data related to a category of products in an
    estimation.
    
    :param request: The HTTP request object that contains metadata about the request being made, such as
    the user agent, headers, and query parameters
    :param version: The version of the estimation being used to retrieve the category data
    :param category_id: The ID of the category for which the data is being fetched
    :return: a dictionary containing various calculated values related to a category of products in an
    estimation. These values include quantities, areas, costs, overheads, subtotals, add-ons,
    tolerances, unit prices, and totals for both the main products and any add-ons.
    """

    quantity = 0
    quantity_addon = 0
    area = 0
    area_addon = 0
    aluminium_unit_price = 0
    infill_unit_price = 0
    accessory_unit_price = 0
    sealant_unit_price = 0
    cost_of_material = 0
    labour_overhead = 0
    sub_total = 0
    addon = 0
    tolerance = 0
    rp_sqm_without_addon = 0
    rp_sqm = 0
    total = 0

    aluminium_unit_price_addon = 0
    infill_unit_price_addon = 0
    sealant_unit_price_addon = 0
    accessory_unit_price_addon = 0
    cost_of_material_addon =0
    labour_overhead_addon = 0
    sub_total_addon = 0
    addon_addon = 0
    tolerance_addon = 0
    rp_sqm_without_addon_addon = 0
    rp_sqm_addon = 0
    total_addon = 0
    addon_flag = 0
    no_addon_flag = 0
    uom_addon = None
    uom = None
    
    PATHS = [
        '/Estimation/estimation_list_enquiry/',
        '/Estimation/summary_view_all/',
        '/Estimation/consolidate_scope_summary_print/',
    ]

    if any(path in request.path for path in PATHS):
        MainProduct = EstimationMainProduct
        AluminiumModel = MainProductAluminium
        MainProductGlassModel = MainProductGlass
        MainProductAddonCostModel = MainProductAddonCost
        PricingOptionModel = PricingOption
    else:
        MainProduct = Temp_EstimationMainProduct
        AluminiumModel = Temp_MainProductAluminium
        MainProductGlassModel = Temp_MainProductGlass
        MainProductAddonCostModel = Temp_MainProductAddonCost
        PricingOptionModel = Temp_PricingOption

    products = MainProduct.objects.select_related('building', 'category').filter(building__estimation=version ,category=category_id, disabled=False).order_by('id')
    for product in products:
        data = AluminiumModel.objects.get(estimation_product=product)
        if addon_data := MainProductAddonCostModel.objects.filter(
             estimation_product=product
            ):
            addon_flag +=1
            if product.building.typical_buildings_enabled:
                typical_buildings_addon = product.building.no_typical_buildings
            else:
                typical_buildings_addon = 1
            price_data_addon = product_unit_price(request=request, pk=product.id)
            if (
                product.category.is_curtain_wall
                and not product.after_deduction_price
            ):
                # if not product.product_type == 2 and not product.main_product.after_deduction_price:
                quantity_addon += (float(data.total_area) * float(typical_buildings_addon))
                area_addon += float(data.area) * float(typical_buildings_addon) 
            elif product.category.is_curtain_wall:
                # if not product.product_type == 2 and not product.main_product.after_deduction_price:
                quantity_addon += (float(data.area) - float(product.deducted_area)) * float(typical_buildings_addon)*float(data.total_quantity)
                area_addon += (float(data.area) - float(product.deducted_area)) * float(typical_buildings_addon) * float(data.total_quantity)
            else:
                quantity_addon += (float(data.total_quantity) * float(typical_buildings_addon))
                if not product.after_deduction_price:
                    area_addon += float(data.total_area) * float(typical_buildings_addon)
                else:
                    area_addon += (float(data.area) - float(product.deducted_area)) * float(typical_buildings_addon)
                    
            if product.product_type == 2 :
                if not product.main_product.have_merge:
                    aluminium_unit_price_addon += (float(price_data_addon['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings_addon))
                    infill_unit_price_addon += (float(price_data_addon['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings_addon))
                    accessory_unit_price_addon += (float(price_data_addon['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings_addon))
                    sealant_unit_price_addon += (float(price_data_addon['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings_addon))
                    cost_of_material_addon += (price_data_addon['material_cost'] * float(typical_buildings_addon))
                    labour_overhead_addon += (price_data_addon['labour_overhead'] * float(typical_buildings_addon))
                    sub_total_addon += (price_data_addon['sub_total'] * float(typical_buildings_addon))
                    addon_addon += (price_data_addon['addon'] * float(typical_buildings_addon))
                    tolerance_addon += (price_data_addon['tolerance'] * float(typical_buildings_addon))
                    rp_sqm_without_addon_addon += price_data_addon['product_sqm_price_without_addon']
                    rp_sqm_addon += price_data_addon['rp_sqm']
                    total_addon += (float(math.ceil(price_data_addon['unit_price'])) * float(data.total_quantity) * float(typical_buildings_addon))
            else:
                # if not product.have_merge:
                aluminium_unit_price_addon += (float(price_data_addon['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings_addon))
                infill_unit_price_addon += (float(price_data_addon['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings_addon))
                accessory_unit_price_addon += (float(price_data_addon['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings_addon))
                sealant_unit_price_addon += (float(price_data_addon['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings_addon))
                cost_of_material_addon += (price_data_addon['material_cost'] * float(typical_buildings_addon))
                labour_overhead_addon += (price_data_addon['labour_overhead'] * float(typical_buildings_addon))
                sub_total_addon += (price_data_addon['sub_total'] * float(typical_buildings_addon))
                addon_addon += (price_data_addon['addon'] * float(typical_buildings_addon))
                tolerance_addon += (price_data_addon['tolerance'] * float(typical_buildings_addon))
                rp_sqm_without_addon_addon += price_data_addon['product_sqm_price_without_addon']
                rp_sqm_addon += price_data_addon['rp_sqm']
                # total_addon += (float(math.ceil(price_data_addon['unit_price'])) * float(data.total_quantity) * float(typical_buildings_addon))
                total_addon += (float(math.ceil(price_data_addon['unit_price_massupdate'])) * float(data.total_quantity) * float(typical_buildings_addon))
            uom_addon = price_data_addon['uom']
            
        else:
            no_addon_flag += 1
            if product.building.typical_buildings_enabled:
                typical_buildings = product.building.no_typical_buildings
            else:
                typical_buildings = 1
            price_data = product_unit_price(request=request, pk=product.id)
            if (
                product.category.is_curtain_wall
                and not product.after_deduction_price
            ):
                quantity += (float(data.area) * float(data.total_quantity) * float(typical_buildings))
                area += float(data.area) * float(typical_buildings) * float(data.total_quantity)
            elif product.category.is_curtain_wall:
                quantity += (float(data.area) - float(product.deducted_area)) * float(typical_buildings) * float(data.total_quantity)
                area += (float(data.area) - float(product.deducted_area)) * float(typical_buildings) * float(data.total_quantity)
            else:
                quantity += (float(data.total_quantity) * float(typical_buildings))
                if not product.after_deduction_price:
                    area += float(data.total_area) * float(typical_buildings)
                else:
                    area += (float(data.area) - float(product.deducted_area)) * float(typical_buildings) * float(data.total_quantity)
            # area += area_temp
            
            if product.product_type == 2 :
                if not product.main_product.have_merge:
                    aluminium_unit_price += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    infill_unit_price += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    accessory_unit_price += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    sealant_unit_price += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    cost_of_material += (price_data['material_cost'] * float(typical_buildings))
                    labour_overhead += (price_data['labour_overhead'] * float(typical_buildings))
                    sub_total += (price_data['sub_total'] * float(typical_buildings))
                    addon += (price_data['addon'] * float(typical_buildings))
                    tolerance += (price_data['tolerance'] * float(typical_buildings))
                    rp_sqm_without_addon += price_data['product_sqm_price_without_addon']
                    rp_sqm += price_data['rp_sqm']
                    total += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))
                
            else:
                # if not product.have_merge:
                aluminium_unit_price += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                infill_unit_price += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                accessory_unit_price += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                sealant_unit_price += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                cost_of_material += (price_data['material_cost'] * float(typical_buildings))
                labour_overhead += (price_data['labour_overhead'] * float(typical_buildings))
                sub_total += (price_data['sub_total'] * float(typical_buildings))
                addon += (price_data['addon'] * float(typical_buildings))
                tolerance += (price_data['tolerance'] * float(typical_buildings))
                rp_sqm_without_addon += price_data['product_sqm_price_without_addon']
                rp_sqm += price_data['rp_sqm']
                total += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))
                # else:
                #     aluminium_unit_price += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                #     infill_unit_price += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                #     accessory_unit_price += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                #     sealant_unit_price += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                #     cost_of_material += (price_data['material_cost'] * float(typical_buildings))
                #     labour_overhead += (price_data['labour_overhead'] * float(typical_buildings))
                #     sub_total += (price_data['sub_total'] * float(typical_buildings))
                #     addon += (price_data['addon'] * float(typical_buildings))
                #     tolerance += (price_data['tolerance'] * float(typical_buildings))
                #     rp_sqm_without_addon += price_data['product_sqm_price_without_addon']
                #     rp_sqm += price_data['rp_sqm']
                #     total += (float(math.ceil(price_data['unit_price_massupdate'])) * float(data.total_quantity) * float(typical_buildings))
            uom = price_data['uom']
            
    data = {
         "quantity": quantity,
         "area": area,
         "aluminium_unit_price": round(aluminium_unit_price, 2),
         "infill_unit_price": round(infill_unit_price, 2),
         "accessory_unit_price": round(accessory_unit_price, 2),
         "sealant_unit_price": round(sealant_unit_price, 2),
         "cost_of_material": round(cost_of_material, 2),
         "labour_overhead": round(labour_overhead, 2),
         "sub_total": round(sub_total, 2),
         "addon": round(addon, 2),
         "tolerance": round(tolerance, 2),
         "uom": uom,
         "rp_sqm_without_addon": round(rp_sqm_without_addon, 2),
         "rp_sqm": round(rp_sqm, 2),
         "total": round(total, 2),

         "addon_flag":addon_flag,
         "no_addon_flag": no_addon_flag,
         "quantity_addon": quantity_addon,
         "area_addon": area_addon,
         "aluminium_unit_price_addon": round(aluminium_unit_price_addon, 2),
         "infill_unit_price_addon": round(infill_unit_price_addon, 2),
         "accessory_unit_price_addon": round(accessory_unit_price_addon, 2),
         "sealant_unit_price_addon": round(sealant_unit_price_addon, 2),
         "cost_of_material_addon": round(cost_of_material_addon, 2),
         "labour_overhead_addon": round(labour_overhead_addon, 2),
         "sub_total_addon": round(sub_total_addon, 2),
         "addon_addon": round(addon_addon, 2),
         "tolerance_addon": round(tolerance_addon, 2),
         "uom_addon": uom_addon,
         "rp_sqm_without_addon_addon": round(rp_sqm_without_addon_addon, 2),
         "rp_sqm_addon": round(rp_sqm_addon, 2),
         "total_addon": round(total_addon, 2),
    }
    return data

@register.simple_tag
def category_data_building_wise(request, version, building, category_id):
    
    """
    This function calculates and returns various data related to a specific category of products in a
    building for an estimation project.
    
    :param request: The HTTP request object that contains metadata about the request being made
    :param version: The version of the estimation being used
    :param building: The building object for which the category data is being fetched
    :param category_id: The ID of the category for which the data is being fetched
    :return: a dictionary containing various calculated values related to a specific category of
    products in a building, including quantity, area, cost of material, labour overhead, sub-total,
    addon, tolerance, unit of measurement, rate per square meter without addon, rate per square meter,
    and total. It also includes flags indicating whether there are any addons or not, and if there are,
    it includes additional
    """
    
    quantity = 0
    area = 0
    aluminium_unit_price = 0
    infill_unit_price = 0
    accessory_unit_price = 0
    sealant_unit_price = 0
    cost_of_material = 0
    labour_overhead = 0
    sub_total = 0
    addon= 0 
    tolerance = 0
    rp_sqm_without_addon = 0
    rp_sqm = 0
    total = 0
    
    addon_flag = 0
    no_addon_flag = 0
    
    quantity_addon = 0
    area_addon = 0
    aluminium_unit_price_addon = 0
    infill_unit_price_addon = 0
    sealant_unit_price_addon = 0
    accessory_unit_price_addon = 0
    cost_of_material_addon = 0
    labour_overhead_addon = 0
    sub_total_addon = 0
    addon_addon = 0 
    tolerance_addon = 0
    rp_sqm_without_addon_addon = 0
    rp_sqm_addon = 0
    total_addon = 0
    unit_price = 0
    addon_unit_price = 0
    
    uom_addon = None
    uom = None
    PATHS = [
        '/Estimation/building_category_summary/',
        '/Estimation/estimation_list_enquiry/',
        '/Estimation/estimation_list_by_boq_enquiry/',
        '/Project/project_scop/',
        '/Project/project_contract_items/',
        '/Estimation/summary_view_all/',
        '/Estimation/building_summary/',
        '/Estimation/building_scope_summary_print/',
        '/Estimation/consolidate_scope_summary_print/',
        '/Estimation/spec_wise_building/',
    ]
    if any(path in request.path for path in PATHS):
        MainProduct = EstimationMainProduct
        AluminiumModel = MainProductAluminium
        MainProductAddonCostModel = MainProductAddonCost
        EstimationModel = Estimations
        MainProductGlassModel = MainProductGlass
        PricingOptionModel = PricingOption
    else:
        MainProduct = Temp_EstimationMainProduct
        AluminiumModel = Temp_MainProductAluminium
        MainProductAddonCostModel = Temp_MainProductAddonCost
        EstimationModel = Temp_Estimations
        MainProductGlassModel = Temp_MainProductGlass
        PricingOptionModel = Temp_PricingOption
    
    products = MainProduct.objects.select_related('building', 'category').filter(building=building, building__estimation=version, category=category_id, disabled=False).order_by('id')
    
    for product in products:
        addon_data = MainProductAddonCostModel.objects.filter(estimation_product=product)
        price_data = product_unit_price(request=request, pk=product.id)
        if product.building.typical_buildings_enabled:
            typical_buildings = product.building.no_typical_buildings
        else:
            typical_buildings = 1
            
        if addon_data:
            addon_flag += 1
            if product.category.is_curtain_wall:
                data = AluminiumModel.objects.get(estimation_product=product)
                if product.category.is_curtain_wall:
                    if not product.after_deduction_price:
                        quantity_addon += (float(data.total_area) * float(typical_buildings))
                        area_addon += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        area_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                elif product.category.handrail:
                    if not product.after_deduction_price:
                        quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                        area_addon += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                        area_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                else:
                    if not product.after_deduction_price:
                        quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                        area_addon += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                        area_addon += (float(data.total_area) - (float(product.deducted_area)*float(data.total_quantity))) * float(typical_buildings)
                        
                        
                if product.product_type == 2 :
                    # if not product.main_product.have_merge:
                    aluminium_unit_price_addon += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    infill_unit_price_addon += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    accessory_unit_price_addon += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    sealant_unit_price_addon += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    cost_of_material_addon += (price_data['material_cost'] * float(typical_buildings))
                    labour_overhead_addon += (price_data['labour_overhead'] * float(typical_buildings))
                    sub_total_addon += (price_data['sub_total'] * (float(typical_buildings)))
                    addon_addon += (price_data['addon'] * float(typical_buildings))
                    tolerance_addon += (price_data['tolerance'] * float(typical_buildings))
                    rp_sqm_without_addon_addon += price_data['product_sqm_price_without_addon']
                    rp_sqm_addon += price_data['rp_sqm']
                    addon_unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))
                else:
                    if not product.have_merge:
                        aluminium_unit_price_addon += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price_addon += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price_addon += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price_addon += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material_addon += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead_addon += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total_addon += (math.ceil(price_data['sub_total']) * (float(typical_buildings)))
                        addon_addon += (price_data['addon'] * float(typical_buildings))
                        tolerance_addon += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm_addon += price_data['rp_sqm']
                        addon_unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))
                        # addon_unit_price += (float(math.ceil(price_data['unit_price_massupdate'])) * float(data.total_quantity) * float(typical_buildings))
                    else:
                        aluminium_unit_price_addon += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price_addon += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price_addon += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price_addon += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material_addon += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead_addon += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total_addon += (math.ceil(price_data['sub_total']) * (float(typical_buildings)))
                        addon_addon += (price_data['addon'] * float(typical_buildings))
                        tolerance_addon += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm_addon += price_data['rp_sqm']
                        addon_unit_price += (float(math.ceil(price_data['unit_price_massupdate'])) * float(data.total_quantity) * float(typical_buildings))
                        
                        
                uom_addon = price_data['uom']
                total_addon = addon_unit_price
                
            else:
                data = AluminiumModel.objects.get(estimation_product=product)
                if product.category.is_curtain_wall:
                    if not product.after_deduction_price:
                        quantity_addon += (float(data.total_area) * float(typical_buildings))
                        area_addon += float(data.total_area) * float(data.total_quantity) * float(typical_buildings)
                    else:
                        quantity_addon +=  (float(data.total_area)-(float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        area_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                elif product.category.handrail:
                    if not product.after_deduction_price:
                        quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                        area_addon += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                        area_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                else:
                    if not product.after_deduction_price:
                        quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                        area_addon += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                        area_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        
                if product.product_type == 2 :
                    # if not product.main_product.have_merge :
                    aluminium_unit_price_addon += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    infill_unit_price_addon += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    accessory_unit_price_addon += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    sealant_unit_price_addon += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    cost_of_material_addon += (price_data['material_cost'] * float(typical_buildings))
                    labour_overhead_addon += (price_data['labour_overhead'] * float(typical_buildings))
                    sub_total_addon += (price_data['sub_total'] * (float(typical_buildings)))
                    addon_addon += (price_data['addon'] * float(typical_buildings))
                    tolerance_addon += (price_data['tolerance'] * float(typical_buildings))
                    rp_sqm_without_addon_addon += price_data['product_sqm_price_without_addon']
                    rp_sqm_addon += price_data['rp_sqm']
                    addon_unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))
                else:
                    # if product.deduction_method:
                    #     if product.deduction_method in [1, 2]:
                    #         aluminium_unit_price_addon += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #         infill_unit_price_addon += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #         accessory_unit_price_addon += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #         sealant_unit_price_addon += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #         cost_of_material_addon += (price_data['material_cost'] * float(typical_buildings))
                    #         labour_overhead_addon += (price_data['labour_overhead'] * float(typical_buildings))
                    #         sub_total_addon += (math.ceil(price_data['sub_total']) * (float(typical_buildings)))
                    #         addon_addon += (price_data['addon'] * float(typical_buildings))
                    #         tolerance_addon += (price_data['tolerance'] * float(typical_buildings))
                    #         rp_sqm_without_addon_addon += price_data['product_sqm_price_without_addon']
                    #         rp_sqm_addon += price_data['rp_sqm']
                    #         addon_unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))
                    #     else:
                    #         if not product.deduction_method == 3:
                    #             aluminium_unit_price_addon += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #             infill_unit_price_addon += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #             accessory_unit_price_addon += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #             sealant_unit_price_addon += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #             cost_of_material_addon += (price_data['material_cost'] * float(typical_buildings))
                    #             labour_overhead_addon += (price_data['labour_overhead'] * float(typical_buildings))
                    #             sub_total_addon += (price_data['sub_total'] * (float(typical_buildings)))
                    #             addon_addon += (price_data['addon'] * float(typical_buildings))
                    #             tolerance_addon += (price_data['tolerance'] * float(typical_buildings))
                    #             rp_sqm_without_addon_addon += price_data['product_sqm_price_without_addon']
                    #             rp_sqm_addon += price_data['rp_sqm']
                    #             addon_unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))
                    # else:
                        if not product.have_merge:
                            aluminium_unit_price_addon += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                            infill_unit_price_addon += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                            accessory_unit_price_addon += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                            sealant_unit_price_addon += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                            cost_of_material_addon += (price_data['material_cost'] * float(typical_buildings))
                            labour_overhead_addon += (price_data['labour_overhead'] * float(typical_buildings))
                            sub_total_addon += (price_data['sub_total'] * (float(typical_buildings)))
                            addon_addon += (price_data['addon'] * float(typical_buildings))
                            tolerance_addon += (price_data['tolerance'] * float(typical_buildings))
                            rp_sqm_without_addon_addon += price_data['product_sqm_price_without_addon']
                            rp_sqm_addon += price_data['rp_sqm']
                            # addon_unit_price += (float(math.ceil(price_data['unit_price_massupdate'])) * float(data.total_quantity) * float(typical_buildings))
                            addon_unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))
                        else:
                            aluminium_unit_price_addon += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                            infill_unit_price_addon += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                            accessory_unit_price_addon += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                            sealant_unit_price_addon += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                            cost_of_material_addon += (price_data['material_cost'] * float(typical_buildings))
                            labour_overhead_addon += (price_data['labour_overhead'] * float(typical_buildings))
                            sub_total_addon += (price_data['sub_total'] * (float(typical_buildings)))
                            addon_addon += (price_data['addon'] * float(typical_buildings))
                            tolerance_addon += (price_data['tolerance'] * float(typical_buildings))
                            rp_sqm_without_addon_addon += price_data['product_sqm_price_without_addon']
                            rp_sqm_addon += price_data['rp_sqm']
                            addon_unit_price += (float(math.ceil(price_data['unit_price_massupdate'])) * float(data.total_quantity) * float(typical_buildings))
                    
                uom_addon = price_data['uom']
                # # total_addon = addon_unit_price
                # if not product.after_deduction_price:
                #     total_addon = sub_total_addon+addon_addon
                # else:
                total_addon = addon_unit_price
                
        else:
            no_addon_flag += 1
            if product.category.is_curtain_wall:
                data = AluminiumModel.objects.get(estimation_product=product)
                
                if product.category.is_curtain_wall:
                    if not product.after_deduction_price:
                        quantity += (float(data.total_area) * float(typical_buildings))
                        area += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        area += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        
                elif product.category.handrail:
                    if not product.after_deduction_price:
                        quantity += (float(data.total_quantity) * float(typical_buildings))
                        area += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity += (float(data.total_quantity) * float(typical_buildings))
                        # area += (float(data.total_area) - float(product.deducted_area)) * float(typical_buildings)
                        area += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                else:
                    if not product.after_deduction_price:
                        quantity += (float(data.total_quantity) * float(typical_buildings))
                        area += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity += (float(data.total_quantity) * float(typical_buildings))
                        area += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                
                if product.product_type == 2 :
                    # if not product.main_product.have_merge:
                    aluminium_unit_price += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    infill_unit_price += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    accessory_unit_price += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    sealant_unit_price += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    cost_of_material += (price_data['material_cost'] * float(typical_buildings))
                    labour_overhead += (price_data['labour_overhead'] * float(typical_buildings))
                    sub_total += (price_data['sub_total'] * (float(typical_buildings)))
                    addon += (price_data['addon'] * float(typical_buildings))
                    tolerance += (price_data['tolerance'] * float(typical_buildings))
                    rp_sqm_without_addon += price_data['product_sqm_price_without_addon']
                    rp_sqm += price_data['rp_sqm']
                    unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))
                else:
                    if not product.have_merge:
                        aluminium_unit_price += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total += (price_data['sub_total'] * (float(typical_buildings)))
                        addon += (price_data['addon'] * float(typical_buildings))
                        tolerance += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm += price_data['rp_sqm']
                        unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity)* float(typical_buildings))
                        # unit_price += (float(math.ceil(price_data['unit_price_massupdate'])) * float(data.total_quantity)* float(typical_buildings))
                        
                    else:
                        aluminium_unit_price += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total += (price_data['sub_total'] * (float(typical_buildings)))
                        addon += (price_data['addon'] * float(typical_buildings))
                        tolerance += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm += price_data['rp_sqm']
                        unit_price += (float(math.ceil(price_data['unit_price_massupdate'])) * float(data.total_quantity)* float(typical_buildings))
                    
                uom = price_data['uom']
                total = unit_price
                          
            else:
                data = AluminiumModel.objects.get(estimation_product=product)
                if product.category.is_curtain_wall:
                    if not product.after_deduction_price:
                        quantity += (float(data.total_area) * float(typical_buildings))
                        area += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        # area += (float(data.total_area) - float(product.deducted_area)) * float(typical_buildings)
                        area += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        
                elif product.category.handrail:
                    if not product.after_deduction_price:
                        quantity += (float(data.total_quantity) * float(typical_buildings))
                        area += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity += (float(data.total_quantity) * float(typical_buildings))
                        # area += (float(data.total_area) - float(product.deducted_area)) * float(typical_buildings)
                        area += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                else:
                    if not product.after_deduction_price:
                        quantity += (float(data.total_quantity) * float(typical_buildings))
                        area += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity += (float(data.total_quantity) * float(typical_buildings))
                        # area += (float(data.total_area) - float(product.deducted_area)) * float(typical_buildings)
                        area += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        
                if product.product_type == 2 :
                    # if not product.main_product.have_merge:
                    aluminium_unit_price += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    infill_unit_price += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    accessory_unit_price += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    sealant_unit_price += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    cost_of_material += (price_data['material_cost'] * float(typical_buildings))
                    labour_overhead += (price_data['labour_overhead'] * float(typical_buildings))
                    sub_total += (price_data['sub_total'] * (float(typical_buildings)))
                    addon += (price_data['addon'] * float(typical_buildings))
                    tolerance += (price_data['tolerance'] * float(typical_buildings))
                    rp_sqm_without_addon += price_data['product_sqm_price_without_addon']
                    rp_sqm += price_data['rp_sqm']
                    unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))
                        
                else:
                    if not product.have_merge:
                        aluminium_unit_price += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total += (price_data['sub_total'] * (float(typical_buildings)))
                        addon += (price_data['addon'] * float(typical_buildings))
                        tolerance += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm += price_data['rp_sqm']
                        unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))
                        # unit_price += (float(math.ceil(price_data['unit_price_massupdate'])) * float(data.total_quantity) * float(typical_buildings))
                    else:
                        aluminium_unit_price += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total += (price_data['sub_total'] * (float(typical_buildings)))
                        addon += (price_data['addon'] * float(typical_buildings))
                        tolerance += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm += price_data['rp_sqm']
                        unit_price += (float(math.ceil(price_data['unit_price_massupdate'])) * float(data.total_quantity) * float(typical_buildings))
                        
                uom = price_data['uom']
                total = unit_price
                   
    data = {
         "quantity": quantity,
         "area": area,
         "aluminium_unit_price": round(aluminium_unit_price, 2),
         "infill_unit_price": round(infill_unit_price, 2),
         "accessory_unit_price": round(accessory_unit_price, 2),
         "sealant_unit_price": round(sealant_unit_price, 2),
         "cost_of_material": round(cost_of_material, 2),
         "labour_overhead": round(labour_overhead, 2),
         "sub_total": round(sub_total, 2),
         "addon": round(addon, 2),
         "tolerance": round(tolerance, 2),
         "uom": uom,
         "rp_sqm_without_addon": round(rp_sqm_without_addon, 2),
         "rp_sqm": round(rp_sqm, 2),
         "total": round(total, 2),
         
         "addon_flag":addon_flag,
         "no_addon_flag": no_addon_flag,
         "quantity_addon": quantity_addon,
         "area_addon": area_addon,
         "aluminium_unit_price_addon": round(aluminium_unit_price_addon, 2),
         "infill_unit_price_addon": round(infill_unit_price_addon, 2),
         "accessory_unit_price_addon": round(accessory_unit_price_addon, 2),
         "sealant_unit_price_addon": round(sealant_unit_price_addon, 2),
         "cost_of_material_addon": round(cost_of_material_addon, 2),
         "labour_overhead_addon": round(labour_overhead_addon, 2),
         "sub_total_addon": round(sub_total_addon, 2),
         "addon_addon": round(addon_addon, 2),
         "tolerance_addon": round(tolerance_addon, 2),
         "uom_addon": uom_addon,
         "rp_sqm_without_addon_addon": round(rp_sqm_without_addon_addon, 2),
         "rp_sqm_addon": round(rp_sqm_addon, 2),
         "total_addon": round(total_addon, 2),
    }   
    return data

@register.simple_tag
def specification_summary_scope(request, pk):
    quantity = 0
    area = 0
    aluminium_unit_price = 0
    infill_unit_price = 0
    accessory_unit_price = 0
    sealant_unit_price = 0
    cost_of_material = 0
    labour_overhead = 0
    sub_total = 0
    addon= 0 
    tolerance = 0
    rp_sqm_without_addon = 0
    rp_sqm = 0
    total = 0
    
    addon_flag = 0
    no_addon_flag = 0
    
    quantity_addon = 0
    area_addon = 0
    aluminium_unit_price_addon = 0
    infill_unit_price_addon = 0
    sealant_unit_price_addon = 0
    accessory_unit_price_addon = 0
    cost_of_material_addon = 0
    labour_overhead_addon = 0
    sub_total_addon = 0
    addon_addon = 0 
    tolerance_addon = 0
    rp_sqm_without_addon_addon = 0
    rp_sqm_addon = 0
    total_addon = 0
    unit_price = 0
    addon_unit_price = 0
    
    uom_addon = None
    uom = None
    PATHS = [
        '/Estimation/building_category_summary/',
        '/Estimation/estimation_list_enquiry/',
        '/Estimation/estimation_list_by_boq_enquiry/',
        '/Project/project_scop/',
        '/Project/project_contract_items/',
        '/Estimation/summary_view_all/',
        '/Estimation/specification_wise_scope_summary/',
        '/Estimation/specification_scope_summary_print/',
        '/Estimation/consolidate_scope_summary_print/',
        '/Project/salesItem_specifications/',
        
    ]
    if any(path in request.path for path in PATHS):
        MainProduct = EstimationMainProduct
        AluminiumModel = MainProductAluminium
        MainProductAddonCostModel = MainProductAddonCost
        
    else:
        MainProduct = Temp_EstimationMainProduct
        AluminiumModel = Temp_MainProductAluminium
        MainProductAddonCostModel = Temp_MainProductAddonCost
    
    products = MainProduct.objects.select_related('building', 'category').filter(specification_Identifier=pk, disabled=False).order_by('id')
    for product in products:
        addon_data = MainProductAddonCostModel.objects.filter(estimation_product=product)
        price_data = product_unit_price(request=request, pk=product.id)
        
        if product.building.typical_buildings_enabled:
            typical_buildings = product.building.no_typical_buildings
        else:
            typical_buildings = 1
            
        if addon_data:
            addon_flag += 1
            if product.category.is_curtain_wall:
                data = AluminiumModel.objects.get(estimation_product=product)
                if product.category.is_curtain_wall:
                    if not product.after_deduction_price:
                        quantity_addon += (float(data.total_area) * float(typical_buildings))
                        area_addon += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        area_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        
                elif product.category.handrail:
                    if not product.after_deduction_price:
                        quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                        area_addon += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                        area_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                else:
                    if not product.after_deduction_price:
                        quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                        area_addon += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                        area_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                
                        
                if product.product_type == 2 :
                    if not product.main_product.have_merge:
                        aluminium_unit_price_addon += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price_addon += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price_addon += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price_addon += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material_addon += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead_addon += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total_addon += (price_data['sub_total'] * float(typical_buildings))
                        addon_addon += (price_data['addon'] * float(typical_buildings))
                        tolerance_addon += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm_addon += price_data['rp_sqm']
                        addon_unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))
                        print('addon_unit_price', (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings)))
                else:
                    # if not product.have_merge:
                        aluminium_unit_price_addon += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price_addon += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price_addon += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price_addon += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material_addon += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead_addon += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total_addon += (price_data['sub_total'] * float(typical_buildings))
                        addon_addon += (price_data['addon'] * float(typical_buildings))
                        tolerance_addon += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm_addon += price_data['rp_sqm']
                        addon_unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))
                        print('addon_unit_price', (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings)))
                    # else:
                    #     aluminium_unit_price_addon += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #     infill_unit_price_addon += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #     accessory_unit_price_addon += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #     sealant_unit_price_addon += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #     cost_of_material_addon += (price_data['material_cost'] * float(typical_buildings))
                    #     labour_overhead_addon += (price_data['labour_overhead'] * float(typical_buildings))
                    #     sub_total_addon += (price_data['sub_total'] * float(typical_buildings))
                    #     addon_addon += (price_data['addon'] * float(typical_buildings))
                    #     tolerance_addon += (price_data['tolerance'] * float(typical_buildings))
                    #     rp_sqm_without_addon_addon += price_data['product_sqm_price_without_addon']
                    #     rp_sqm_addon += price_data['rp_sqm']
                    #     addon_unit_price += (float(math.ceil(price_data['unit_price_massupdate'])) * float(data.total_quantity) * float(typical_buildings))
                    
                uom_addon = price_data['uom']
                total_addon = addon_unit_price
                
                
            else:
                data = AluminiumModel.objects.get(estimation_product=product)
                if product.category.is_curtain_wall:
                    if not product.after_deduction_price:
                        quantity_addon += (float(data.total_area) * float(typical_buildings))
                        area_addon += float(data.total_area) * float(data.total_quantity) * float(typical_buildings)
                    else:
                        quantity_addon +=  (float(data.total_area)-(float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings) 
                        area_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                elif product.category.handrail:
                    if not product.after_deduction_price:
                        quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                        area_addon += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                        area_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                else:
                    if not product.after_deduction_price:
                        quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                        area_addon += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                        area_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        
                        
                if product.product_type == 2 :
                    if not product.main_product.have_merge :
                        aluminium_unit_price_addon += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price_addon += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price_addon += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price_addon += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material_addon += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead_addon += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total_addon += (price_data['sub_total'] * float(typical_buildings))
                        addon_addon += (price_data['addon'] * float(typical_buildings))
                        tolerance_addon += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm_addon += price_data['rp_sqm']
                        addon_unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))
                else:
                    # if product.deduction_method:
                    #     if product.deduction_method in [1, 2]:
                    #         aluminium_unit_price_addon += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #         infill_unit_price_addon += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #         accessory_unit_price_addon += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #         sealant_unit_price_addon += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #         cost_of_material_addon += (price_data['material_cost'] * float(typical_buildings))
                    #         labour_overhead_addon += (price_data['labour_overhead'] * float(typical_buildings))
                    #         sub_total_addon += (price_data['sub_total'] * float(typical_buildings))
                    #         addon_addon += (price_data['addon'] * float(typical_buildings))
                    #         tolerance_addon += (price_data['tolerance'] * float(typical_buildings))
                    #         rp_sqm_without_addon_addon += price_data['product_sqm_price_without_addon']
                    #         rp_sqm_addon += price_data['rp_sqm']
                    #         addon_unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))                            
                    #         # addon_unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity)) * float(typical_buildings)
                            
                    #     else:
                    #         if not product.deduction_method == 3:
                    #             aluminium_unit_price_addon += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #             infill_unit_price_addon += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #             accessory_unit_price_addon += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #             sealant_unit_price_addon += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #             cost_of_material_addon += (price_data['material_cost'] * float(typical_buildings))
                    #             labour_overhead_addon += (price_data['labour_overhead'] * float(typical_buildings))
                    #             sub_total_addon += (price_data['sub_total'] * float(typical_buildings))
                    #             addon_addon += (price_data['addon'] * float(typical_buildings))
                    #             tolerance_addon += (price_data['tolerance'] * float(typical_buildings))
                    #             rp_sqm_without_addon_addon += price_data['product_sqm_price_without_addon']
                    #             rp_sqm_addon += price_data['rp_sqm']
                    #             addon_unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))                                
                    #             # addon_unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity)) * float(typical_buildings)
                    # else:
                    # if not product.have_merge:
                        aluminium_unit_price_addon += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price_addon += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price_addon += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price_addon += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material_addon += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead_addon += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total_addon += (price_data['sub_total'] * float(typical_buildings))
                        addon_addon += (price_data['addon'] * float(typical_buildings))
                        tolerance_addon += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm_addon += price_data['rp_sqm']
                        addon_unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))                               
                    # else:
                    #     aluminium_unit_price_addon += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #     infill_unit_price_addon += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #     accessory_unit_price_addon += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #     sealant_unit_price_addon += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #     cost_of_material_addon += (price_data['material_cost'] * float(typical_buildings))
                    #     labour_overhead_addon += (price_data['labour_overhead'] * float(typical_buildings))
                    #     sub_total_addon += (price_data['sub_total'] * float(typical_buildings))
                    #     addon_addon += (price_data['addon'] * float(typical_buildings))
                    #     tolerance_addon += (price_data['tolerance'] * float(typical_buildings))
                    #     rp_sqm_without_addon_addon += price_data['product_sqm_price_without_addon']
                    #     rp_sqm_addon += price_data['rp_sqm']
                    #     addon_unit_price += (float(math.ceil(price_data['unit_price_massupdate'])) * float(data.total_quantity) * float(typical_buildings))                               
                    
                uom_addon = price_data['uom']
                total_addon = addon_unit_price
                
        else:
            no_addon_flag += 1
            if product.category.is_curtain_wall:
                data = AluminiumModel.objects.get(estimation_product=product)
                
                if product.category.is_curtain_wall:
                    if not product.after_deduction_price:
                        quantity += (float(data.total_area) * float(typical_buildings))
                        area += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        area += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        
                elif product.category.handrail:
                    if not product.after_deduction_price:
                        quantity += (float(data.total_quantity) * float(typical_buildings))
                        area += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity += (float(data.total_quantity) * float(typical_buildings))
                        # area += (float(data.total_area) - float(product.deducted_area)) * float(typical_buildings)
                        area += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                else:
                    
                    if not product.after_deduction_price:
                        quantity += (float(data.total_quantity) * float(typical_buildings))
                        area += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity += (float(data.total_quantity) * float(typical_buildings))
                        # area += (float(data.total_area) - float(product.deducted_area)) * float(typical_buildings)
                        area += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                
                if product.product_type == 2 :
                    if not product.main_product.have_merge:
                        aluminium_unit_price += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total += (price_data['sub_total'] * float(typical_buildings))
                        addon += (price_data['addon'] * float(typical_buildings))
                        tolerance += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm += price_data['rp_sqm']
                        unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))        
                        
                else:
                    # if not product.have_merge:
                        aluminium_unit_price += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total += (price_data['sub_total'] * float(typical_buildings))
                        addon += (price_data['addon'] * float(typical_buildings))
                        tolerance += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm += price_data['rp_sqm']
                        unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings)) 
                    # else:
                    #     aluminium_unit_price += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #     infill_unit_price += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #     accessory_unit_price += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #     sealant_unit_price += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #     cost_of_material += (price_data['material_cost'] * float(typical_buildings))
                    #     labour_overhead += (price_data['labour_overhead'] * float(typical_buildings))
                    #     sub_total += (price_data['sub_total'] * float(typical_buildings))
                    #     addon += (price_data['addon'] * float(typical_buildings))
                    #     tolerance += (price_data['tolerance'] * float(typical_buildings))
                    #     rp_sqm_without_addon += price_data['product_sqm_price_without_addon']
                    #     rp_sqm += price_data['rp_sqm']
                    #     unit_price += (float(math.ceil(price_data['unit_price_massupdate'])) * float(data.total_quantity) * float(typical_buildings))                                
                        
                    
                uom = price_data['uom']
                total = unit_price
                
                                
            else:
                data = AluminiumModel.objects.get(estimation_product=product)
                if product.category.is_curtain_wall:
                    if not product.after_deduction_price:
                        quantity += (float(data.total_area) * float(typical_buildings))
                        area += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        # area += (float(data.total_area) - float(product.deducted_area)) * float(typical_buildings)
                        area += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        
                elif product.category.handrail:
                    if not product.after_deduction_price:
                        quantity += (float(data.total_quantity) * float(typical_buildings))
                        area += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity += (float(data.total_quantity) * float(typical_buildings))
                        # area += (float(data.total_area) - float(product.deducted_area)) * float(typical_buildings)
                        area += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                else:
                    if not product.after_deduction_price:
                        quantity += (float(data.total_quantity) * float(typical_buildings))
                        area += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity += (float(data.total_quantity) * float(typical_buildings))
                        # area += (float(data.total_area) - float(product.deducted_area)) * float(typical_buildings)
                        area += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        
                if product.product_type == 2 :
                    if not product.main_product.have_merge:
                        aluminium_unit_price += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total += (price_data['sub_total'] * float(typical_buildings))
                        addon += (price_data['addon'] * float(typical_buildings))
                        tolerance += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm += price_data['rp_sqm']
                        unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))                          
                else:
                    # if not product.have_merge:
                        aluminium_unit_price += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total += (price_data['sub_total'] * float(typical_buildings))
                        addon += (price_data['addon'] * float(typical_buildings))
                        tolerance += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm += price_data['rp_sqm']
                        unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))  
                                                
                    # else:
                    #     aluminium_unit_price += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #     infill_unit_price += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #     accessory_unit_price += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #     sealant_unit_price += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #     cost_of_material += (price_data['material_cost'] * float(typical_buildings))
                    #     labour_overhead += (price_data['labour_overhead'] * float(typical_buildings))
                    #     sub_total += (price_data['sub_total'] * float(typical_buildings))
                    #     addon += (price_data['addon'] * float(typical_buildings))
                    #     tolerance += (price_data['tolerance'] * float(typical_buildings))
                    #     rp_sqm_without_addon += price_data['product_sqm_price_without_addon']
                    #     rp_sqm += price_data['rp_sqm']
                    #     unit_price += (float(math.ceil(price_data['unit_price_massupdate'])) * float(data.total_quantity) * float(typical_buildings))                          
                                            
                    
                uom = price_data['uom']
                total = unit_price
                
    
            
    data = {
            "quantity": quantity,
            "area": area,
            "aluminium_unit_price": round(aluminium_unit_price, 2),
            "infill_unit_price": round(infill_unit_price, 2),
            "accessory_unit_price": round(accessory_unit_price, 2),
            "sealant_unit_price": round(sealant_unit_price, 2),
            "cost_of_material": round(cost_of_material, 2),
            "labour_overhead": round(labour_overhead, 2),
            "sub_total": round(sub_total, 2),
            "addon": round(addon, 2),
            "tolerance": round(tolerance, 2),
            "uom": uom,
            "rp_sqm_without_addon": round(rp_sqm_without_addon, 2),
            "rp_sqm": round(rp_sqm, 2),
            "total": round(total, 2),
            
            "addon_flag":addon_flag,
            "no_addon_flag": no_addon_flag,
            "quantity_addon": quantity_addon,
            "area_addon": area_addon,
            "aluminium_unit_price_addon": round(aluminium_unit_price_addon, 2),
            "infill_unit_price_addon": round(infill_unit_price_addon, 2),
            "accessory_unit_price_addon": round(accessory_unit_price_addon, 2),
            "sealant_unit_price_addon": round(sealant_unit_price_addon, 2),
            "cost_of_material_addon": round(cost_of_material_addon, 2),
            "labour_overhead_addon": round(labour_overhead_addon, 2),
            "sub_total_addon": round(sub_total_addon, 2),
            "addon_addon": round(addon_addon, 2),
            "tolerance_addon": round(tolerance_addon, 2),
            "uom_addon": uom_addon,
            "rp_sqm_without_addon_addon": round(rp_sqm_without_addon_addon, 2),
            "rp_sqm_addon": round(rp_sqm_addon, 2),
            "total_addon": round(total_addon, 2),
    }   
    return data

def _quoate_rate(base, markup, surface=None):
    quoate_rate = (float(base)*markup)+float(base)
    if surface:
        quoate_rate += float(surface)
        
    return quoate_rate

@register.simple_tag
def overview_scope(request, version, t_type=None):
    """
    This function retrieves data related to an estimation and its products, including pricing
    information for aluminum and glass.
    
    :param request: The HTTP request object containing metadata about the current request
    :param version: The version parameter is an identifier for a specific estimation or temporary
    estimation. It is used to retrieve data related to that estimation from the database
    :return: a list of dictionaries containing data related to the estimation and its products,
    including information about the aluminum and glass used, pricing options, and other details.
    """
    PATHS = [
        '/Estimation/summary_view_all/',
        '/Estimation/specification_wise_scope_summary/',
        '/Estimation/consolidate_scope_summary_print/',
        '/Estimation/specification_scope_summary_print/',
        '/Estimation/specification_scope_summary_print_view/',
        # '/Project/salesItem_specifications/',
    ]
    
    
    data = []
    
    if any(path in request.path for path in PATHS):
        EstimationModel = Estimations
        AluminiumModel = MainProductAluminium
        MainProduct = EstimationMainProduct
        MainProductGlassModel = MainProductGlass
        PricingOptionModel = PricingOption
    else:
        EstimationModel = Temp_Estimations
        MainProduct = Temp_EstimationMainProduct
        AluminiumModel = Temp_MainProductAluminium
        MainProductGlassModel = Temp_MainProductGlass
        PricingOptionModel = Temp_PricingOption
        
    estimation = EstimationModel.objects.get(pk=version)
    if t_type == 'category':
        products = MainProduct.objects.filter(building__estimation=estimation.id, disabled=False).order_by('brand', 'category')\
            .distinct('brand', 'category')
    elif t_type == 'specification':
        products = MainProduct.objects.filter(building__estimation=estimation.id, disabled=False).order_by('brand', 'specification_Identifier')\
            .distinct('brand', 'specification_Identifier')
    else:
        products = MainProduct.objects.filter(building__estimation=estimation.id, disabled=False).order_by('brand', 'specification_Identifier')\
            .distinct('brand', 'specification_Identifier')
        
    
    for product in products:
        
        glass_base_rate = 0
        aluminium_base_rate = 0
        glass_quoted = 0
        glass_markup = 0
        aluminium_markup = 0
        
        aluminium_obj = AluminiumModel.objects.get(estimation_product=product)
        pricing = PricingOptionModel.objects.get(estimation_product=product)
        try:
            glass_obj = MainProductGlassModel.objects.get(estimation_product=product, glass_primary=True)
        except:
            glass_obj = None
        
        data_dict = {
            'category': None,
            'specification': None,
            'aluminium_base_rate': None,
            'labour': None,
            'overhead': None,
            'glass_base_rate': None,
            'glass_markup': None,
            'glass_quoted': None,
        }
        if t_type == 'category':
            data_dict['category'] = product.category.category
        else:
            data_dict['category'] = f'{product.specification_Identifier} | {product.specification_Identifier.categories}'
            
        try:
            data_dict['specification'] = product.specification_Identifier.aluminium_system.brands if product.specification_Identifier.aluminium_system else product.specification_Identifier.panel_brand.panel_brands.brands
        except Exception:
            data_dict['specification'] = '-'
            
        if aluminium_obj:
            if aluminium_obj.al_markup:
                aluminium_markup = float(aluminium_obj.al_markup)/100
                
            if aluminium_obj.aluminium_pricing == 1:
                if aluminium_obj.al_price_per_unit:
                    aluminium_base_rate = _quoate_rate(base=aluminium_obj.al_price_per_unit, markup=aluminium_markup)
                    
                elif aluminium_obj.al_price_per_sqm:
                    aluminium_base_rate = _quoate_rate(base=aluminium_obj.al_price_per_sqm, markup=aluminium_markup)
                elif aluminium_obj.al_weight_per_unit:
                    if aluminium_obj.surface_finish:
                        aluminium_base_rate = _quoate_rate(base=aluminium_obj.price_per_kg, markup=aluminium_markup, 
                                                           surface=aluminium_obj.surface_finish.surface_finish_price)
                    else:
                        aluminium_base_rate = _quoate_rate(base=aluminium_obj.price_per_kg, markup=aluminium_markup)
                else:
                    aluminium_base_rate = 0
            elif aluminium_obj.aluminium_pricing == 2:
                if aluminium_obj.pricing_unit == 1:
                    aluminium_base_rate = _quoate_rate(base=aluminium_obj.custom_price, markup=aluminium_markup)
                    
                elif aluminium_obj.pricing_unit == 2:
                    aluminium_base_rate = _quoate_rate(base=aluminium_obj.custom_price, markup=aluminium_markup)
                    
                elif aluminium_obj.pricing_unit == 3:
                    if aluminium_obj.surface_finish:
                        aluminium_base_rate = _quoate_rate(base=aluminium_obj.price_per_kg, markup=aluminium_markup, 
                                                           surface=aluminium_obj.surface_finish.surface_finish_price)
                    else:
                        aluminium_base_rate = _quoate_rate(base=aluminium_obj.price_per_kg, markup=aluminium_markup)
                    
                else:
                    aluminium_base_rate = 0
            elif aluminium_obj.aluminium_pricing == 4:
                if aluminium_obj.surface_finish:
                    aluminium_base_rate = _quoate_rate(base=aluminium_obj.price_per_kg, markup=aluminium_markup, 
                                                       surface=aluminium_obj.surface_finish.surface_finish_price)
                else:
                    aluminium_base_rate = _quoate_rate(base=aluminium_obj.price_per_kg, markup=aluminium_markup)
            else: 
                aluminium_base_rate = 0
        
        data_dict['aluminium_base_rate'] = aluminium_base_rate
        data_dict['labour'] = pricing.labour_perce
        data_dict['overhead'] = pricing.overhead_perce
        
        if glass_obj and glass_obj.glass_quoted_price and glass_obj.is_glass_cost:
            glass_base_rate = float(glass_obj.glass_base_rate)
            # glass_quoted = (float(glass_obj.glass_base_rate)*float(glass_obj.glass_markup_percentage)/100)\
            #     +float(glass_obj.glass_base_rate)
            glass_quoted = _quoate_rate(base=glass_obj.glass_base_rate, markup=float(glass_obj.glass_markup_percentage)/100)
            glass_markup = glass_obj.glass_markup_percentage
        
        data_dict['glass_base_rate'] = glass_base_rate
        data_dict['glass_quoted'] = glass_quoted
        data_dict['glass_markup'] = glass_markup
        data_dict['infill_spec'] = product.specification_Identifier.panel_specification
        
        data.append(data_dict)
            
    return data


@register.simple_tag
def spec_data_building_wise(request, version, building, specification):
    
    
    quantity = 0
    area = 0
    aluminium_unit_price = 0
    infill_unit_price = 0
    accessory_unit_price = 0
    sealant_unit_price = 0
    cost_of_material = 0
    labour_overhead = 0
    sub_total = 0
    addon= 0 
    tolerance = 0
    rp_sqm_without_addon = 0
    rp_sqm = 0
    total = 0
    
    addon_flag = 0
    no_addon_flag = 0
    
    quantity_addon = 0
    area_addon = 0
    aluminium_unit_price_addon = 0
    infill_unit_price_addon = 0
    sealant_unit_price_addon = 0
    accessory_unit_price_addon = 0
    cost_of_material_addon = 0
    labour_overhead_addon = 0
    sub_total_addon = 0
    addon_addon = 0 
    tolerance_addon = 0
    rp_sqm_without_addon_addon = 0
    rp_sqm_addon = 0
    total_addon = 0
    unit_price = 0
    addon_unit_price = 0
    
    uom_addon = None
    uom = None
    PATHS = [
        '/Estimation/building_category_summary/',
        '/Estimation/estimation_list_enquiry/',
        '/Estimation/estimation_list_by_boq_enquiry/',
        '/Project/project_scop/',
        '/Project/project_contract_items/',
        '/Estimation/summary_view_all/',
        '/Estimation/building_summary/',
        '/Estimation/building_scope_summary_print/',
        '/Estimation/consolidate_scope_summary_print/',
        '/Estimation/spec_wise_building/',
    ]
    if any(path in request.path for path in PATHS):
        MainProduct = EstimationMainProduct
        AluminiumModel = MainProductAluminium
        MainProductAddonCostModel = MainProductAddonCost
        EstimationModel = Estimations
        MainProductGlassModel = MainProductGlass
        PricingOptionModel = PricingOption
    else:
        MainProduct = Temp_EstimationMainProduct
        AluminiumModel = Temp_MainProductAluminium
        MainProductAddonCostModel = Temp_MainProductAddonCost
        EstimationModel = Temp_Estimations
        MainProductGlassModel = Temp_MainProductGlass
        PricingOptionModel = Temp_PricingOption
    
    products = MainProduct.objects.select_related('building').filter(building=building, specification_Identifier=specification, disabled=False).order_by('id')
    for product in products:
        addon_data = MainProductAddonCostModel.objects.filter(estimation_product=product)
        price_data = product_unit_price(request=request, pk=product.id)
        if product.building.typical_buildings_enabled:
            typical_buildings = product.building.no_typical_buildings
        else:
            typical_buildings = 1
            
        if addon_data:
            addon_flag += 1
            if product.category.is_curtain_wall:
                data = AluminiumModel.objects.get(estimation_product=product)
                if product.category.is_curtain_wall:
                    if not product.after_deduction_price:
                        quantity_addon += (float(data.total_area) * float(typical_buildings))
                        area_addon += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        area_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                elif product.category.handrail:
                    if not product.after_deduction_price:
                        quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                        area_addon += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                        area_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                else:
                    if not product.after_deduction_price:
                        quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                        area_addon += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                        area_addon += (float(data.total_area) - (float(product.deducted_area)*float(data.total_quantity))) * float(typical_buildings)
                        
                        
                if product.product_type == 2 :
                    if not product.main_product.have_merge:
                        aluminium_unit_price_addon += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price_addon += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price_addon += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price_addon += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material_addon += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead_addon += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total_addon += (price_data['sub_total'] * (float(typical_buildings)))
                        addon_addon += (price_data['addon'] * float(typical_buildings))
                        tolerance_addon += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm_addon += price_data['rp_sqm']
                        addon_unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))
                else:
                    if not product.have_merge:
                        aluminium_unit_price_addon += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price_addon += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price_addon += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price_addon += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material_addon += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead_addon += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total_addon += (math.ceil(price_data['sub_total']) * (float(typical_buildings)))
                        addon_addon += (price_data['addon'] * float(typical_buildings))
                        tolerance_addon += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm_addon += price_data['rp_sqm']
                        addon_unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))
                    else:
                        aluminium_unit_price_addon += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price_addon += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price_addon += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price_addon += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material_addon += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead_addon += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total_addon += (math.ceil(price_data['sub_total']) * (float(typical_buildings)))
                        addon_addon += (price_data['addon'] * float(typical_buildings))
                        tolerance_addon += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm_addon += price_data['rp_sqm']
                        addon_unit_price += (float(math.ceil(price_data['unit_price_massupdate'])) * float(data.total_quantity) * float(typical_buildings))
                        
                        
                uom_addon = price_data['uom']
                total_addon = addon_unit_price
                
            else:
                data = AluminiumModel.objects.get(estimation_product=product)
                if product.category.is_curtain_wall:
                    if not product.after_deduction_price:
                        quantity_addon += (float(data.total_area) * float(typical_buildings))
                        area_addon += float(data.total_area) * float(data.total_quantity) * float(typical_buildings)
                    else:
                        quantity_addon +=  (float(data.total_area)-(float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        area_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                elif product.category.handrail:
                    if not product.after_deduction_price:
                        quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                        area_addon += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                        area_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                else:
                    if not product.after_deduction_price:
                        quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                        area_addon += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                        area_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        
                if product.product_type == 2 :
                    if not product.main_product.have_merge :
                        aluminium_unit_price_addon += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price_addon += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price_addon += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price_addon += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material_addon += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead_addon += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total_addon += (price_data['sub_total'] * (float(typical_buildings)))
                        addon_addon += (price_data['addon'] * float(typical_buildings))
                        tolerance_addon += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm_addon += price_data['rp_sqm']
                        addon_unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))
                else:
                    # if product.deduction_method:
                    #     if product.deduction_method in [1, 2]:
                    #         aluminium_unit_price_addon += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #         infill_unit_price_addon += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #         accessory_unit_price_addon += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #         sealant_unit_price_addon += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #         cost_of_material_addon += (price_data['material_cost'] * float(typical_buildings))
                    #         labour_overhead_addon += (price_data['labour_overhead'] * float(typical_buildings))
                    #         sub_total_addon += (math.ceil(price_data['sub_total']) * (float(typical_buildings)))
                    #         addon_addon += (price_data['addon'] * float(typical_buildings))
                    #         tolerance_addon += (price_data['tolerance'] * float(typical_buildings))
                    #         rp_sqm_without_addon_addon += price_data['product_sqm_price_without_addon']
                    #         rp_sqm_addon += price_data['rp_sqm']
                    #         addon_unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))
                    #     else:
                    #         if not product.deduction_method == 3:
                    #             aluminium_unit_price_addon += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #             infill_unit_price_addon += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #             accessory_unit_price_addon += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #             sealant_unit_price_addon += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                    #             cost_of_material_addon += (price_data['material_cost'] * float(typical_buildings))
                    #             labour_overhead_addon += (price_data['labour_overhead'] * float(typical_buildings))
                    #             sub_total_addon += (price_data['sub_total'] * (float(typical_buildings)))
                    #             addon_addon += (price_data['addon'] * float(typical_buildings))
                    #             tolerance_addon += (price_data['tolerance'] * float(typical_buildings))
                    #             rp_sqm_without_addon_addon += price_data['product_sqm_price_without_addon']
                    #             rp_sqm_addon += price_data['rp_sqm']
                    #             addon_unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))
                    # else:
                    if not product.have_merge:
                        aluminium_unit_price_addon += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price_addon += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price_addon += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price_addon += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material_addon += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead_addon += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total_addon += (price_data['sub_total'] * (float(typical_buildings)))
                        addon_addon += (price_data['addon'] * float(typical_buildings))
                        tolerance_addon += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm_addon += price_data['rp_sqm']
                        addon_unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))
                    else:
                        aluminium_unit_price_addon += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price_addon += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price_addon += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price_addon += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material_addon += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead_addon += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total_addon += (price_data['sub_total'] * (float(typical_buildings)))
                        addon_addon += (price_data['addon'] * float(typical_buildings))
                        tolerance_addon += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm_addon += price_data['rp_sqm']
                        addon_unit_price += (float(math.ceil(price_data['unit_price_massupdate'])) * float(data.total_quantity) * float(typical_buildings))
                    
                uom_addon = price_data['uom']
                # # total_addon = addon_unit_price
                # if not product.after_deduction_price:
                #     total_addon = sub_total_addon+addon_addon
                # else:
                total_addon = addon_unit_price
                
        else:
            no_addon_flag += 1
            if product.category.is_curtain_wall:
                data = AluminiumModel.objects.get(estimation_product=product)
                
                if product.category.is_curtain_wall:
                    if not product.after_deduction_price:
                        quantity += (float(data.total_area) * float(typical_buildings))
                        area += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        area += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        
                elif product.category.handrail:
                    if not product.after_deduction_price:
                        quantity += (float(data.total_quantity) * float(typical_buildings))
                        area += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity += (float(data.total_quantity) * float(typical_buildings))
                        # area += (float(data.total_area) - float(product.deducted_area)) * float(typical_buildings)
                        area += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                else:
                    if not product.after_deduction_price:
                        quantity += (float(data.total_quantity) * float(typical_buildings))
                        area += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity += (float(data.total_quantity) * float(typical_buildings))
                        area += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                
                if product.product_type == 2 :
                    if not product.main_product.have_merge:
                        aluminium_unit_price += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total += (price_data['sub_total'] * (float(typical_buildings)))
                        addon += (price_data['addon'] * float(typical_buildings))
                        tolerance += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm += price_data['rp_sqm']
                        unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))
                else:
                    if not product.have_merge:
                        aluminium_unit_price += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total += (price_data['sub_total'] * (float(typical_buildings)))
                        addon += (price_data['addon'] * float(typical_buildings))
                        tolerance += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm += price_data['rp_sqm']
                        unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity)* float(typical_buildings))
                        
                    else:
                        aluminium_unit_price += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total += (price_data['sub_total'] * (float(typical_buildings)))
                        addon += (price_data['addon'] * float(typical_buildings))
                        tolerance += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm += price_data['rp_sqm']
                        unit_price += (float(math.ceil(price_data['unit_price_massupdate'])) * float(data.total_quantity)* float(typical_buildings))
                    
                uom = price_data['uom']
                total = unit_price
                          
            else:
                data = AluminiumModel.objects.get(estimation_product=product)
                if product.category.is_curtain_wall:
                    if not product.after_deduction_price:
                        quantity += (float(data.total_area) * float(typical_buildings))
                        area += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        # area += (float(data.total_area) - float(product.deducted_area)) * float(typical_buildings)
                        area += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        
                elif product.category.handrail:
                    if not product.after_deduction_price:
                        quantity += (float(data.total_quantity) * float(typical_buildings))
                        area += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity += (float(data.total_quantity) * float(typical_buildings))
                        # area += (float(data.total_area) - float(product.deducted_area)) * float(typical_buildings)
                        area += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                else:
                    if not product.after_deduction_price:
                        quantity += (float(data.total_quantity) * float(typical_buildings))
                        area += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity += (float(data.total_quantity) * float(typical_buildings))
                        # area += (float(data.total_area) - float(product.deducted_area)) * float(typical_buildings)
                        area += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        
                if product.product_type == 2 :
                    if not product.main_product.have_merge:
                        aluminium_unit_price += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total += (price_data['sub_total'] * (float(typical_buildings)))
                        addon += (price_data['addon'] * float(typical_buildings))
                        tolerance += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm += price_data['rp_sqm']
                        unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))
                        
                else:
                    if not product.have_merge:
                        aluminium_unit_price += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total += (price_data['sub_total'] * (float(typical_buildings)))
                        addon += (price_data['addon'] * float(typical_buildings))
                        tolerance += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm += price_data['rp_sqm']
                        unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))
                    else:
                        aluminium_unit_price += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total += (price_data['sub_total'] * (float(typical_buildings)))
                        addon += (price_data['addon'] * float(typical_buildings))
                        tolerance += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm += price_data['rp_sqm']
                        unit_price += (float(math.ceil(price_data['unit_price_massupdate'])) * float(data.total_quantity) * float(typical_buildings))
                        
                uom = price_data['uom']
                total = unit_price
                   
    data = {
         "quantity": quantity,
         "area": area,
         "aluminium_unit_price": round(aluminium_unit_price, 2),
         "infill_unit_price": round(infill_unit_price, 2),
         "accessory_unit_price": round(accessory_unit_price, 2),
         "sealant_unit_price": round(sealant_unit_price, 2),
         "cost_of_material": round(cost_of_material, 2),
         "labour_overhead": round(labour_overhead, 2),
         "sub_total": round(sub_total, 2),
         "addon": round(addon, 2),
         "tolerance": round(tolerance, 2),
         "uom": uom,
         "rp_sqm_without_addon": round(rp_sqm_without_addon, 2),
         "rp_sqm": round(rp_sqm, 2),
         "total": round(total, 2),
         
         "addon_flag":addon_flag,
         "no_addon_flag": no_addon_flag,
         "quantity_addon": quantity_addon,
         "area_addon": area_addon,
         "aluminium_unit_price_addon": round(aluminium_unit_price_addon, 2),
         "infill_unit_price_addon": round(infill_unit_price_addon, 2),
         "accessory_unit_price_addon": round(accessory_unit_price_addon, 2),
         "sealant_unit_price_addon": round(sealant_unit_price_addon, 2),
         "cost_of_material_addon": round(cost_of_material_addon, 2),
         "labour_overhead_addon": round(labour_overhead_addon, 2),
         "sub_total_addon": round(sub_total_addon, 2),
         "addon_addon": round(addon_addon, 2),
         "tolerance_addon": round(tolerance_addon, 2),
         "uom_addon": uom_addon,
         "rp_sqm_without_addon_addon": round(rp_sqm_without_addon_addon, 2),
         "rp_sqm_addon": round(rp_sqm_addon, 2),
         "total_addon": round(total_addon, 2),
    }   
    return data


@register.simple_tag
def specification_summary_project_scope(request, pk):
    quantity = 0
    area = 0
    aluminium_unit_price = 0
    infill_unit_price = 0
    accessory_unit_price = 0
    sealant_unit_price = 0
    cost_of_material = 0
    labour_overhead = 0
    sub_total = 0
    addon= 0 
    tolerance = 0
    rp_sqm_without_addon = 0
    rp_sqm = 0
    total = 0
    
    addon_flag = 0
    no_addon_flag = 0
    
    quantity_addon = 0
    area_addon = 0
    aluminium_unit_price_addon = 0
    infill_unit_price_addon = 0
    sealant_unit_price_addon = 0
    accessory_unit_price_addon = 0
    cost_of_material_addon = 0
    labour_overhead_addon = 0
    sub_total_addon = 0
    addon_addon = 0 
    tolerance_addon = 0
    rp_sqm_without_addon_addon = 0
    rp_sqm_addon = 0
    total_addon = 0
    unit_price = 0
    addon_unit_price = 0
    
    uom_addon = None
    uom = None
    # PATHS = [
    #     '/Project/salesItem_specifications/',
    # ]
    
    sales_specification_obj = SalesOrderSpecification.objects.get(pk=pk)
    sales_objs = SalesOrderItems.objects.filter(specification_Identifier=sales_specification_obj)
    for sales_obj in sales_objs:
        if sales_obj.ref_product:
            MainProduct = EstimationMainProduct
            AluminiumModel = MainProductAluminium
            MainProductAddonCostModel = MainProductAddonCost

            
            products = MainProduct.objects.select_related('building', 'category').filter(specification_Identifier=pk, disabled=False).order_by('id')
            for product in products:
                addon_data = MainProductAddonCostModel.objects.filter(estimation_product=product)
                price_data = product_unit_price(request=request, pk=product.id)
                if product.building.typical_buildings_enabled:
                    typical_buildings = product.building.no_typical_buildings
                else:
                    typical_buildings = 1
                    
                if addon_data:
                    addon_flag += 1
                    if product.category.is_curtain_wall:
                        data = AluminiumModel.objects.get(estimation_product=product)
                        if product.category.is_curtain_wall:
                            if not product.after_deduction_price:
                                quantity_addon += (float(data.total_area) * float(typical_buildings))
                                area_addon += float(data.total_area) * float(typical_buildings)
                            else:
                                quantity_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                                area_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        elif product.category.handrail:
                            if not product.after_deduction_price:
                                quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                                area_addon += float(data.total_area) * float(typical_buildings)
                            else:
                                quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                                area_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        else:
                            if not product.after_deduction_price:
                                quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                                area_addon += float(data.total_area) * float(typical_buildings)
                            else:
                                quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                                area_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        
                                
                        if product.product_type == 2 :
                            if not product.main_product.have_merge:
                                aluminium_unit_price_addon += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                                infill_unit_price_addon += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                                accessory_unit_price_addon += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                                sealant_unit_price_addon += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                                cost_of_material_addon += (price_data['material_cost'] * float(typical_buildings))
                                labour_overhead_addon += (price_data['labour_overhead'] * float(typical_buildings))
                                sub_total_addon += (price_data['sub_total'] * float(typical_buildings))
                                addon_addon += (price_data['addon'] * float(typical_buildings))
                                tolerance_addon += (price_data['tolerance'] * float(typical_buildings))
                                rp_sqm_without_addon_addon += price_data['product_sqm_price_without_addon']
                                rp_sqm_addon += price_data['rp_sqm']
                                addon_unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))
                        else:
                            aluminium_unit_price_addon += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                            infill_unit_price_addon += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                            accessory_unit_price_addon += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                            sealant_unit_price_addon += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                            cost_of_material_addon += (price_data['material_cost'] * float(typical_buildings))
                            labour_overhead_addon += (price_data['labour_overhead'] * float(typical_buildings))
                            sub_total_addon += (price_data['sub_total'] * float(typical_buildings))
                            addon_addon += (price_data['addon'] * float(typical_buildings))
                            tolerance_addon += (price_data['tolerance'] * float(typical_buildings))
                            rp_sqm_without_addon_addon += price_data['product_sqm_price_without_addon']
                            rp_sqm_addon += price_data['rp_sqm']
                            addon_unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))
                        
                            
                        uom_addon = price_data['uom']
                        total_addon = addon_unit_price
                    else:
                        data = AluminiumModel.objects.get(estimation_product=product)
                        if product.category.is_curtain_wall:
                            if not product.after_deduction_price:
                                quantity_addon += (float(data.total_area) * float(typical_buildings))
                                area_addon += float(data.total_area) * float(data.total_quantity) * float(typical_buildings)
                            else:
                                quantity_addon +=  (float(data.total_area)-(float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings) 
                                area_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        elif product.category.handrail:
                            if not product.after_deduction_price:
                                quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                                area_addon += float(data.total_area) * float(typical_buildings)
                            else:
                                quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                                area_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        else:
                            if not product.after_deduction_price:
                                quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                                area_addon += float(data.total_area) * float(typical_buildings)
                            else:
                                quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                                area_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                                
                                
                        if product.product_type == 2 :
                            if not product.main_product.have_merge :
                                aluminium_unit_price_addon += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                                infill_unit_price_addon += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                                accessory_unit_price_addon += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                                sealant_unit_price_addon += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                                cost_of_material_addon += (price_data['material_cost'] * float(typical_buildings))
                                labour_overhead_addon += (price_data['labour_overhead'] * float(typical_buildings))
                                sub_total_addon += (price_data['sub_total'] * float(typical_buildings))
                                addon_addon += (price_data['addon'] * float(typical_buildings))
                                tolerance_addon += (price_data['tolerance'] * float(typical_buildings))
                                rp_sqm_without_addon_addon += price_data['product_sqm_price_without_addon']
                                rp_sqm_addon += price_data['rp_sqm']
                                addon_unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))
                        else:
                            aluminium_unit_price_addon += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                            infill_unit_price_addon += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                            accessory_unit_price_addon += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                            sealant_unit_price_addon += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                            cost_of_material_addon += (price_data['material_cost'] * float(typical_buildings))
                            labour_overhead_addon += (price_data['labour_overhead'] * float(typical_buildings))
                            sub_total_addon += (price_data['sub_total'] * float(typical_buildings))
                            addon_addon += (price_data['addon'] * float(typical_buildings))
                            tolerance_addon += (price_data['tolerance'] * float(typical_buildings))
                            rp_sqm_without_addon_addon += price_data['product_sqm_price_without_addon']
                            rp_sqm_addon += price_data['rp_sqm']
                            addon_unit_price += (float(math.ceil(price_data['unit_price_massupdate'])) * float(data.total_quantity) * float(typical_buildings))                               
                            
                        uom_addon = price_data['uom']
                        total_addon = addon_unit_price
                        
                else:
                    no_addon_flag += 1
                    if product.category.is_curtain_wall:
                        data = AluminiumModel.objects.get(estimation_product=product)
                        
                        if product.category.is_curtain_wall:
                            if not product.after_deduction_price:
                                quantity += (float(data.total_area) * float(typical_buildings))
                                area += float(data.total_area) * float(typical_buildings)
                            else:
                                quantity += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                                area += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                                
                        elif product.category.handrail:
                            if not product.after_deduction_price:
                                quantity += (float(data.total_quantity) * float(typical_buildings))
                                area += float(data.total_area) * float(typical_buildings)
                            else:
                                quantity += (float(data.total_quantity) * float(typical_buildings))
                                # area += (float(data.total_area) - float(product.deducted_area)) * float(typical_buildings)
                                area += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        else:
                            
                            if not product.after_deduction_price:
                                quantity += (float(data.total_quantity) * float(typical_buildings))
                                area += float(data.total_area) * float(typical_buildings)
                            else:
                                quantity += (float(data.total_quantity) * float(typical_buildings))
                                # area += (float(data.total_area) - float(product.deducted_area)) * float(typical_buildings)
                                area += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        
                        if product.product_type == 2 :
                            # if not product.main_product.have_merge:
                                aluminium_unit_price += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                                infill_unit_price += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                                accessory_unit_price += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                                sealant_unit_price += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                                cost_of_material += (price_data['material_cost'] * float(typical_buildings))
                                labour_overhead += (price_data['labour_overhead'] * float(typical_buildings))
                                sub_total += (price_data['sub_total'] * float(typical_buildings))
                                addon += (price_data['addon'] * float(typical_buildings))
                                tolerance += (price_data['tolerance'] * float(typical_buildings))
                                rp_sqm_without_addon += price_data['product_sqm_price_without_addon']
                                rp_sqm += price_data['rp_sqm']
                                unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))                                
                        else:
                            # if not product.have_merge:
                                aluminium_unit_price += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                                infill_unit_price += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                                accessory_unit_price += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                                sealant_unit_price += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                                cost_of_material += (price_data['material_cost'] * float(typical_buildings))
                                labour_overhead += (price_data['labour_overhead'] * float(typical_buildings))
                                sub_total += (price_data['sub_total'] * float(typical_buildings))
                                addon += (price_data['addon'] * float(typical_buildings))
                                tolerance += (price_data['tolerance'] * float(typical_buildings))
                                rp_sqm_without_addon += price_data['product_sqm_price_without_addon']
                                rp_sqm += price_data['rp_sqm']
                                unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))                                
                            # else:
                            #     aluminium_unit_price += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                            #     infill_unit_price += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                            #     accessory_unit_price += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                            #     sealant_unit_price += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                            #     cost_of_material += (price_data['material_cost'] * float(typical_buildings))
                            #     labour_overhead += (price_data['labour_overhead'] * float(typical_buildings))
                            #     sub_total += (price_data['sub_total'] * float(typical_buildings))
                            #     addon += (price_data['addon'] * float(typical_buildings))
                            #     tolerance += (price_data['tolerance'] * float(typical_buildings))
                            #     rp_sqm_without_addon += price_data['product_sqm_price_without_addon']
                            #     rp_sqm += price_data['rp_sqm']
                            #     unit_price += (float(math.ceil(price_data['unit_price_massupdate'])) * float(data.total_quantity) * float(typical_buildings))                                
                                
                            
                        uom = price_data['uom']
                        total = unit_price
                                        
                    else:
                        data = AluminiumModel.objects.get(estimation_product=product)
                        if product.category.is_curtain_wall:
                            if not product.after_deduction_price:
                                quantity += (float(data.total_area) * float(typical_buildings))
                                area += float(data.total_area) * float(typical_buildings)
                            else:
                                quantity += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                                # area += (float(data.total_area) - float(product.deducted_area)) * float(typical_buildings)
                                area += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                                
                        elif product.category.handrail:
                            if not product.after_deduction_price:
                                quantity += (float(data.total_quantity) * float(typical_buildings))
                                area += float(data.total_area) * float(typical_buildings)
                            else:
                                quantity += (float(data.total_quantity) * float(typical_buildings))
                                # area += (float(data.total_area) - float(product.deducted_area)) * float(typical_buildings)
                                area += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        else:
                            if not product.after_deduction_price:
                                quantity += (float(data.total_quantity) * float(typical_buildings))
                                area += float(data.total_area) * float(typical_buildings)
                            else:
                                quantity += (float(data.total_quantity) * float(typical_buildings))
                                # area += (float(data.total_area) - float(product.deducted_area)) * float(typical_buildings)
                                area += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                                
                        if product.product_type == 2 :
                            # if not product.main_product.have_merge:
                                aluminium_unit_price += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                                infill_unit_price += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                                accessory_unit_price += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                                sealant_unit_price += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                                cost_of_material += (price_data['material_cost'] * float(typical_buildings))
                                labour_overhead += (price_data['labour_overhead'] * float(typical_buildings))
                                sub_total += (price_data['sub_total'] * float(typical_buildings))
                                addon += (price_data['addon'] * float(typical_buildings))
                                tolerance += (price_data['tolerance'] * float(typical_buildings))
                                rp_sqm_without_addon += price_data['product_sqm_price_without_addon']
                                rp_sqm += price_data['rp_sqm']
                                unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))                          
                        else:
                            # if not product.have_merge:
                                aluminium_unit_price += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                                infill_unit_price += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                                accessory_unit_price += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                                sealant_unit_price += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                                cost_of_material += (price_data['material_cost'] * float(typical_buildings))
                                labour_overhead += (price_data['labour_overhead'] * float(typical_buildings))
                                sub_total += (price_data['sub_total'] * float(typical_buildings))
                                addon += (price_data['addon'] * float(typical_buildings))
                                tolerance += (price_data['tolerance'] * float(typical_buildings))
                                rp_sqm_without_addon += price_data['product_sqm_price_without_addon']
                                rp_sqm += price_data['rp_sqm']
                                unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))                          
                            # else:
                            #     aluminium_unit_price += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                            #     infill_unit_price += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                            #     accessory_unit_price += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                            #     sealant_unit_price += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                            #     cost_of_material += (price_data['material_cost'] * float(typical_buildings))
                            #     labour_overhead += (price_data['labour_overhead'] * float(typical_buildings))
                            #     sub_total += (price_data['sub_total'] * float(typical_buildings))
                            #     addon += (price_data['addon'] * float(typical_buildings))
                            #     tolerance += (price_data['tolerance'] * float(typical_buildings))
                            #     rp_sqm_without_addon += price_data['product_sqm_price_without_addon']
                            #     rp_sqm += price_data['rp_sqm']
                            #     unit_price += (float(math.ceil(price_data['unit_price_massupdate'])) * float(data.total_quantity) * float(typical_buildings))                          
                                                    
                            
                        uom = price_data['uom']
                        total = unit_price
                            
            data = {
                "quantity": quantity,
                "area": area,
                "aluminium_unit_price": round(aluminium_unit_price, 2),
                "infill_unit_price": round(infill_unit_price, 2),
                "accessory_unit_price": round(accessory_unit_price, 2),
                "sealant_unit_price": round(sealant_unit_price, 2),
                "cost_of_material": round(cost_of_material, 2),
                "labour_overhead": round(labour_overhead, 2),
                "sub_total": round(sub_total, 2),
                "addon": round(addon, 2),
                "tolerance": round(tolerance, 2),
                "uom": uom,
                "rp_sqm_without_addon": round(rp_sqm_without_addon, 2),
                "rp_sqm": round(rp_sqm, 2),
                "total": round(total, 2),
                
                "addon_flag":addon_flag,
                "no_addon_flag": no_addon_flag,
                "quantity_addon": quantity_addon,
                "area_addon": area_addon,
                "aluminium_unit_price_addon": round(aluminium_unit_price_addon, 2),
                "infill_unit_price_addon": round(infill_unit_price_addon, 2),
                "accessory_unit_price_addon": round(accessory_unit_price_addon, 2),
                "sealant_unit_price_addon": round(sealant_unit_price_addon, 2),
                "cost_of_material_addon": round(cost_of_material_addon, 2),
                "labour_overhead_addon": round(labour_overhead_addon, 2),
                "sub_total_addon": round(sub_total_addon, 2),
                "addon_addon": round(addon_addon, 2),
                "tolerance_addon": round(tolerance_addon, 2),
                "uom_addon": uom_addon,
                "rp_sqm_without_addon_addon": round(rp_sqm_without_addon_addon, 2),
                "rp_sqm_addon": round(rp_sqm_addon, 2),
                "total_addon": round(total_addon, 2),
            }  
                
        else:
            ...

    
     
    return data



@register.simple_tag
def overview_scope_specification_unit(request, version, t_type=None):
    quantity = 0
    area = 0
    aluminium_unit_price = 0
    infill_unit_price = 0
    accessory_unit_price = 0
    sealant_unit_price = 0
    cost_of_material = 0
    labour_overhead = 0
    sub_total = 0
    addon= 0 
    tolerance = 0
    rp_sqm_without_addon = 0
    rp_sqm = 0
    total = 0
    
    addon_flag = 0
    no_addon_flag = 0
    
    quantity_addon = 0
    area_addon = 0
    aluminium_unit_price_addon = 0
    infill_unit_price_addon = 0
    sealant_unit_price_addon = 0
    accessory_unit_price_addon = 0
    cost_of_material_addon = 0
    labour_overhead_addon = 0
    sub_total_addon = 0
    addon_addon = 0 
    tolerance_addon = 0
    rp_sqm_without_addon_addon = 0
    rp_sqm_addon = 0
    total_addon = 0
    unit_price = 0
    addon_unit_price = 0
    
    uom_addon = None
    uom = None
    
    PATHS = [
        '/Estimation/specification_wise_scope_summary_unit_price/',
        
        '/Estimation/building_category_summary/',
        '/Estimation/estimation_list_enquiry/',
        '/Estimation/estimation_list_by_boq_enquiry/',
        '/Project/project_scop/',
        '/Project/project_contract_items/',
        '/Estimation/summary_view_all/',
        '/Estimation/specification_wise_scope_summary/',
        '/Estimation/specification_scope_summary_print/',
        '/Estimation/consolidate_scope_summary_print/',
        '/Project/salesItem_specifications/',
        
    ]
    if any(path in request.path for path in PATHS):
        MainProduct = EstimationMainProduct
        AluminiumModel = MainProductAluminium
        MainProductAddonCostModel = MainProductAddonCost
        
    else:
        MainProduct = Temp_EstimationMainProduct
        AluminiumModel = Temp_MainProductAluminium
        MainProductAddonCostModel = Temp_MainProductAddonCost
    
    products = MainProduct.objects.select_related('building', 'category').filter(specification_Identifier=pk, disabled=False).order_by('id')
    for product in products:
        addon_data = MainProductAddonCostModel.objects.filter(estimation_product=product)
        price_data = product_unit_price(request=request, pk=product.id)
        
        if product.building.typical_buildings_enabled:
            typical_buildings = product.building.no_typical_buildings
        else:
            typical_buildings = 1
            
        if addon_data:
            addon_flag += 1
            if product.category.is_curtain_wall:
                data = AluminiumModel.objects.get(estimation_product=product)
                if product.category.is_curtain_wall:
                    if not product.after_deduction_price:
                        quantity_addon += (float(data.total_area) * float(typical_buildings))
                        area_addon += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        area_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        
                elif product.category.handrail:
                    if not product.after_deduction_price:
                        quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                        area_addon += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                        area_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                else:
                    if not product.after_deduction_price:
                        quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                        area_addon += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                        area_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                
                        
                if product.product_type == 2 :
                    if not product.main_product.have_merge:
                        aluminium_unit_price_addon += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price_addon += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price_addon += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price_addon += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material_addon += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead_addon += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total_addon += (price_data['sub_total'] * float(typical_buildings))
                        addon_addon += (price_data['addon'] * float(typical_buildings))
                        tolerance_addon += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm_addon += price_data['rp_sqm']
                        addon_unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))
                else:
                    # if not product.have_merge:
                        aluminium_unit_price_addon += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price_addon += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price_addon += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price_addon += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material_addon += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead_addon += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total_addon += (price_data['sub_total'] * float(typical_buildings))
                        addon_addon += (price_data['addon'] * float(typical_buildings))
                        tolerance_addon += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm_addon += price_data['rp_sqm']
                        addon_unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))
                        
                uom_addon = price_data['uom']
                total_addon = addon_unit_price
                
                
            else:
                data = AluminiumModel.objects.get(estimation_product=product)
                if product.category.is_curtain_wall:
                    if not product.after_deduction_price:
                        quantity_addon += (float(data.total_area) * float(typical_buildings))
                        area_addon += float(data.total_area) * float(data.total_quantity) * float(typical_buildings)
                    else:
                        quantity_addon +=  (float(data.total_area)-(float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings) 
                        area_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                elif product.category.handrail:
                    if not product.after_deduction_price:
                        quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                        area_addon += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                        area_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                else:
                    if not product.after_deduction_price:
                        quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                        area_addon += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity_addon += (float(data.total_quantity) * float(typical_buildings))
                        area_addon += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        
                        
                if product.product_type == 2 :
                    if not product.main_product.have_merge :
                        aluminium_unit_price_addon += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price_addon += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price_addon += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price_addon += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material_addon += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead_addon += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total_addon += (price_data['sub_total'] * float(typical_buildings))
                        addon_addon += (price_data['addon'] * float(typical_buildings))
                        tolerance_addon += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm_addon += price_data['rp_sqm']
                        addon_unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))
                else:
                    
                        aluminium_unit_price_addon += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price_addon += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price_addon += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price_addon += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material_addon += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead_addon += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total_addon += (price_data['sub_total'] * float(typical_buildings))
                        addon_addon += (price_data['addon'] * float(typical_buildings))
                        tolerance_addon += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm_addon += price_data['rp_sqm']
                        addon_unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))                               
                    
                uom_addon = price_data['uom']
                total_addon = addon_unit_price
                
        else:
            no_addon_flag += 1
            if product.category.is_curtain_wall:
                data = AluminiumModel.objects.get(estimation_product=product)
                
                if product.category.is_curtain_wall:
                    if not product.after_deduction_price:
                        quantity += (float(data.total_area) * float(typical_buildings))
                        area += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        area += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        
                elif product.category.handrail:
                    if not product.after_deduction_price:
                        quantity += (float(data.total_quantity) * float(typical_buildings))
                        area += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity += (float(data.total_quantity) * float(typical_buildings))
                        # area += (float(data.total_area) - float(product.deducted_area)) * float(typical_buildings)
                        area += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                else:
                    
                    if not product.after_deduction_price:
                        quantity += (float(data.total_quantity) * float(typical_buildings))
                        area += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity += (float(data.total_quantity) * float(typical_buildings))
                        # area += (float(data.total_area) - float(product.deducted_area)) * float(typical_buildings)
                        area += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                
                if product.product_type == 2 :
                    if not product.main_product.have_merge:
                        aluminium_unit_price += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total += (price_data['sub_total'] * float(typical_buildings))
                        addon += (price_data['addon'] * float(typical_buildings))
                        tolerance += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm += price_data['rp_sqm']
                        unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))        
                        
                else:
                    # if not product.have_merge:
                        aluminium_unit_price += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total += (price_data['sub_total'] * float(typical_buildings))
                        addon += (price_data['addon'] * float(typical_buildings))
                        tolerance += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm += price_data['rp_sqm']
                        unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings)) 
                    
                    
                uom = price_data['uom']
                total = unit_price
                
                                
            else:
                data = AluminiumModel.objects.get(estimation_product=product)
                if product.category.is_curtain_wall:
                    if not product.after_deduction_price:
                        quantity += (float(data.total_area) * float(typical_buildings))
                        area += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        # area += (float(data.total_area) - float(product.deducted_area)) * float(typical_buildings)
                        area += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        
                elif product.category.handrail:
                    if not product.after_deduction_price:
                        quantity += (float(data.total_quantity) * float(typical_buildings))
                        area += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity += (float(data.total_quantity) * float(typical_buildings))
                        # area += (float(data.total_area) - float(product.deducted_area)) * float(typical_buildings)
                        area += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                else:
                    if not product.after_deduction_price:
                        quantity += (float(data.total_quantity) * float(typical_buildings))
                        area += float(data.total_area) * float(typical_buildings)
                    else:
                        quantity += (float(data.total_quantity) * float(typical_buildings))
                        # area += (float(data.total_area) - float(product.deducted_area)) * float(typical_buildings)
                        area += (float(data.total_area) - (float(product.deducted_area) * float(data.total_quantity))) * float(typical_buildings)
                        
                if product.product_type == 2 :
                    if not product.main_product.have_merge:
                        aluminium_unit_price += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total += (price_data['sub_total'] * float(typical_buildings))
                        addon += (price_data['addon'] * float(typical_buildings))
                        tolerance += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm += price_data['rp_sqm']
                        unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))                          
                else:
                    # if not product.have_merge:
                        aluminium_unit_price += (float(price_data['aluminium_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        infill_unit_price += (float(price_data['glass_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        accessory_unit_price += (float(price_data['accessory_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        sealant_unit_price += (float(price_data['sealant_unit_price']) * float(data.total_quantity) * float(typical_buildings))
                        cost_of_material += (price_data['material_cost'] * float(typical_buildings))
                        labour_overhead += (price_data['labour_overhead'] * float(typical_buildings))
                        sub_total += (price_data['sub_total'] * float(typical_buildings))
                        addon += (price_data['addon'] * float(typical_buildings))
                        tolerance += (price_data['tolerance'] * float(typical_buildings))
                        rp_sqm_without_addon += price_data['product_sqm_price_without_addon']
                        rp_sqm += price_data['rp_sqm']
                        unit_price += (float(math.ceil(price_data['unit_price'])) * float(data.total_quantity) * float(typical_buildings))  
                                
                    
                uom = price_data['uom']
                total = unit_price
                
    
            
    data = {
            "quantity": quantity,
            "area": area,
            "aluminium_unit_price": round(aluminium_unit_price, 2),
            "infill_unit_price": round(infill_unit_price, 2),
            "accessory_unit_price": round(accessory_unit_price, 2),
            "sealant_unit_price": round(sealant_unit_price, 2),
            "cost_of_material": round(cost_of_material, 2),
            "labour_overhead": round(labour_overhead, 2),
            "sub_total": round(sub_total, 2),
            "addon": round(addon, 2),
            "tolerance": round(tolerance, 2),
            "uom": uom,
            "rp_sqm_without_addon": round(rp_sqm_without_addon, 2),
            "rp_sqm": round(rp_sqm, 2),
            "total": round(total, 2),
            
            "addon_flag":addon_flag,
            "no_addon_flag": no_addon_flag,
            "quantity_addon": quantity_addon,
            "area_addon": area_addon,
            "aluminium_unit_price_addon": round(aluminium_unit_price_addon, 2),
            "infill_unit_price_addon": round(infill_unit_price_addon, 2),
            "accessory_unit_price_addon": round(accessory_unit_price_addon, 2),
            "sealant_unit_price_addon": round(sealant_unit_price_addon, 2),
            "cost_of_material_addon": round(cost_of_material_addon, 2),
            "labour_overhead_addon": round(labour_overhead_addon, 2),
            "sub_total_addon": round(sub_total_addon, 2),
            "addon_addon": round(addon_addon, 2),
            "tolerance_addon": round(tolerance_addon, 2),
            "uom_addon": uom_addon,
            "rp_sqm_without_addon_addon": round(rp_sqm_without_addon_addon, 2),
            "rp_sqm_addon": round(rp_sqm_addon, 2),
            "total_addon": round(total_addon, 2),
    }   
    return data
    
    






