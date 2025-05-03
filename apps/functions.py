import math
import random, os, io, re
from django.template.loader import get_template
from django.utils.timezone import now as time
from django.db.models import F, Func, Sum
from django.shortcuts import render, redirect, get_object_or_404


from apps.accessories_kit.models import AccessoriesKit, AccessoriesKitItem
from apps.customers.models import Customers
from apps.enquiries.models import (
        Enquiries, 
        EnquirySpecifications,
        EnquiryUser, 
        Estimations, 
        Pricing_Summary, 
        Temp_EnquirySpecifications, 
        Temp_Estimations, 
        Temp_Pricing_Summary,
)

from apps.estimations.models import (
        AuditLogModel,
        Estimation_UserTimes,
        EstimationMainProduct, 
        EstimationMainProductMergeData, 
        EstimationProduct_Associated_Data,
        MainProductAccessories, 
        MainProductAluminium, 
        MainProductGlass, 
        MainProductAddonCost, 
        MainProductSilicon, 
        PricingOption, 
        EstimationBuildings, 
        Quotation_Notes,
        Quotation_Provisions, 
        Quotations,
        Temp_AuditLogModel, 
        Temp_Deduction_Items, 
        Temp_Estimation_GeneralNotes, 
        Temp_EstimationBuildings, 
        Temp_EstimationMainProduct, 
        Temp_EstimationMainProductMergeData, 
        Temp_EstimationProduct_Associated_Data, 
        Temp_EstimationProductComplaints,
        Temp_EstimationProjectSpecifications, 
        Temp_MainProductAccessories, 
        Temp_MainProductAddonCost, 
        Temp_MainProductAluminium, 
        Temp_MainProductGlass, 
        Temp_MainProductSecondtaryGlass, 
        Temp_MainProductSilicon, 
        Temp_PricingOption, 
        Temp_ProductComments, 
        Temp_Quotation_Notes, 
        Temp_Quotation_Notes_Comments, 
        Temp_Quotation_Provisions, 
        Temp_Quotations,
)
from apps.estimations.templatetags.assocciated_data import have_deducted_associated

from apps.helper import enquiry_logger
from apps.others.models import (
    AI_RatingModel, 
    Labour_and_OverheadMaster,
)
from apps.pricing_master.models import PriceMaster
from apps.product_master.models import Product_WorkStations
from amoeba.settings import MEDIA_URL, PROJECT_NAME
from apps.suppliers.models import BillofQuantity
from wkhtmltopdf.views import PDFTemplateResponse


def calculate_kit_total(kit_id):
    """
        This function calculates the total cost of all items in an accessories kit.
    """
    accessory = AccessoriesKit.objects.get(pk=kit_id)
    kit_obj = AccessoriesKitItem.objects.filter(accessory_kit=accessory)
    total = 0
    for kit_item in kit_obj:
        total += kit_item.kit_item_total
    return total


def main_product_duplicate(request, pk, data, associated_key):
    """
    This function duplicates a main product and its associated objects with updated data.
    """
    try:
        PATHS = [
            '/Enquiries/product_duplicate/',
            '/Estimation/multiple_scope_add/',
        ]
        if any(path in request.path for path in PATHS):
            MainProduct = EstimationMainProduct
            Accessories = MainProductAccessories
            Aluminium = MainProductAluminium
            Glass = MainProductGlass
            Silicon = MainProductSilicon
            AddonCost = MainProductAddonCost
            pricing = PricingOption
        else:
            MainProduct = Temp_EstimationMainProduct
            Accessories = Temp_MainProductAccessories
            Aluminium = Temp_MainProductAluminium
            Glass = Temp_MainProductGlass
            Silicon = Temp_MainProductSilicon
            AddonCost = Temp_MainProductAddonCost
            pricing = Temp_PricingOption

        main_product_obj = MainProduct.objects.get(pk=pk)
        main_product_obj.pk = None
        main_product_obj.created_date = time()
        main_product_obj.building_id = data['building']
        main_product_obj.save()
        main_product_obj.main_product = main_product_obj
        main_product_obj.associated_key = str(associated_key) + str(main_product_obj.id)
        main_product_obj.save()

        accessory_obj = Accessories.objects.filter(estimation_product=pk)
        for accessory in accessory_obj:
            accessory.pk = None
            accessory.estimation_product = main_product_obj
            accessory.created_date = time()
            accessory.save()
        
        alumin_obj = Aluminium.objects.get(estimation_product=pk)
        alumin_obj.pk = None
        alumin_obj.estimation_product = main_product_obj
        alumin_obj.created_date = time()
        if data.get('width'):
            alumin_obj.width = float(data['width'])
        if data.get('height'):
            alumin_obj.height = float(data['height'])
        alumin_obj.area = float(data['new_area'])
        alumin_obj.quantity = float(data['quantity'])
        alumin_obj.total_quantity = float(data['quantity'])
        alumin_obj.total_area = float(data['new_area']) * float(data['quantity'])
        if data.get('new_al_quoted_price'):
            alumin_obj.al_quoted_price = math.ceil(float(data['new_al_quoted_price']))
        if data.get('new_al_total_weight'):
            alumin_obj.total_weight = float(data['new_al_total_weight'])
        alumin_obj.product_type = data['product_type']
        alumin_obj.product_description = data['product_description']
        alumin_obj.enable_divisions = data.get('enable_divisions') == 'on'
        alumin_obj.horizontal = data.get('horizontal')
        alumin_obj.vertical = data.get('vertical')
        alumin_obj.total_linear_meter = data.get('new_total_linear_meter')
        alumin_obj.weight_per_unit = data.get('new_unit_weight')
        alumin_obj.save()

        try:
            glass_obj = Glass.objects.get(estimation_product=pk, glass_primary=True)
            glass_obj.pk = None
            glass_obj.estimation_product = main_product_obj
            glass_obj.created_date = time()
            glass_obj.total_area_glass = float(data['new_area'])
            glass_obj.glass_quoted_price = math.ceil(float(data['new_glass_quoted_price']))
            glass_obj.save()
        except Exception:
            pass

        second_glass_obj = Glass.objects.filter(estimation_product=pk, glass_primary=False)
        for second_glass in second_glass_obj:
            second_glass.pk = None
            second_glass.estimation_product = main_product_obj
            second_glass.created_date = time()
            second_glass.save()
            
        try:
            silicon_obj = Silicon.objects.get(estimation_product=pk)
            silicon_obj.pk = None
            silicon_obj.estimation_product = main_product_obj
            silicon_obj.created_date = time()
            silicon_obj.external_lm = float(data['external_lm']) if data.get('external_lm') else float(0)
            silicon_obj.internal_lm = float(data['internal_lm']) if data.get('internal_lm') else float(0)
            silicon_obj.polyamide_lm = float(data['polyamide_lm']) if data.get('polyamide_lm') else float(0)
            silicon_obj.transom_lm = float(data['transom_lm']) if data.get('transom_lm') else float(0)
            silicon_obj.mullion_lm = float(data['mullion_lm']) if data.get('mullion_lm') else float(0)
            # silicon_obj.epdm_lm = float(data['epdm_lm']) if data.get('epdm_lm') else None
            silicon_obj.silicon_quoted_price = math.ceil(float(data['sealant_quote_price'])) if data.get('sealant_quote_price') else None
            silicon_obj.save()
        except Exception:
            pass

        addon_obj = AddonCost.objects.filter(estimation_product=pk)
        addon_unit_cost = 0
        for addon in addon_obj:
            addon.pk = None
            addon_baserate = float(addon.base_rate)
            if addon.pricing_type == 1:
                unit_lm = float(data['external_lm']) + float(data['internal_lm'])
                addon.addon_quantity = unit_lm
                addon_unit_cost += addon_baserate*unit_lm
            elif addon.pricing_type == 2:
                addon.addon_quantity = float(data['new_area'])
                addon_unit_cost += addon_baserate*float(data['new_area'])
            elif addon.pricing_type == 3:
                addon.addon_quantity = addon.addon_quantity
                addon_unit_cost += addon_baserate*float(addon.addon_quantity)

            addon.estimation_product = main_product_obj
            addon.created_date = time()
            addon.save()

        main_product_obj.total_addon_cost = math.ceil(addon_unit_cost)
        pricing_obj = pricing.objects.get(estimation_product=pk)
        pricing_obj.pk = None
        pricing_obj.estimation_product = main_product_obj
        pricing_obj.created_date = time()
        pricing_obj.save()

    except Exception as e:
        print("Exception:", e)
        
    
    main_productminimum_price = min_price_setup(request, main_product_obj.id)
    main_product_obj.minimum_price = main_productminimum_price
    main_product_obj.product_index = set_index(request, main_product_obj.building.id)
    main_product_obj.save()
    return main_product_obj


def building_duplicate_function(request, pk):
    """
    This function duplicates a building and its associated products and accessories in the original or
    temporary database.
    """
    if '/Enquiries/building_duplicate/' in request.path:
        BuildingModel = EstimationBuildings
        MainProductModel = EstimationMainProduct
        AccessoriesModel = MainProductAccessories
        AluminiumModel = MainProductAluminium
        GlassModel = MainProductGlass
        SiliconModel = MainProductSilicon
        AddonCostModel = MainProductAddonCost
        PricingOptionModel = PricingOption
        AssociatedDataModel = EstimationProduct_Associated_Data
    else:
        BuildingModel = Temp_EstimationBuildings
        MainProductModel = Temp_EstimationMainProduct
        AccessoriesModel = Temp_MainProductAccessories
        AluminiumModel = Temp_MainProductAluminium
        GlassModel = Temp_MainProductGlass
        SiliconModel = Temp_MainProductSilicon
        AddonCostModel = Temp_MainProductAddonCost
        PricingOptionModel = Temp_PricingOption
        AssociatedDataModel = Temp_EstimationProduct_Associated_Data
        
    building = BuildingModel.objects.get(pk=pk)
    building.pk = None
    building.created_date = time()
    building.save()
    
    main_product = MainProductModel.objects.filter(building=pk, product_type=1).order_by('id')
    for products in main_product:
        
        associated = MainProductModel.objects.filter(
            main_product=products, product_type=2).order_by('id')
        product_id = products.id
        prev_main_id = None
        try:
            products.pk = None
            products.created_date = time()
            products.building = building
            products.save()
            products.main_product = products
            products.save()
            prev_main_id = products

            try:
                accessory_obj = AccessoriesModel.objects.filter(
                    estimation_product=product_id)
                for accessory in accessory_obj:
                    accessory.pk = None
                    accessory.estimation_product = products
                    accessory.created_date = time()
                    accessory.save()
            except Exception as e:
                print("AccessoriesKit Exception: ", e)

            alumin_obj = AluminiumModel.objects.get(
                estimation_product=product_id)
            alumin_obj.pk = None
            alumin_obj.estimation_product = products
            alumin_obj.created_date = time()
            alumin_obj.save()
            try:
                glass_obj = GlassModel.objects.get(
                    estimation_product=product_id, glass_primary=True)
                glass_obj.pk = None
                glass_obj.estimation_product = products
                glass_obj.created_date = time()
                glass_obj.save()
            except Exception as e:
                print('main Exception n glass==>', e)
            try:
                second_glass_obj = GlassModel.objects.filter(
                    estimation_product=product_id, glass_primary=False).order_by('id')
                for second_glass in second_glass_obj:
                    second_glass.pk = None
                    second_glass.estimation_product = products
                    second_glass.created_date = time()
                    second_glass.save()
            except Exception as e:
                print("main EXCEPTIOPN as second_glass==>", e)
            try:
                silicon_obj = SiliconModel.objects.filter(
                    estimation_product=product_id).order_by('id')
                for silicon in silicon_obj:
                    silicon.pk = None
                    silicon.estimation_product = products
                    silicon.created_date = time()
                    silicon.save()
            except Exception as e:
                print("main EXCEPTION silicon_obj==>", e)

            try:
                addon_obj = AddonCostModel.objects.filter(
                    estimation_product=product_id).order_by('id')
                for addon in addon_obj:
                    addon.pk = None
                    addon.estimation_product = products
                    addon.created_date = time()
                    addon.save()
            except Exception as e:
                print('main EXCEPTIOn addon ==>', e)
            pricing_obj = PricingOptionModel.objects.get(
                estimation_product=product_id)
            pricing_obj.pk = None
            pricing_obj.estimation_product = products
            pricing_obj.created_date = time()
            pricing_obj.save()
            
            main_productminimum_price = min_price_setup(request, products.id)
            products.minimum_price = main_productminimum_price
            products.save()
            
            
        
            
        except Exception as e:
            print('main Exception priceing option Main==>', e)

        if associated:
            for associated_product in associated:
                product_id = associated_product.id
                try:
                    associated_product = associated_product
                    associated_product.pk = None
                    associated_product.created_date = time()
                    associated_product.building = building
                    associated_product.main_product = prev_main_id
                    associated_product.save()
                except Exception as e:
                    print('Exception associate ==>', e)

                try:
                    accessory_obj = AccessoriesModel.objects.filter(
                        estimation_product=product_id)
                    for accessory in accessory_obj:
                        accessory.pk = None
                        accessory.estimation_product = associated_product
                        accessory.created_date = time()
                        accessory.save()
                except Exception as e:
                    print("AccessoriesKit Exception: ", e)

                try:
                    alumin_obj = AluminiumModel.objects.get(
                        estimation_product=product_id)
                    alumin_obj.pk = None
                    alumin_obj.estimation_product = associated_product
                    alumin_obj.created_date = time()
                    alumin_obj.save()
                except Exception as e:
                    print('Exception associate Alum==>', e)
                try:
                    glass_obj = GlassModel.objects.get(
                        estimation_product=product_id, glass_primary=True)
                    glass_obj.pk = None
                    glass_obj.estimation_product = associated_product
                    glass_obj.created_date = time()
                    glass_obj.save()
                except Exception as e:
                    print('EXCEPTION associate glass==>', e)

                try:
                    second_glass_obj = GlassModel.objects.filter(
                        estimation_product=product_id, glass_primary=False)
                    for second_glass in second_glass_obj:
                        second_glass.pk = None
                        second_glass.estimation_product = associated_product
                        second_glass.created_date = time()
                        second_glass.save()
                except Exception as e:
                    print("EXCEPTION in associated secod glass==>", e)

                try:
                    silicon_obj = SiliconModel.objects.filter(
                        estimation_product=product_id).order_by('id')
                    for silicon in silicon_obj:
                        silicon.pk = None
                        silicon.estimation_product = associated_product
                        silicon.created_date = time()
                        silicon.save()
                except Exception as e:
                    print("EXCEPTION in associated silicon==>", e)

                try:
                    addon_obj = AddonCostModel.objects.filter(
                        estimation_product=product_id).order_by('id')
                    for addon in addon_obj:
                        addon.pk = None
                        addon.estimation_product = associated_product
                        addon.created_date = time()
                        addon.save()
                except Exception as e:
                    print("EXCEPTION in associated addon==>", e)

                associated_datas = AssociatedDataModel.objects.filter(
                    associated_product=product_id)
                for associated_data in associated_datas:
                    associated_data.pk = None
                    associated_data.estimation_main_product = prev_main_id
                    associated_data.associated_product = associated_product
                    associated_data.save()
                try:
                    pricing_obj = PricingOptionModel.objects.get(
                        estimation_product=product_id)
                    pricing_obj.pk = None
                    pricing_obj.estimation_product = associated_product
                    pricing_obj.created_date = time()
                    pricing_obj.save()
                except Exception as e:
                    print("Exception in associated pricing_obj==>", e)
                    
                main_productminimum_price = min_price_setup(request, associated_product.id)
                associated_product.minimum_price = main_productminimum_price
                associated_product.save()
    
    update_pricing_summary(request, pk=building.estimation.id)
    enquiry_logger(enquiry=building.estimation.enquiry, message= building.building_name+' Building Duplicated in Original.' if building.estimation.version.version == '0' else building.building_name+' Building Duplicated in Revision '+str(building.estimation.version.version), action=1, user=request.user)
    
    return True


def clear_temp(pk):
    """
    This function clears all temporary data related to a given primary key.
    """
    try:
        temp_estimations = Temp_Estimations.objects.get(pk=pk)
        temp_quotations = Temp_Quotations.objects.filter(
            estimations=temp_estimations)
        for quotation in temp_quotations:
            quotation_notes = Temp_Quotation_Notes.objects.filter(quotation=quotation)
            for note in quotation_notes:
                Temp_Quotation_Notes_Comments.objects.filter(quotation_note=note).delete()
            quotation_notes.delete()
        for temp_quotation in temp_quotations:
            provisions = Temp_Quotation_Provisions.objects.filter(
                quotation=temp_quotation).delete()
            Temp_Quotation_Notes.objects.filter(quotation=temp_quotation).delete()
        temp_quotations.delete()
        
        Temp_EstimationProductComplaints.objects.filter(estimation=temp_estimations).delete()
        Temp_Quotation_Notes.objects.filter(quotation__estimations=temp_estimations).delete()
        Temp_EstimationProjectSpecifications.objects.filter(estimations=temp_estimations).delete()
        Temp_Quotation_Notes_Comments.objects.filter(quotation_note__quotation__estimations=temp_estimations).delete()
        Temp_Estimation_GeneralNotes.objects.get(estimations=temp_estimations).delete()
        Temp_Pricing_Summary.objects.get(estimation=temp_estimations).delete()
        Temp_AuditLogModel.objects.filter(estimation=temp_estimations).delete()

    except Exception as e:
        print("Exception Temp clear==>", e)
        
    try:
        _extracted_from_clear_temp_30(temp_estimations)
    except Exception as r:
        print("Exception TEmpS Clear ==>", r)


def _extracted_from_clear_temp_30(temp_estimations):
    temp_specification = Temp_EnquirySpecifications.objects.filter(
        estimation=temp_estimations)
    temp_building = Temp_EstimationBuildings.objects.filter(
        estimation=temp_estimations)
    for building in temp_building:
        temp_main_products = Temp_EstimationMainProduct.objects.filter(
            building__estimation=building.estimation)
        for products in temp_main_products:
            temp_addons = Temp_MainProductAddonCost.objects.filter(
                estimation_product=products).delete()
            temp_pricing = Temp_PricingOption.objects.filter(
                estimation_product=products).delete()
            temp_glass = Temp_MainProductGlass.objects.filter(
                estimation_product=products).delete()
            temp_silicon = Temp_MainProductSilicon.objects.filter(
                estimation_product=products).delete()
            temp_alumi = Temp_MainProductAluminium.objects.filter(
                estimation_product=products).delete()
            temp_comments = Temp_ProductComments.objects.filter(
                product=products).delete()
            temp_accessories = Temp_MainProductAccessories.objects.filter(
                estimation_product=products).delete()
            temp_associated_data = Temp_EstimationProduct_Associated_Data.objects.filter(
                estimation_main_product=products).delete()
            temp_deduction = Temp_Deduction_Items.objects.filter(estimation_product=products).delete()
            temp_merge = Temp_EstimationMainProductMergeData.objects.filter(estimation_product=products).delete()
        temp_main_products.delete()
    temp_building.delete()
    temp_specification.delete()
    temp_estimations.delete()


def submit_temp_glass(request, main_product_id, temp=None):
    """
    This function submits temporary secondary glass data to the main product glass model and deletes the
    temporary data.
    """
    
    temp_secondary_glass = Temp_MainProductSecondtaryGlass.objects.filter(
        created_by=request.user)
    if not temp:
        for temp_glass in temp_secondary_glass:
            glass_obj = MainProductGlass(
                estimation_product_id=main_product_id, is_glass_cost=temp_glass.sec_is_glass_cost, 
                glass_specif=temp_glass.sec_glass_specif, total_area_glass=temp_glass.sec_total_area, 
                glass_quoted_price=temp_glass.sec_quoted_price, glass_pricing_type=temp_glass.sec_glass_pricing_type,
                glass_primary=False, glass_width=temp_glass.sec_width, glass_height=temp_glass.sec_height, 
                glass_area=temp_glass.sec_area, glass_quantity=temp_glass.sec_quantity, glass_base_rate=temp_glass.sec_base_rate, 
                glass_markup_percentage=temp_glass.sec_markup_percentage
                # , glass_price_per_sqm=temp_glass.sec_price_per_sqm
            )
            glass_obj.save()
            temp_glass.delete()
    else:
        for temp_glass in temp_secondary_glass:
            glass_obj = Temp_MainProductGlass(
                estimation_product_id=main_product_id, is_glass_cost=temp_glass.sec_is_glass_cost, 
                glass_specif=temp_glass.sec_glass_specif, total_area_glass=temp_glass.sec_total_area, 
                glass_quoted_price=temp_glass.sec_quoted_price, glass_pricing_type=temp_glass.sec_glass_pricing_type,
                glass_primary=False, glass_width=temp_glass.sec_width, glass_height=temp_glass.sec_height, 
                glass_area=temp_glass.sec_area, glass_quantity=temp_glass.sec_quantity, glass_base_rate=temp_glass.sec_base_rate, 
                glass_markup_percentage=temp_glass.sec_markup_percentage
                # , glass_price_per_sqm=temp_glass.sec_price_per_sqm
            )
            glass_obj.save()
            temp_glass.delete()
        


def product_unit_price(request=None, pk=None, edit=None):
    """
    This function calculates various pricing and cost values for a given product based on its attributes
    and pricing options.
    """
    PATHS = [
        '/Estimation/product_merge_summary/',
        '/Estimation/add_estimation_pricing/',
        '/Estimation/edit_estimation_pricing/',
        '/Estimation/add_associated_product/',
        '/Estimation/merge_summary_print/',
        '/Enquiries/product_category_summary/',
        '/Enquiries/edit_enq_specifications/',
        '/Estimation/merge_summary_update/',
        '/Estimation/sync_associated_data/',
        '/Estimation/consolidate_price_update/',
        '/Estimation/deducted_item_delete/',
        '/Estimation/temp_deducted_item_delete/',
        '/Estimation/merge_summary_print_2/',
        '/Estimation/product_merge/',
        '/Estimation/summary_view_all/',
        '/Estimation/building_category_summary/',
        '/Estimation/estimation_list_enquiry/',
        '/Estimation/estimation_list_by_boq_enquiry/',
        '/Project/project_scop/',
        '/Project/project_contract_items/',
        '/Estimation/merge_summary_update_spec/',
        '/Estimation/reset_sync_data/',
        '/Estimation/consolidate_addon_update/',
        '/Estimation/consolidate_aluminium_update/',
        '/Estimation/consolidate_loh_update/',
        '/Estimation/consolidate_unitprice_update',
        '/Enquiries/create_quotation_base/',
        '/Enquiries/edit_quotation/',
        '/Enquiries/product_duplicate/',
        '/Enquiries/building_duplicate/',
        '/Estimation/add_typical_buildings/',
        '/Estimation/reset_merge/',
        '/Estimation/product_merge/',
        '/Estimation/sync_associated_data_full/' ,
        '/Estimation/estimation_product_delete/',
        '/Estimation/building_delete/',
        '/Estimation/costing_summary/',
        '/Estimation/specification_wise_scope_summary/',
        '/Estimation/consolidate_scope_summary_print/',
        '/Estimation/building_scope_summary_print/',
        '/Estimation/specification_scope_summary_print/',
        '/Estimation/spec_wise_building/',
        '/Estimation/disable_products/',
        '/Project/salesItem_specifications/',
        
    ]    
    
    if any(path in request.path for path in PATHS):
        MainProduct = EstimationMainProduct
        AluminiumModel = MainProductAluminium
        MainProductAddonCostModel = MainProductAddonCost
        EstimationModel = Estimations
        MainProductGlassModel = MainProductGlass
        PricingOptionModel = PricingOption
        MainProductSiliconModel = MainProductSilicon
    else:
        MainProduct = Temp_EstimationMainProduct
        AluminiumModel = Temp_MainProductAluminium
        MainProductAddonCostModel = Temp_MainProductAddonCost
        EstimationModel = Temp_Estimations
        MainProductGlassModel = Temp_MainProductGlass
        PricingOptionModel = Temp_PricingOption
        MainProductSiliconModel = Temp_MainProductSilicon
        
    try:
        main_product = MainProduct.objects.get(pk=pk)
    except Exception as e:
        main_product = None
    try:
        aluminium_obj = AluminiumModel.objects.get(estimation_product=pk)
    except Exception as e:
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
    material_cost = 0
    silicon_price = 0
    product_base_rate = 0
    aluminium_rate = 0
    glass_rate = 0
    addon = 0
    rp_sqm = 0
    total_price_without_addon = 0
    rounded_total_price = 0
    uom = ''
    tolerance =0 
    labour_overhead = 0
    unit_value_for_deduction_calculation = 0
    rp_sqm_without_addon = 0
    accessory_price = 0
    product_sqm_price_without_addon = 0
    
    aluminium_unit_price = 0
    glass_unit_price = 0
    sealant_unit_price = 0
    accessory_unit_price = 0
    addon_cost = 0
    
    sub_total = 0
    estimated_value_massupdate = 0
    estimated_value_without_addon_massupdate = 0
    
    addon_tolerance = 0
    if aluminium_obj:
        # unit_area = float(aluminium_obj.area)
        if not main_product.after_deduction_price:
            unit_area = float(aluminium_obj.area)
        else:
            unit_area = float(aluminium_obj.area) - float(main_product.deducted_area)
        quantity = aluminium_obj.total_quantity
        total_area = float(unit_area) * float(quantity)
        
        if aluminium_obj.al_quoted_price:
            unit_price += float(aluminium_obj.al_quoted_price)
            aluminium_rate += float(aluminium_obj.al_quoted_price)*float(aluminium_obj.total_quantity)
            aluminium_unit_price += float(aluminium_obj.al_quoted_price)
        
        if aluminium_obj.aluminium_pricing == 1:
            if aluminium_obj.al_price_per_unit:
                product_base_rate += (float(aluminium_obj.al_price_per_unit)*(float(aluminium_obj.al_markup)/100))+float(aluminium_obj.al_price_per_unit)
            elif aluminium_obj.al_price_per_sqm:
                product_base_rate += (float(aluminium_obj.al_price_per_sqm)*(float(aluminium_obj.al_markup)/100))+float(aluminium_obj.al_price_per_sqm)
            elif aluminium_obj.al_weight_per_unit:
                if aluminium_obj.surface_finish:
                    product_base_rate += ((float(aluminium_obj.price_per_kg)*(float(aluminium_obj.al_markup))/100)\
                        +float(aluminium_obj.price_per_kg))+float(aluminium_obj.surface_finish.surface_finish_price)
                else:
                    product_base_rate += (float(aluminium_obj.price_per_kg)*(float(aluminium_obj.al_markup)/100))+float(aluminium_obj.price_per_kg)
            else:
                product_base_rate = 0
        elif aluminium_obj.aluminium_pricing == 2:
            if aluminium_obj.pricing_unit == 1:
                product_base_rate += (float(aluminium_obj.custom_price)*(float(aluminium_obj.al_markup)/100))+\
                    float(aluminium_obj.custom_price)
            elif aluminium_obj.pricing_unit == 2:
                product_base_rate += (float(aluminium_obj.custom_price)*(float(aluminium_obj.al_markup)/100))+\
                    float(aluminium_obj.custom_price)
            elif aluminium_obj.pricing_unit == 3:
                product_base_rate += ((float(aluminium_obj.price_per_kg)*(float(aluminium_obj.al_markup)/100)+\
                    float(aluminium_obj.price_per_kg)))+float(aluminium_obj.surface_finish.surface_finish_price)
            else:
                product_base_rate += 0
        elif aluminium_obj.aluminium_pricing == 4:
            product_base_rate += ((float(aluminium_obj.price_per_kg)*(float(aluminium_obj.al_markup)/100))+float(aluminium_obj.price_per_kg))+float(aluminium_obj.surface_finish.surface_finish_price)
        else: 
            product_base_rate += 0
    
    if glass_obj:
        if glass_obj.glass_quoted_price and glass_obj.is_glass_cost:
            unit_price += float(glass_obj.glass_quoted_price)
            product_base_rate += (float(glass_obj.glass_base_rate)*float(glass_obj.glass_markup_percentage)/100)\
                +float(glass_obj.glass_base_rate)
            
            glass_rate += float(glass_obj.glass_quoted_price)*float(aluminium_obj.total_quantity)
            glass_unit_price += float(glass_obj.glass_quoted_price)
    
    if second_glass_obj:
        for second_glass in second_glass_obj:
            if second_glass.glass_quoted_price and second_glass.is_glass_cost:
                unit_price += float(second_glass.glass_quoted_price)
                glass_rate += float(second_glass.glass_quoted_price)*float(aluminium_obj.total_quantity)

    if silicon_obj:
        if silicon_obj.is_silicon:
            unit_price += float(silicon_obj.silicon_quoted_price)
            silicon_price += float(silicon_obj.silicon_quoted_price)*float(aluminium_obj.total_quantity)
            sealant_unit_price += float(silicon_obj.silicon_quoted_price)
        
    if main_product:
        if main_product.accessory_total and main_product.is_accessory:
            unit_price += float(main_product.accessory_total)
            accessory_price += float(main_product.accessory_total)*float(aluminium_obj.total_quantity)
            accessory_unit_price += float(main_product.accessory_total)
            
        material_cost += float(aluminium_rate)+float(glass_rate)+float(silicon_price)+float(accessory_price)
        if pricing_control:
            if pricing_control.labour_perce:
                labour_percentage = float(pricing_control.labour_perce)/100
                labour_percent_price = round(float(unit_price)*float(labour_percentage), 4)

            if pricing_control.overhead_perce:
                overhead_percentage = float(pricing_control.overhead_perce)/100
                overhead_percent_price = round(float(unit_price)*float(overhead_percentage), 4)
            
        sub_total += (material_cost+(labour_percent_price*float(aluminium_obj.total_quantity))+(overhead_percent_price*float(aluminium_obj.total_quantity)))
        addon_cost += float(main_product.total_addon_cost)
        
        if aluminium_obj.aluminium_pricing == 1 or aluminium_obj.aluminium_pricing == 2 or aluminium_obj.aluminium_pricing == 4:
            if main_product.is_tolerance:
                if main_product.tolerance_type == 1: # percentage
                    tolarance = int(main_product.tolerance)/100
                    tolarance_price = float(aluminium_obj.al_quoted_price)*tolarance
                elif main_product.tolerance_type == 2:
                    tolarance_price = float(main_product.tolerance)
                else:
                    tolarance_price = 0
            else:
                tolarance_price = 0
        else:
            tolarance_price = 0 
        
        estimated_value_massupdate = float(unit_price)+float(overhead_percent_price)+float(labour_percent_price)+float(tolarance_price)+float(main_product.total_addon_cost)
        estimated_value_without_addon_massupdate = float(unit_price)+float(overhead_percent_price)+float(labour_percent_price)
        
        if not main_product.have_merge:
            if not main_product.after_deduction_price:
                estimated_value = round(float(unit_price)+float(overhead_percent_price)+float(labour_percent_price)+float(tolarance_price)+float(main_product.total_addon_cost), 2)
                estimated_value_without_addon = round(float(unit_price)+float(overhead_percent_price)+float(labour_percent_price)+float(tolarance_price), 2)
            else:
                if not edit:
                    estimated_value = math.ceil(float(main_product.after_deduction_price))
                    # +float(main_product.total_addon_cost)
                    estimated_value_without_addon = math.ceil(float(main_product.after_deduction_price))
                    # +float(main_product.total_addon_cost)
                else:
                    if main_product.after_deduction_price:
                        estimated_value = math.ceil(float(main_product.after_deduction_price))
                        # +float(main_product.total_addon_cost)
                        estimated_value_without_addon = math.ceil(float(main_product.after_deduction_price))
                        # +float(main_product.total_addon_cost)
                    else:
                        estimated_value = float((unit_price))+float(overhead_percent_price)+float(labour_percent_price)+float(tolarance_price)+float(main_product.total_addon_cost)
                        estimated_value_without_addon = float((unit_price))+float(overhead_percent_price)+float(labour_percent_price)+float(tolarance_price)
        else:
            estimated_value = main_product.merge_price
            estimated_value_without_addon = main_product.merge_price
    
        unit_value_for_deduction_calculation = float((unit_price))+float(overhead_percent_price)+float(labour_percent_price)+float(tolarance_price)+float(main_product.total_addon_cost)
        
        try:
            labour_overhead = (float(labour_percent_price)+float(overhead_percent_price))*float(aluminium_obj.total_quantity)
        except:
            labour_overhead = (float(labour_percent_price)+float(overhead_percent_price))
        
        
        addon = float(main_product.total_addon_cost)*float(aluminium_obj.total_quantity)
        tolerance = float(tolarance_price)*float(aluminium_obj.total_quantity)
        
        if not main_product.have_merge:
            
            if main_product.after_deduction_price:
                total_price = ((float(math.ceil(main_product.after_deduction_price)))*int(quantity))
                total_price_without_addon = (float(math.ceil(main_product.after_deduction_price)))*int(quantity)
            else:
                total_price = (float(math.ceil(round(estimated_value, 2))))*int(quantity)
                total_price_without_addon = (float(math.ceil(round(estimated_value_without_addon, 2))))*int(quantity)
        else:
            total_price = float(main_product.merge_price)
            total_price_without_addon = float(main_product.merge_price)

        try:
            rp_sqm = total_price/total_area
            rp_sqm_without_addon = total_price_without_addon/total_area
            
            if not main_product.have_merge:
                if not main_product.after_deduction_price:
                    product_sqm_price_without_addon = ((float((unit_price))+float(overhead_percent_price)+float(labour_percent_price)+float(tolarance_price))*float(quantity))/float(total_area)
                else:
                    product_sqm_price_without_addon = (((float(main_product.after_deduction_price)) - (float(main_product.total_addon_cost)))*float(quantity))/float(total_area)
                    # product_sqm_price_without_addon = (((float(main_product.after_deduction_price)+float(main_product.total_addon_cost)) - (float(tolarance_price)+float(main_product.total_addon_cost)))*float(quantity))/float(total_area)
            else:
                product_sqm_price_without_addon = (float(main_product.merge_price)-(float(main_product.total_addon_cost))*float(quantity))/float(total_area)
                
        except Exception as e:
            rp_sqm = 0
            rp_sqm_without_addon = 0
            product_sqm_price_without_addon = 0
        
        uom = main_product.uom.uom
    
    # rounded_total_price = float((round(total_price, 2)))
    rounded_total_price = float(math.ceil(round(total_price, 2)))
        
    data = {
        'unit_price': estimated_value,
        # 'unit_price_massupdate': estimated_value_massupdate,
        'unit_price_massupdate': math.ceil(round(estimated_value_massupdate, 2)),
        'total_price': total_price,
        'rp_sqm': rp_sqm,
        'rp_sqm_without_addon': rp_sqm_without_addon,
        # 'sub_total': total_price_without_addon,
        'product_base_rate': product_base_rate,
        'aluminium_rate': aluminium_rate,
        'glass_rate': glass_rate,
        'material_cost': material_cost,
        'labour_overhead': labour_overhead,
        'tolarance_price': tolarance_price,
        'unit_value_for_deduction_calculation': unit_value_for_deduction_calculation,
        'round_total_price': rounded_total_price,
        'aluminium_unit_price': aluminium_unit_price,
        'glass_unit_price': glass_unit_price,
        'sealant_unit_price': sealant_unit_price,
        'silicon_price': silicon_price,
        'accessory_unit_price': accessory_unit_price,
        'accessory_price': accessory_price,
        'product_sqm_price_without_addon': product_sqm_price_without_addon,
        'uom': uom,
        'addon': addon,
        'total_price_without_addon':total_price_without_addon,
        'tolerance': tolerance,
        'sub_total': sub_total,
        'addon_cost': addon_cost,
        'estimated_value_without_addon_massupdate': estimated_value_without_addon_massupdate,
    }
    return data


def merge_update_price(
                        request, pk, aluminium_markup=None, 
                        alu_base_input=None, infill_markup=None, 
                        infil_base_input=None, labour=None, 
                        overhead=None, sqm_price=None, 
                        glass_spec=None,
                        external=None, external_markup=None, 
                        internal=None, internal_markup=None,
                    ):
    """
    This function updates the pricing information for a product and its components based on user input.
    
    :param request: The HTTP request object
    :param pk: The primary key of the MainProduct object that needs to be updated
    :param aluminium_markup: Markup percentage for aluminium pricing
    :param alu_base_input: The base input price for the aluminium material used in the product
    :param infill_markup: The markup percentage to be applied on the infill base rate for calculating
    the infill quote rate
    :param infil_base_input: The base input value for the infill material used in the product
    :param labour: The percentage markup for labour cost
    :param overhead: The overhead percentage to be applied in the pricing calculation
    :param sqm_price: The price per square meter of the product without any addons or markups
    :param glass_spec: The specification of the glass used in the product
    :param external: The base rate for external silicon sealant
    :param external_markup: The markup percentage to be applied on the external silicon cost
    :param internal: The base rate for internal silicon sealant
    :param internal_markup: The markup percentage for the internal silicon sealant cost
    """
    PATHS = [
        '/Estimation/merge_summary_update/',
        '/Enquiries/product_category_summary/',
        '/Estimation/consolidate_price_update/',
        '/Estimation/merge_summary_update_spec/',
        '/Estimation/consolidate_addon_update/',
        '/Estimation/consolidate_aluminium_update/',
        '/Estimation/consolidate_sealant_update/',
        '/Estimation/consolidate_sealant_products/',
        '/Estimation/consolidate_loh_update/',
        '/Estimation/consolidate_unitprice_update',
        
    ]
    if any(path in request.path for path in PATHS):
        MainProduct = EstimationMainProduct
        AluminiumModel = MainProductAluminium
        MainProductAddonCostModel = MainProductAddonCost
        EstimationModel = Estimations
        MainProductGlassModel = MainProductGlass
        PricingOptionModel = PricingOption
        MainProductSiliconModel = MainProductSilicon
    else:
        MainProduct = Temp_EstimationMainProduct
        AluminiumModel = Temp_MainProductAluminium
        MainProductAddonCostModel = Temp_MainProductAddonCost
        EstimationModel = Temp_Estimations
        MainProductGlassModel = Temp_MainProductGlass
        PricingOptionModel = Temp_PricingOption
        MainProductSiliconModel = Temp_MainProductSilicon
                   
    try:
        main_product = MainProduct.objects.get(pk=pk)
    except MainProduct.DoesNotExist:
        main_product = None
    try:
        aluminium_obj = AluminiumModel.objects.get(estimation_product=main_product.id)
    except AluminiumModel.DoesNotExist:
        aluminium_obj = None
    
    try:
        if glass_spec:
            glass_obj = MainProductGlassModel.objects.get(estimation_product=main_product.id, glass_primary=True, glass_specif=int(glass_spec))
        else:
            glass_obj = MainProductGlassModel.objects.get(estimation_product=main_product.id, glass_primary=True)
            second_glass_obj = MainProductGlassModel.objects.filter(estimation_product=main_product.id, glass_primary=False)
            
    except MainProductGlassModel.DoesNotExist:
        glass_obj = None
        second_glass_obj = None
        
    if glass_spec:
        second_glass_obj = MainProductGlassModel.objects.filter(estimation_product=main_product.id, glass_primary=False, glass_specif=int(glass_spec))
        # second_glass_obj = MainProductGlassModel.objects.select_related('estimation_product').filter(estimation_product=main_product.id, glass_primary=False)
        
    try:
        silicon_obj = MainProductSiliconModel.objects.get(estimation_product=main_product.id)
    except Exception:
        silicon_obj = None
        
    try:
        pricing_control = PricingOptionModel.objects.get(estimation_product=main_product.id)
    except PricingOptionModel.DoesNotExist:
        pricing_control = None
    
    old_price = main_product.product_unit_price
    old_sqm = main_product.product_sqm_price_without_addon
    
    product_base_rate = 0
    
    if aluminium_obj:
        alumin_quote_rate = 0
        if aluminium_obj.aluminium_pricing == 1:
            if aluminium_obj.pricing_unit == 1:
                if aluminium_markup:
                    if alu_base_input:
                        product_base_rate += (float(alu_base_input)*(float(aluminium_markup)/100))+float(alu_base_input)
                        alumin_quote_rate = product_base_rate
                        aluminium_obj.al_price_per_unit = alu_base_input
                    else:
                        product_base_rate += (float(aluminium_obj.al_price_per_unit)*(float(aluminium_markup)/100))+float(aluminium_obj.al_price_per_unit)
                        alumin_quote_rate = product_base_rate
                else:
                    if alu_base_input:
                        product_base_rate += (float(alu_base_input)*(float(aluminium_obj.al_markup)/100))+float(alu_base_input)
                        alumin_quote_rate = product_base_rate
                        aluminium_obj.al_price_per_unit = alu_base_input
                    else:
                        product_base_rate += (float(aluminium_obj.al_price_per_unit)*(float(aluminium_obj.al_markup)/100))+float(aluminium_obj.al_price_per_unit)
                        alumin_quote_rate = product_base_rate
            elif aluminium_obj.pricing_unit == 2:
                if aluminium_markup:
                    if alu_base_input:
                        product_base_rate += (float(alu_base_input)*(float(aluminium_markup)/100))+float(alu_base_input)
                        alumin_quote_rate = product_base_rate*float(aluminium_obj.area)
                        aluminium_obj.al_price_per_sqm = alu_base_input
                    else:
                        product_base_rate += (float(aluminium_obj.al_price_per_sqm)*(float(aluminium_markup)/100))+float(aluminium_obj.al_price_per_sqm)
                        alumin_quote_rate = product_base_rate*float(aluminium_obj.area) 
                else:
                    if alu_base_input:
                        product_base_rate += (float(alu_base_input)*(float(aluminium_obj.al_markup)/100))+float(alu_base_input)
                        alumin_quote_rate = product_base_rate*float(aluminium_obj.area)
                        aluminium_obj.al_price_per_sqm = alu_base_input
                    else:
                        product_base_rate += (float(aluminium_obj.al_price_per_sqm)*(float(aluminium_obj.al_markup)/100))+float(aluminium_obj.al_price_per_sqm)
                        alumin_quote_rate = product_base_rate*float(aluminium_obj.area)
                        
            elif aluminium_obj.pricing_unit == 3:
                if aluminium_obj.surface_finish:
                    if aluminium_markup:
                        if alu_base_input:
                            product_base_rate += ((float(alu_base_input)*(float(aluminium_markup))/100)\
                                +float(alu_base_input))+float(aluminium_obj.surface_finish.surface_finish_price)
                            alumin_quote_rate = product_base_rate*float(aluminium_obj.weight_per_unit)
                            aluminium_obj.price_per_kg = alu_base_input
                        else:
                            product_base_rate += ((float(aluminium_obj.price_per_kg)*(float(aluminium_markup))/100)\
                                +float(aluminium_obj.price_per_kg))+float(aluminium_obj.surface_finish.surface_finish_price)
                            alumin_quote_rate = product_base_rate*float(aluminium_obj.weight_per_unit)
                    else:
                        if alu_base_input:
                            product_base_rate += ((float(alu_base_input)*(float(aluminium_obj.al_markup))/100)\
                                +float(alu_base_input))+float(aluminium_obj.surface_finish.surface_finish_price)
                            alumin_quote_rate = product_base_rate*float(aluminium_obj.weight_per_unit)
                            aluminium_obj.price_per_kg = alu_base_input
                        else:
                            product_base_rate += ((float(aluminium_obj.price_per_kg)*(float(aluminium_obj.al_markup))/100)\
                                +float(aluminium_obj.price_per_kg))+float(aluminium_obj.surface_finish.surface_finish_price)
                            alumin_quote_rate = product_base_rate*float(aluminium_obj.weight_per_unit)
                else:
                    if aluminium_markup:
                        if alu_base_input:
                            product_base_rate += (float(alu_base_input)*(float(aluminium_markup)/100))+float(alu_base_input)
                            alumin_quote_rate = product_base_rate*float(aluminium_obj.weight_per_unit)
                            aluminium_obj.price_per_kg = alu_base_input
                        else:
                            product_base_rate += (float(aluminium_obj.price_per_kg)*(float(aluminium_markup)/100))+float(aluminium_obj.price_per_kg)
                            alumin_quote_rate = product_base_rate*float(aluminium_obj.weight_per_unit)
                    else:
                        if alu_base_input:
                            product_base_rate += (float(alu_base_input)*(float(aluminium_obj.al_markup)/100))+float(alu_base_input)
                            alumin_quote_rate = product_base_rate*float(aluminium_obj.weight_per_unit)
                            aluminium_obj.price_per_kg = alu_base_input
                        else:
                            product_base_rate += (float(aluminium_obj.price_per_kg)*(float(aluminium_obj.al_markup)/100))+float(aluminium_obj.price_per_kg)
                            alumin_quote_rate = product_base_rate*float(aluminium_obj.weight_per_unit)
                        
            else:
                product_base_rate = 0
        elif aluminium_obj.aluminium_pricing == 2:
            if aluminium_obj.pricing_unit == 1:
                if aluminium_markup:
                    if alu_base_input:
                        product_base_rate += (float(alu_base_input)*(float(aluminium_markup)/100))+\
                            float(alu_base_input)
                        alumin_quote_rate = product_base_rate*float(aluminium_obj.area)
                        aluminium_obj.custom_price = alu_base_input
                    else:
                        product_base_rate += (float(aluminium_obj.custom_price)*(float(aluminium_markup)/100))+\
                            float(aluminium_obj.custom_price)
                        alumin_quote_rate = product_base_rate*float(aluminium_obj.area)
                else:
                    if alu_base_input:
                        product_base_rate += (float(alu_base_input)*(float(aluminium_obj.al_markup)/100))+\
                            float(alu_base_input)
                        alumin_quote_rate = product_base_rate*float(aluminium_obj.area)
                        aluminium_obj.custom_price = alu_base_input
                    else:
                        product_base_rate += (float(aluminium_obj.custom_price)*(float(aluminium_obj.al_markup)/100))+\
                            float(aluminium_obj.custom_price)
                        alumin_quote_rate = product_base_rate*float(aluminium_obj.area)
                        
            elif aluminium_obj.pricing_unit == 2:
                if aluminium_markup:
                    if alu_base_input:
                        product_base_rate += (float(alu_base_input)*(float(aluminium_markup)/100))+\
                            float(alu_base_input)
                        alumin_quote_rate = product_base_rate
                        aluminium_obj.custom_price = alu_base_input
                    else:
                        product_base_rate += (float(aluminium_obj.custom_price)*(float(aluminium_markup)/100))+\
                            float(aluminium_obj.custom_price)
                        alumin_quote_rate = product_base_rate
                else:
                    if alu_base_input:
                        product_base_rate += (float(alu_base_input)*(float(aluminium_obj.al_markup)/100))+\
                            float(alu_base_input)
                        alumin_quote_rate = product_base_rate
                        aluminium_obj.custom_price = alu_base_input
                    else:
                        product_base_rate += (float(aluminium_obj.custom_price)*(float(aluminium_obj.al_markup)/100))+\
                            float(aluminium_obj.custom_price)
                        alumin_quote_rate = product_base_rate
                        
            elif aluminium_obj.pricing_unit == 3:
                if aluminium_markup:
                    if alu_base_input:
                        product_base_rate += ((float(alu_base_input)*(float(aluminium_markup)/100)+\
                            float(alu_base_input)))+float(aluminium_obj.surface_finish.surface_finish_price)
                        alumin_quote_rate = product_base_rate*float(aluminium_obj.weight_per_unit)
                        aluminium_obj.price_per_kg = alu_base_input
                    else:
                        product_base_rate += ((float(aluminium_obj.price_per_kg)*(float(aluminium_markup)/100)+\
                            float(aluminium_obj.price_per_kg)))+float(aluminium_obj.surface_finish.surface_finish_price)
                        alumin_quote_rate = product_base_rate*float(aluminium_obj.weight_per_unit)   
                else:
                    if alu_base_input:
                        product_base_rate += ((float(alu_base_input)*(float(aluminium_obj.al_markup)/100)+\
                            float(alu_base_input)))+float(aluminium_obj.surface_finish.surface_finish_price)
                        alumin_quote_rate = product_base_rate*float(aluminium_obj.weight_per_unit)
                        aluminium_obj.price_per_kg = alu_base_input
                    else:
                        product_base_rate += ((float(aluminium_obj.price_per_kg)*(float(aluminium_obj.al_markup)/100)+\
                            float(aluminium_obj.price_per_kg)))+float(aluminium_obj.surface_finish.surface_finish_price)
                        alumin_quote_rate = product_base_rate*float(aluminium_obj.weight_per_unit)
            else:
                product_base_rate += 0
        elif aluminium_obj.aluminium_pricing == 4:
            if aluminium_markup:
                if alu_base_input:
                    product_base_rate += ((float(alu_base_input)*(float(aluminium_markup)/100))+float(alu_base_input))+float(aluminium_obj.surface_finish.surface_finish_price)
                    alumin_quote_rate = product_base_rate*float(aluminium_obj.weight_per_unit)
                    aluminium_obj.price_per_kg = alu_base_input
                else:
                    product_base_rate += ((float(aluminium_obj.price_per_kg)*(float(aluminium_markup)/100))+float(aluminium_obj.price_per_kg))+float(aluminium_obj.surface_finish.surface_finish_price)
                    alumin_quote_rate = product_base_rate*float(aluminium_obj.weight_per_unit) 
            else:
                if alu_base_input:
                    product_base_rate += ((float(alu_base_input)*(float(aluminium_obj.al_markup)/100))+float(alu_base_input))+float(aluminium_obj.surface_finish.surface_finish_price)
                    alumin_quote_rate = product_base_rate*float(aluminium_obj.weight_per_unit)
                    aluminium_obj.price_per_kg = alu_base_input
                else:
                    product_base_rate += ((float(aluminium_obj.price_per_kg)*(float(aluminium_obj.al_markup)/100))+float(aluminium_obj.price_per_kg))+float(aluminium_obj.surface_finish.surface_finish_price)
                    alumin_quote_rate = product_base_rate*float(aluminium_obj.weight_per_unit)
                    
        else: 
            product_base_rate += 0
        
        if aluminium_markup:
            aluminium_obj.al_markup = float(aluminium_markup)
        aluminium_obj.al_quoted_price = math.ceil(alumin_quote_rate)
        aluminium_obj.save()
        
    if glass_obj:
        if glass_obj.glass_pricing_type == 1:
            if infill_markup:
                if infil_base_input:
                    infill_quote_rate = ((float(infil_base_input)*float(infill_markup)/100)+\
                        float(infil_base_input))*float(glass_obj.total_area_glass)
                    glass_obj.glass_base_rate = infil_base_input
                else:
                    infill_quote_rate = ((float(glass_obj.glass_base_rate)*float(infill_markup)/100)+\
                        float(glass_obj.glass_base_rate))*float(glass_obj.total_area_glass)
            else:
                if infil_base_input:
                    infill_quote_rate = ((float(infil_base_input)*float(glass_obj.glass_markup_percentage)/100)+\
                        float(infil_base_input))*float(glass_obj.total_area_glass)
                    glass_obj.glass_base_rate = infil_base_input
                else:
                    infill_quote_rate = ((float(glass_obj.glass_base_rate)*float(glass_obj.glass_markup_percentage)/100)+\
                        float(glass_obj.glass_base_rate))*float(glass_obj.total_area_glass)
        elif glass_obj.glass_pricing_type == 2:
            if infill_markup:
                if infil_base_input:
                    infill_quote_rate = ((float(infil_base_input)*float(infill_markup)/100)+\
                        float(infil_base_input))*float(glass_obj.total_area_glass)
                    glass_obj.glass_base_rate = infil_base_input
                else:
                    infill_quote_rate = ((float(glass_obj.glass_base_rate)*float(infill_markup)/100)+\
                        float(glass_obj.glass_base_rate))*float(glass_obj.total_area_glass)
            else:
                if infil_base_input:
                    infill_quote_rate = ((float(infil_base_input)*float(glass_obj.glass_markup_percentage)/100)+\
                        float(infil_base_input))*float(glass_obj.total_area_glass)
                    glass_obj.glass_base_rate = infil_base_input
                else:
                    infill_quote_rate = ((float(glass_obj.glass_base_rate)*float(glass_obj.glass_markup_percentage)/100)+\
                        float(glass_obj.glass_base_rate))*float(glass_obj.total_area_glass)
                    
        if infill_markup:
            glass_obj.glass_markup_percentage = float(infill_markup)
            glass_obj.glass_quoted_price = math.ceil(infill_quote_rate)
        # else:
        #     glass_obj.glass_quoted_price = math.ceil(infill_quote_rate)
            
        glass_obj.save()
        
    if second_glass_obj:
        for second_glass in second_glass_obj:
            if second_glass.glass_pricing_type == 1:
                if infill_markup:
                    if infil_base_input:
                        infill_quote_rate = ((float(infil_base_input)*float(infill_markup)/100)+\
                            float(infil_base_input))*float(second_glass.total_area_glass)
                        second_glass.glass_base_rate = infil_base_input
                    else:
                        infill_quote_rate = ((float(second_glass.glass_base_rate)*float(infill_markup)/100)+\
                            float(second_glass.glass_base_rate))*float(second_glass.total_area_glass)
                else:
                    if infil_base_input:
                        infill_quote_rate = ((float(infil_base_input)*float(second_glass.glass_markup_percentage)/100)+\
                            float(infil_base_input))*float(second_glass.total_area_glass)
                        second_glass.glass_base_rate = infil_base_input
                    else:
                        infill_quote_rate = ((float(second_glass.glass_base_rate)*float(second_glass.glass_markup_percentage)/100)+\
                            float(second_glass.glass_base_rate))*float(second_glass.total_area_glass)
                        
            elif second_glass.glass_pricing_type == 2:
                if infill_markup:
                    if infil_base_input:
                        infill_quote_rate = ((float(infil_base_input)*float(infill_markup)/100)+\
                            float(infil_base_input))*float(second_glass.total_area_glass)
                        second_glass.glass_base_rate = infil_base_input
                    else:
                        infill_quote_rate = ((float(second_glass.glass_base_rate)*float(infill_markup)/100)+\
                            float(second_glass.glass_base_rate))*float(second_glass.total_area_glass)
                else:
                    if infil_base_input:
                        infill_quote_rate = ((float(infil_base_input)*float(second_glass.glass_markup_percentage)/100)+\
                            float(infil_base_input))*float(second_glass.total_area_glass)
                        second_glass.glass_base_rate = infil_base_input
                    else:
                        infill_quote_rate = ((float(second_glass.glass_base_rate)*float(second_glass.glass_markup_percentage)/100)+\
                            float(second_glass.glass_base_rate))*float(second_glass.total_area_glass)
                        
            if infill_markup:
                second_glass.glass_markup_percentage = float(infill_markup)
                second_glass.glass_quoted_price = math.ceil(infill_quote_rate)
                
            else:
                second_glass.glass_quoted_price = math.ceil(infill_quote_rate)
            second_glass.save()

    if labour or overhead:
        if labour:
            pricing_control.labour_perce = float(labour)
        if overhead:
            pricing_control.overhead_perce = float(overhead)
            
        if sqm_price:
            pricing_control.adjust_by_sqm = True
        
        pricing_control.save()
        
    if silicon_obj:
        if external:
            silicon_obj.external_base_rate = external
        if external_markup:
            silicon_obj.external_markup = external_markup
        if internal:
            silicon_obj.internal_base_rate = internal
        if internal_markup:
            silicon_obj.internal_markup = internal_markup
            
        silicon_obj.save()
        if sealant_quote_cal(request, silicon_obj):
            silicon_obj.save()
            
    price_data = product_unit_price(request=request, pk=main_product.id)
    
    if aluminium_obj.aluminium_pricing == 1 or aluminium_obj.aluminium_pricing == 2 or aluminium_obj.aluminium_pricing == 4:
        if main_product.is_tolerance:
            if main_product.tolerance_type == 1: # percentage
                tolarance = int(main_product.tolerance)/100
                tolarance_price = float(aluminium_obj.al_quoted_price)*tolarance
            elif main_product.tolerance_type == 2:
                tolarance_price = float(main_product.tolerance)
            else:
                tolarance_price = 0
        else:
            tolarance_price = 0
    else:
        tolarance_price = 0 
    
    if main_product:
        # unit_price = main_product.product_unit_price
        main_product.product_base_rate = price_data['product_base_rate']
        main_product.product_sqm_price = price_data['rp_sqm']
        
        if sqm_price:
            main_product.product_sqm_price_without_addon = sqm_price
        else:
           main_product.product_sqm_price_without_addon = price_data['product_sqm_price_without_addon']
        
        main_product.product_unit_price = price_data['unit_price']
        
            
        if main_product.product_type == 1:
            if main_product.have_merge:
                associated_products = MainProduct.objects.filter(product_type=2, main_product=main_product.id)
                
                associated_unit = 0
                for associated in associated_products:
                    associated_aluminium = AluminiumModel.objects.get(estimation_product=associated.id)
                    associated_unit += float(associated.product_unit_price)*float(associated_aluminium.quantity)
                total = math.ceil(float(price_data['unit_price_massupdate'])+float(associated_unit))
                main_product.product_unit_price = price_data['unit_price_massupdate']
                main_product.merge_price = total 
                main_product.save()
                
                
                # diff = float(main_product.merge_price) - float(unit_price)
                # main_product.merge_price = float(main_product.product_unit_price)
                # main_product.product_unit_price = float(main_product.product_unit_price) - float(diff)
                
        # else:
        #     if main_product.main_product.have_merge:
        #         main_product2 = MainProduct.objects.get(pk=main_product.main_product.id)
        #         price_data2 = product_unit_price(request=request, pk=main_product2.id)
        #         associated_products = MainProduct.objects.filter(product_type=2, main_product=main_product2.id) #.exclude(pk=main_product.id)
                
        #         associated_unit = 0
        #         for associated in associated_products:
        #             associated_aluminium = AluminiumModel.objects.get(estimation_product=associated.id)
        #             associated_unit += float(associated.product_unit_price)*float(associated_aluminium.quantity)
        #         total = float(price_data2['unit_price_massupdate']) + float(price_data['unit_price_massupdate'])
        #         main_product2.product_unit_price = price_data2['unit_price_massupdate']
        #         # main_product2.merge_price = total
        #         main_product2.save()
            
                
        if main_product.after_deduction_price or main_product.deduction_price:
            sqm_price = round(float(price_data['estimated_value_without_addon_massupdate'])/float(aluminium_obj.area), 2)
            main_product.product_sqm_price = sqm_price
            new_area = float(aluminium_obj.area) - float(main_product.deducted_area)
            new_deducted_price = (new_area*float(sqm_price))
            main_product.after_deduction_price = float(new_deducted_price)+float(main_product.total_addon_cost)+float(tolarance_price)
            main_product.deduction_price = float(new_deducted_price)
            main_product.product_unit_price = (float(aluminium_obj.area)*(float(sqm_price)))+float(main_product.total_addon_cost)
               
                
                
    main_product.save()
    
    if '/Estimation/merge_summary_update/' in request.path or '/Estimation/temp_merge_summary_update/' in request.path:
        module_label = "Product Summary"
    elif '/Estimation/consolidate_price_update/' in request.path or '/Estimation/temp_consolidate_price_update/' in request.path:
        module_label = "Product Summary Infill Price Update"
    elif '/Estimation/merge_summary_update_spec/' in request.path or '/Estimation/temp_merge_summary_update_spec/' in request.path:
        module_label = "Product Summary Specification Wise Price Update"
    elif '/Estimation/consolidate_addon_update/' in request.path or '/Estimation/temp_consolidate_addon_update/' in request.path:
        module_label = "Product Summary Addon's Price Update"
    elif '/Estimation/consolidate_aluminium_update/' in request.path or '/Estimation/temp_consolidate_aluminium_update/' in request.path:
        module_label = "Product Summary Aluminium Price Update"
    elif '/Estimation/consolidate_sealant_update/' in request.path or '/Estimation/temp_consolidate_sealant_update/' in request.path:
        module_label = "Product Summary Sealant Price Update"
    elif '/Estimation/consolidate_sealant_products/' in request.path or '/Estimation/temp_consolidate_sealant_products/' in request.path:
        module_label = "Product Summary Sealant Price Update"
    elif '/Estimation/consolidate_loh_update/' in request.path or '/Estimation/temp_consolidate_loh_update/' in request.path:
        module_label = "Product Summary Labour and Overhead Price Update"
    elif '/Estimation/consolidate_unitprice_update' in request.path or '/Estimation/temp_consolidate_unitprice_update' in request.path:
        module_label = "Product Summary Unit Price Update"
    else:
        module_label = "Product Summary"
        
        
    audit_data = {
        "estimation" : main_product.building.estimation.id,
        "product" : main_product.id,
        "user" : request.user,
        "old_area" : None,
        "new_area" : None,
        "old_quantity" : None,
        "new_quantity" : None,
        "old_price" : old_price,
        "new_price" : main_product.product_unit_price,
        "action": "UPDATE",
        "old_sqm": old_sqm,
        "new_sqm": main_product.product_sqm_price_without_addon,
        "Module": module_label,
    }
    audit_log(request=request, data=audit_data)
            
    
def new_deduction_price(price, pk):
    """
    The function calculates a new deducted price and new square meter price based on given parameters.
    
    """
    product = EstimationMainProduct.objects.get(pk=pk)
    alumin = MainProductAluminium.objects.get(estimation_product=product)
    glass = MainProductGlass.objects.get(estimation_product=product)
        
    new_deducted_price = float(glass.glass_quoted_price) - (float(product.deducted_area)*float(glass.glass_price_per_sqm))
    deduct_area = float(alumin.area)-float(product.deducted_area)
    data = {
        "new_deducted_price": new_deducted_price,
        "new_sqm_price": float(new_deducted_price)/float(deduct_area),
    }
    return data


def category_summary_data(request, pk):
    """
    This function calculates and returns various data related to a category summary for a given product.
    """
    PATHS = [
        '/Estimation/merge_summary_print/',
        '/Estimation/merge_summary_print_2/'
    ]
    
    if any(path in request.path for path in PATHS):
        MainProduct = EstimationMainProduct
        AluminiumModel = MainProductAluminium
        MainProductAddonCostModel = MainProductAddonCost
        EstimationModel = Estimations
        MainProductGlassModel = MainProductGlass
        PricingOptionModel = PricingOption
        MainProductSiliconModel = MainProductSilicon
    else:
        MainProduct = Temp_EstimationMainProduct
        AluminiumModel = Temp_MainProductAluminium
        MainProductAddonCostModel = Temp_MainProductAddonCost
        EstimationModel = Temp_Estimations
        MainProductGlassModel = Temp_MainProductGlass
        PricingOptionModel = Temp_PricingOption
        MainProductSiliconModel = Temp_MainProductSilicon
        
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
    unit_area = round((int(aluminium_obj.width) * int(aluminium_obj.height))/1000000, 2)
    
    quantity = aluminium_obj.total_quantity
    total_area += float(unit_area) * float(quantity)
    
    if aluminium_obj.product_configuration or aluminium_obj.custom_price or aluminium_obj.price_per_kg:    
        if aluminium_obj.al_quoted_price:
            alumin_total = float(aluminium_obj.al_quoted_price)
    if glass_obj:
        if glass_obj.glass_base_rate:
            glass_total += float(glass_obj.glass_quoted_price)
    if second_glass_obj:
        for second_glass in second_glass_obj:
            if second_glass.glass_base_rate:
                sec_glass_total += float(second_glass.glass_quoted_price)
                
    glass_total = glass_total + sec_glass_total
        
    if silicon_obj:
        if silicon_obj.is_silicon:
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
    if aluminium_obj.aluminium_pricing == 1 or aluminium_obj.aluminium_pricing == 2 or aluminium_obj.aluminium_pricing == 4:
        if main_product.is_tolerance:
            if main_product.tolerance_type == 1:
                tolarance = int(main_product.tolerance)/100
                tolarance_price = float(aluminium_obj.al_quoted_price)*tolarance
            elif main_product.tolerance_type == 2:
                tolarance_price = main_product.tolerance
            else:
                tolarance_price = 0
        else:
            tolarance_price = 0
    else:
        tolarance_price = 0
        
    
    if not main_product.after_deduction_price:
        rate_per_unit = float(material_total)+float(tolarance_price)+float(labour_percent_price)+\
                                        float(overhead_percent_price)+float(total_addon_cost)
    else:
        rate_per_unit = float(main_product.after_deduction_price)
        
    line_total = (float(rate_per_unit)*float(aluminium_obj.total_quantity))
    
    try:
        rate_per_sqm = line_total/total_area
    except Exception as e:
        rate_per_sqm = 0
        
        
    data = {
        'line_total': line_total,
        'rate_per_unit': rate_per_unit,
        'tolarance_price': float(tolarance_price),
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
        'pricing_control': pricing_control,
        'rate_per_sqm': rate_per_sqm,
        'second_glass_obj': second_glass_obj
    }
    return data


def merge_summary_count(request, pk, version, sqm=None, base_rate=None, product=None):
    """
    This function calculates various summary counts and rates for a given set of products in an
    estimation.
    
    """
    PATHS = [
        '/Estimation/merge_summary_print/',
        '/Estimation/product_merge_summary/',
        
    ]
    if any(path in request.path for path in PATHS):
        MainProduct = EstimationMainProduct
        AluminiumModel = MainProductAluminium
        MainProductAddonCostModel = MainProductAddonCost
        EstimationModel = Estimations
        MainProductGlassModel = MainProductGlass
        PricingOptionModel = PricingOption
        MainProductSiliconModel = MainProductSilicon
    else:
        MainProduct = Temp_EstimationMainProduct
        AluminiumModel = Temp_MainProductAluminium
        MainProductAddonCostModel = Temp_MainProductAddonCost
        EstimationModel = Temp_Estimations
        MainProductGlassModel = Temp_MainProductGlass
        PricingOptionModel = Temp_PricingOption
        MainProductSiliconModel = Temp_MainProductSilicon
        
    if base_rate:
        products = MainProduct.objects.filter(building__estimation=version, 
                                              specification_Identifier=pk,
                                              product_base_rate=base_rate
                                            )
    else:
        products = MainProduct.objects.filter(building__estimation=version, 
                                              specification_Identifier=pk, 
                                              product_sqm_price=sqm,
                                            )
    
    quantity = 0
    area = 0
    total_area = 0
    aluminium_rate = 0
    glass_rate = 0
    material_cost = 0
    labour_overhead = 0
    tolarance_price = 0
    total_price = 0
    ids = []
    typical_qty = 1
    for pro in products:
        product = MainProduct.objects.get(pk=pro.id)
        aluminium = AluminiumModel.objects.get(estimation_product=product.id)
            
        quantity += aluminium.total_quantity
        if product.building.typical_buildings_enabled:
            typical_qty = product.building.no_typical_buildings
            
        product_prices = product_unit_price(request=request, pk=product.id)
        if product_prices['rp_sqm']:
            aluminium_rate += product_prices['aluminium_rate']
            glass_rate += product_prices['glass_rate']
            material_cost += product_prices['material_cost']
            labour_overhead += product_prices['labour_overhead']
            tolarance_price += product_prices['tolarance_price']
            total_price += product_prices['total_price']
        else:
            aluminium_rate += 0
            glass_rate += 0
            material_cost += 0
            labour_overhead += 0
            tolarance_price += 0
            total_price += 0
            
        if product.category.is_curtain_wall:
            area = float(aluminium.area)
            total_area += float(aluminium.area)*float(aluminium.total_quantity)*float(typical_qty)
        else:
            area = float(aluminium.area)
            total_area += float(aluminium.area)*float(aluminium.total_quantity)*float(typical_qty)
        ids.append(product.id)
    
    data = {
        'quantity': quantity,
        'area': area,
        'total_area': total_area,
        'ids': ids,
        'aluminium_rate': aluminium_rate,
        'glass_rate': glass_rate,
        'material_cost': material_cost,
        'labour_overhead': labour_overhead,
        'tolarance_price': tolarance_price,
        'total_price': total_price
    }
    return data    


def workstation_data(pk, current_workstation):
    """
    The function returns data about workstations for a given product and current workstation.
    
    """
    workstations = [ workstation.workstation.id for workstation in Product_WorkStations.objects.filter(product=pk)]
    try:    
        next_workstation = workstations[workstations.index(current_workstation)+1]
    except:
        next_workstation = None
    data = {
        "current_workstation": current_workstation,
        "next_workstation": next_workstation,
        "workstations": workstations,
        "final_workstation": workstations[-1]
    }
    return data
    

def sealant_quote_cal(request, silicon_obj):
    """
    This function calculates a quote price for a sealant based on various input parameters.
    
    :param request: The request object is an HTTP request object that contains information about the
    current request being made by the user
    :param silicon_obj: It is an object that contains information about the type of sealant and the
    rates for different types of sealant and gaskets. The function calculates a quote price based on
    these rates and saves it in the silicon_obj object
    :return: a boolean value - True or False.
    """
    if silicon_obj:
        quote_price = 0

        def calculate_quote_rate(base_rate, markup, lm):
            return (base_rate * (markup / 100)) + base_rate

        if silicon_obj.external_base_rate and silicon_obj.external_sealant_type != 0:
            base_rate = float(silicon_obj.external_base_rate)
            markup = float(silicon_obj.external_markup)
            lm = float(silicon_obj.external_lm)
            quote_rate = calculate_quote_rate(base_rate, markup, lm)
            quote_price += quote_rate * lm

        if silicon_obj.internal_base_rate and silicon_obj.internal_sealant_type != 0:
            base_rate = float(silicon_obj.internal_base_rate)
            markup = float(silicon_obj.internal_markup)
            lm = float(silicon_obj.internal_lm)
            quote_rate = calculate_quote_rate(base_rate, markup, lm)
            quote_price += quote_rate * lm

        if silicon_obj.polyamide_base_rate and silicon_obj.polyamide_gasket != 0 and silicon_obj.polyamide_lm:
            base_rate = float(silicon_obj.polyamide_base_rate)
            markup = float(silicon_obj.polyamide_markup)
            lm = float(silicon_obj.polyamide_lm)
            quote_rate = calculate_quote_rate(base_rate, markup, lm)
            quote_price += quote_rate * lm

        if silicon_obj.transom_base_rate and silicon_obj.transom_gasket != 0 and silicon_obj.transom_lm:
            base_rate = float(silicon_obj.transom_base_rate)
            markup = float(silicon_obj.transom_markup)
            lm = float(silicon_obj.transom_lm)
            quote_rate = calculate_quote_rate(base_rate, markup, lm)
            quote_price += quote_rate * lm

        if silicon_obj.mullion_base_rate and silicon_obj.mullion_gasket != 0 and silicon_obj.mullion_lm:
            base_rate = float(silicon_obj.mullion_base_rate)
            markup = float(silicon_obj.mullion_markup)
            lm = float(silicon_obj.mullion_lm)
            quote_rate = calculate_quote_rate(base_rate, markup, lm)
            quote_price += quote_rate * lm

        silicon_obj.silicon_quoted_price = math.ceil(quote_price)
        silicon_obj.save()
        return True
    else:
        return False
    

def quotation_number_update(quotation):
    """
    This function updates the quotation approval number and quotation ID for a given quotation based on
    the existing quotations for the same enquiry.
    
    :param quotation: The quotation object that needs to be updated with a new quotation approval number
    and quotation ID
    :return: a boolean value of True.
    """
    enquiry = Enquiries.objects.get(pk=quotation.estimations.enquiry.id)
    quotations = Quotations.objects.filter(estimations__enquiry=enquiry.id, estimations__version__status__in=[6, 12, 13, 15])
    
    quotation_approval_numbers = [quotation.quoatation_approval_number for quotation in quotations if quotation.quoatation_approval_number is not None]
    
    if len(quotation_approval_numbers) != 0:
        # if len(quotation_approval_numbers) == 1:
        #     approval_number = 1
        # else:
        max_val = max(quotation_approval_numbers)
        approval_number = int(max_val)+1
    else:
        approval_number = 1
    
    if quotation.quoatation_approval_number:
        quotation.quoatation_approval_number = approval_number
        if '/' in quotation.quotation_id:
            new_number = str((quotation.quotation_id).split('/')[0])+'/'+str(approval_number)
            quotation.quotation_id = new_number
        else:
            quotation.quotation_id =  str(quotation.quotation_id)+'/'+str(approval_number)
    quotation.save()
    return True
        
        
def product_details(request, pk):
    """
    This function calculates and returns various product details based on the given primary key.
    
    :param request: The HTTP request object containing metadata about the current request
    :param pk: The primary key of the main product object
    :return: a dictionary containing various calculated values and objects based on the input primary
    key (pk).
    """
    
    DETAILS_URLS = [
        '/Estimation/estimation_pricing_summary/',
        '/Estimation/estimation_list_enquiry/',
        '/Estimation/estimation_list_by_boq_enquiry/',
        '/Estimation/building_category_summary/',
        '/Enquiries/create_quotation_base/',
        '/Estimation/building_price_print/',
        '/Estimation/edit_estimation_pricing/',
        '/Enquiries/edit_enq_specifications/',
        '/Estimation/add_estimation_pricing/',
        '/Estimation/update_pricing_summary/',
        '/Enquiries/product_duplicate/',
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
        '/Estimation/estimation_product_delete/',
        '/Estimation/building_delete/',
        '/Estimation/reset_sync_data/',
        '/Estimation/disable_products/',
    ]
    main_product = None
    aluminium_obj = None
    glass_obj = None
    second_glass_obj = None
    silicon_obj = None
    pricing_control = None
    
    if any(path in request.path for path in DETAILS_URLS):
        MainProduct = EstimationMainProduct
        AluminiumModel = MainProductAluminium
        MainProductAddonCostModel = MainProductAddonCost
        EstimationModel = Estimations
        MainProductGlassModel = MainProductGlass
        PricingOptionModel = PricingOption
        MainProductSiliconModel = MainProductSilicon
    else:
        MainProduct = Temp_EstimationMainProduct
        AluminiumModel = Temp_MainProductAluminium
        MainProductAddonCostModel = Temp_MainProductAddonCost
        EstimationModel = Temp_Estimations
        MainProductGlassModel = Temp_MainProductGlass
        PricingOptionModel = Temp_PricingOption
        MainProductSiliconModel = Temp_MainProductSilicon
        
    main_product = MainProduct.objects.get(pk=pk)
    aluminium_obj = AluminiumModel.objects.get(estimation_product=pk)
    
    try:
        glass_obj = MainProductGlassModel.objects.get(estimation_product=pk, glass_primary=True)
    except MainProductGlassModel.DoesNotExist:
        glass_obj = None
        
    second_glass_obj = MainProductGlassModel.objects.select_related('estimation_product').filter(estimation_product=pk, glass_primary=False)
    try:
        silicon_obj = MainProductSiliconModel.objects.get(estimation_product=pk)
    except MainProductSiliconModel.DoesNotExist:
        silicon_obj = None
    try:
        pricing_control = PricingOptionModel.objects.get(estimation_product=pk)
    except PricingOptionModel.DoesNotExist:
        pricing_control = None
        
    
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
    silicon_price = 0
    if main_product.have_merge and main_product.deduction_method == 3:
        if aluminium_obj and main_product.category.handrail:
            dimension = str(int(aluminium_obj.width))
        elif aluminium_obj:
            dimension = str(int(aluminium_obj.width)) + '*' + str(int(aluminium_obj.height))
        unit_area = float(aluminium_obj.area)
        if main_product.building.typical_buildings_enabled:
            typical_qty = main_product.building.no_typical_buildings
        else:
            typical_qty = 1
        quantity = float(aluminium_obj.total_quantity)*float(typical_qty)
        total_area = float(unit_area) * float(quantity)
        estimated_value = float(main_product.merge_price)
    else:
        if not main_product.deduction_method == 3 or not main_product.deduction_method:
            if aluminium_obj and main_product.category.handrail:
                dimension = str(int(aluminium_obj.width))
            elif aluminium_obj:
                dimension = str(int(aluminium_obj.width)) + '*' + str(int(aluminium_obj.height))
            if main_product.deduction_method == 2:
                deducted_area = float(aluminium_obj.area) - float(main_product.deducted_area)
                unit_area = deducted_area
            else:
                unit_area = float(aluminium_obj.area)
             
            if main_product.building.typical_buildings_enabled:
                typical_qty = main_product.building.no_typical_buildings
            else:
                typical_qty = 1
            
            quantity = float(aluminium_obj.total_quantity)*float(typical_qty)
                
            total_area = float(unit_area) * float(quantity)
            unit_price = 0
            if aluminium_obj.al_quoted_price:
                unit_price += float(aluminium_obj.al_quoted_price)
            if glass_obj and glass_obj.is_glass_cost and glass_obj.glass_quoted_price:
                unit_price += float(glass_obj.glass_quoted_price)
            if second_glass_obj:
                for second_glass in second_glass_obj:
                    if second_glass.glass_quoted_price:
                        unit_price += float(second_glass.glass_quoted_price)
            if silicon_obj and silicon_obj.is_silicon:
                unit_price += float(silicon_obj.silicon_quoted_price)
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
            estimated_value = (estimated_values) if not main_product.after_deduction_price else float(main_product.after_deduction_price)
            
        else:
            estimated_value = 0
            total_price = 1
            quantity = 1
            total_area = 1
    total_price = round((float(round(estimated_value, 2)) * int(quantity)), 2)
    round_total_price = math.ceil(total_price)
    try:
        rp_sqm = total_price / total_area
    except Exception:
        rp_sqm = 0
    
    data = {
        'dimension': dimension,
        'unit_area': str(unit_area),
        'quantity': str(quantity),
        'total_area': total_area,
        'unit_price': math.ceil(round(estimated_value, 2)),
        'round_unit_price': math.ceil(round(estimated_value, 2)),
        'total_price': (float(math.ceil(round(estimated_value, 2)))*float(quantity)),
        'round_total_price': round_total_price,
        'main_pro': main_product,
        'rp_sqm': (float(round(estimated_value, 2)))/(float(unit_area))
    }
    return data


def merge_summary_count2(request, pk, version, sqm=None, base_rate=None, product=None):
    """
    This function calculates various pricing and quantity values for a given set of products based on
    their specifications and other parameters.
    
    """
    sqm2 = int(sqm)
    
    PATHS = [
        '/Estimation/product_merge_summary/',
        '/Estimation/merge_summary_print/',
        '/Enquiries/create_quotation_base/',
        '/Estimation/merge_summary_print_2/',
        '/Estimation/edit_estimation_pricing/',
        '/Estimation/add_estimation_pricing/',
        '/Estimation/update_pricing_summary/',
        '/Enquiries/product_duplicate/',
        '/Enquiries/building_duplicate/',
        '/Estimation/add_associated_product/',
        '/Estimation/add_typical_buildings/',
        '/Enquiries/edit_enq_specifications/',
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
        '/Estimation/sync_associated_data_full/' ,
        '/Estimation/estimation_product_delete/',
        '/Estimation/building_delete/',
        '/Estimation/reset_sync_data/',
        '/Estimation/disable_products/',
    ]
    if any(path in request.path for path in PATHS):
        MainProduct = EstimationMainProduct
        AluminiumModel = MainProductAluminium
        
    else:
        MainProduct = Temp_EstimationMainProduct
        AluminiumModel = Temp_MainProductAluminium
        
    if base_rate:
        products = MainProduct.objects.filter(
                                                building__estimation=version, 
                                                specification_Identifier=pk,
                                                product_base_rate=base_rate,
                                                disabled=False
                                            )
    else:
        products = MainProduct.objects.filter(
                                                building__estimation=version, 
                                                specification_Identifier=pk, 
                                                product_sqm_price_without_addon__startswith=str(sqm2),
                                                disabled=False
                                            )
    
    quantity = 0
    area = 0
    total_area = 0
    aluminium_rate = 0
    glass_rate = 0
    material_cost = 0
    labour_overhead = 0
    tolarance_price = 0
    total_price = 0
    round_total_price = 0
    typical_qty = 1
    accessory_price = 0
    silicon_price = 0
    sub_total = 0
    addon_cost = 0
    unit_price = 0
    price_per_sqm = 0

    ids = []
    
    for pro in products:
        product = MainProduct.objects.get(pk=pro.id)
        aluminium = AluminiumModel.objects.get(estimation_product=product.id)
        if pro.building.typical_buildings_enabled:
            typical_qty = pro.building.no_typical_buildings
        else:
            typical_qty = 1
        quantity += float(aluminium.total_quantity)*float(typical_qty)
        product_prices = product_unit_price(request=request, pk=product.id)
        aluminium_rate += float(product_prices['aluminium_rate'])*float(typical_qty)
        glass_rate += float(product_prices['glass_rate'])*float(typical_qty)
        material_cost += float(product_prices['material_cost'])*float(typical_qty)
        labour_overhead += float(product_prices['labour_overhead'])*float(typical_qty)
        tolarance_price += float(product_prices['tolarance_price'])*float(typical_qty)
        accessory_price += float(product_prices['accessory_price'])*float(typical_qty)
        silicon_price += float(product_prices['silicon_price'])*float(typical_qty)
        sub_total += float(product_prices['sub_total'])*float(typical_qty)
        addon_cost += float(product_prices['addon'])*float(typical_qty)
        unit_price += float(product_prices['unit_price'])*float(typical_qty)
        
        if pro.product_type == 1:
            total_price1 = (float(product_prices['total_price'])*float(typical_qty))
            total_price += total_price1
            
            if pro.have_merge:
                round_total_price += (float(product_prices["round_total_price"])*float(aluminium.total_quantity)*float(typical_qty))
            else:
                round_total_price += (float(math.ceil(product_prices["round_total_price"]))*float(typical_qty))
        else:
            if not pro.main_product.have_merge:
                total_price += (float(product_prices['total_price'])*float(typical_qty))
                round_total_price += (float(product_prices["round_total_price"] )*float(typical_qty))
                
        if product.category.is_curtain_wall:
            area = float(aluminium.area)
            total_area += float(aluminium.area)*(float(aluminium.total_quantity)*float(typical_qty))
        else:
            area = float(aluminium.area)
            total_area += float(aluminium.area)*(float(aluminium.total_quantity)*float(typical_qty))

        ids.append(product.id)

    data = {
        'quantity': quantity,
        'area': area,
        'total_area': total_area,
        'ids': ids,
        'aluminium_rate': aluminium_rate,
        'glass_rate': glass_rate,
        'material_cost': material_cost,
        'labour_overhead': labour_overhead,
        'tolarance_price': tolarance_price,
        'total_price': total_price,
        'round_total_price': round_total_price,
        'accessory_price': accessory_price,
        'silicon_price': silicon_price,
        'sub_total': sub_total,
        'addon_cost': addon_cost,
        'unit_price': unit_price,
        'price_per_sqm': price_per_sqm,
    }
    return data


def material_summary_data(request, pk):
    """
    This function calculates the total cost of materials and labor for an estimation or quotation.
    """
    # alumin_total = 0
    # # galss_price = 0
    # total_addon_cost = 0
    # total_access_price = 0
    # addon_cost = 0
    # access_price = 0
    # unit_price1 = 0
    # total_labour = 0
    # total_overhead = 0
    # total_tolarance = 0
    # overall_total = 0
    # unit_price = 0
    # glass_total1 = 0
    # glass_total = 0
    # sec_glass_total1 = 0
    # sec_glass_total = 0
    # galss_price = 0
    # galss_price1 = 0
    # tolarance_price = 0
    # silicon_total = 0
    # silicon_price = 0
    # silicon_price1 = 0
    # tolarance_unit_total = 0
    # silicon_total1 = 0
    material_total_total = 0
    # price = []
    # unit_total = 0
    # final_price = 0
    # unit_labour = 0
    # unit_overhead = 0
    # merge_total = 0
    # quantity = []
    
    
    PATHS = [
                '/Estimation/estimation_summary/',
                '/Estimation/material_summary_data/',
                '/Enquiries/product_category_summary/',
                '/Enquiries/open_enquiry/',
                '/Enquiries/edit_enq_specifications/',
                '/Enquiries/create_quotation_base/',
                '/Estimation/view_revision_history/',
                '/Estimation/edit_estimation_pricing/',
                '/Estimation/add_estimation_pricing/',
                '/Estimation/update_pricing_summary/',
                '/Enquiries/product_duplicate/',
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
                '/Estimation/estimation_product_delete/',
                '/Estimation/building_delete/',
                '/Estimation/reset_sync_data/',
                '/Estimation/disable_products/',
            ]
    if any(path in request.path for path in PATHS):
        MainProduct = EstimationMainProduct
        AluminiumModel = MainProductAluminium
        MainProductAddonCostModel = MainProductAddonCost
        EstimationModel = Estimations
        MainProductGlassModel = MainProductGlass
        PricingOptionModel = PricingOption
        MainProductSiliconModel = MainProductSilicon
    else:
        MainProduct = Temp_EstimationMainProduct
        AluminiumModel = Temp_MainProductAluminium
        MainProductAddonCostModel = Temp_MainProductAddonCost
        EstimationModel = Temp_Estimations
        MainProductGlassModel = Temp_MainProductGlass
        PricingOptionModel = Temp_PricingOption
        MainProductSiliconModel = Temp_MainProductSilicon
    
    estimation = EstimationModel.objects.get(pk=pk)   
    try:
        main_products = MainProduct.objects.filter(building__estimation=estimation, disabled=False).order_by('id')
    except:
        main_products = None
        
    pro_total = 0
    total_price = 0
    labour_total = 0
    overhead_total = 0
    addons_price = 0
    tolarance_price = 0
    
    if main_products:
        for main_product in main_products:
            price_data = have_deducted_associated(request, main_product.id)
            pro_total += price_data['new_total_price']
            
            # alumin_total += price_data['new_alumn']
            # glass_total += price_data['new_infill']
            # glass_total += price_data['new_infill']
            # silicon_total += price_data['new_infill']
            
            material_total_total += price_data['new_com_display']
            overhead_total += price_data['new_overhead']
            labour_total += price_data['new_labour']
            addons_price += price_data['addons_price']
            tolarance_price += price_data['tolarance_price']
            
    
    final_total =  math.ceil(material_total_total + overhead_total + labour_total + addons_price + tolarance_price)
    data = {
        # 'alumin_total': float(alumin_total),
        # 'glass_total': float(galss_price),
        # 'silicon_total': float(silicon_price),
        # 'addon_cost': float(addon_cost),
        # 'access_price': float(access_price),
        # 'overall_total': float(final_price),
        # 'total_labour': float(total_labour),
        # 'total_overhead': float(total_overhead),
        # 'total_tolarance': float(total_tolarance),
        # 'round_overall_total': float(final_price)
        
        'overall_total': pro_total,
        "total_price": final_total,
    }
    return data



def update_pricing_summary(request, pk):
    """
    This function updates the pricing summary for an estimation project based on various factors such as
    scope of work, product summary, material summary, and specifications.
    
    """
    scope_of_work_price = 0
    product_summary_price = 0
    material_summary_price = 0
    
    product_summary = None
    spec_list = []
    PATHS = [
        '/Enquiries/create_quotation_base/',
        '/Estimation/edit_estimation_pricing/',
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
        '/Estimation/estimation_product_delete/',
        '/Estimation/building_delete/',
        '/Estimation/reset_sync_data/',
        '/Estimation/disable_products/',
    ]
    
    if any(path in request.path for path in PATHS):
        MainProduct = EstimationMainProduct
        AluminiumModel = MainProductAluminium
        MainProductAddonCostModel = MainProductAddonCost
        EstimationModel = Estimations
        MainProductGlassModel = MainProductGlass
        PricingOptionModel = PricingOption
        MainProductSiliconModel = MainProductSilicon
        EnquirySpecificationsModel = EnquirySpecifications
        Pricing_SummaryModel = Pricing_Summary
        QuotationsModel = Quotations
    else:
        MainProduct = Temp_EstimationMainProduct
        AluminiumModel = Temp_MainProductAluminium
        MainProductAddonCostModel = Temp_MainProductAddonCost
        EstimationModel = Temp_Estimations
        MainProductGlassModel = Temp_MainProductGlass
        PricingOptionModel = Temp_PricingOption
        MainProductSiliconModel = Temp_MainProductSilicon
        EnquirySpecificationsModel = Temp_EnquirySpecifications
        Pricing_SummaryModel = Temp_Pricing_Summary
        QuotationsModel = Temp_Quotations
        
        
            
    estimation = EstimationModel.objects.get(pk=pk)
    products = MainProduct.objects.filter(building__estimation=estimation.id, disabled=False)
    specification = EnquirySpecificationsModel.objects.filter(estimation=estimation.id)
    try:
        quotation = QuotationsModel.objects.get(estimations=estimation)
    except:
        quotation = None
        
    material_summary = material_summary_data(request, pk=estimation.id)
    # material_summary_price += material_summary['round_overall_total']
    material_summary_price += material_summary['overall_total']
    
    for spec in specification:
        curtain_wall_products = MainProduct.objects.filter(
            category__is_curtain_wall=True,
            building__estimation=estimation.id,
            specification_Identifier=spec,
            disabled=False
        ).annotate(
            product_sqm_price_without_addon_int=Func(F('product_sqm_price_without_addon'), function='FLOOR')
        ).distinct('product_sqm_price_without_addon_int', 'product__product_name')
        
        other_products = MainProduct.objects.filter(
                                    category__is_curtain_wall=False, 
                                    building__estimation=estimation.id, 
                                    specification_Identifier=spec,
                                    disabled=False
                                    ).distinct('product_base_rate', 'product__product_name')
        
        for prod in curtain_wall_products:
            product_summary1 = merge_summary_count2(request, pk=spec.id, version=estimation.id, sqm=prod.product_sqm_price_without_addon, product=prod.id)
            product_summary_price += product_summary1['round_total_price']
            
        for prod in other_products:
            product_summary2 = merge_summary_count2(request, pk=spec.id, version=estimation.id, sqm=prod.product_sqm_price_without_addon, base_rate=prod.product_base_rate, product=prod.id)
            product_summary_price += product_summary2['round_total_price']
            
    for product in products:
        scope_price = product_details(request, product.id)
        if product.specification_Identifier not in set(spec_list):
            spec_list.append(product.specification_Identifier)
        if product.product_type == 1:
            scope_of_work_price += (scope_price['total_price'])
        else:
            if not product.main_product.have_merge: 
                scope_of_work_price += (scope_price['total_price'])
    
    try:
        summary_price = Pricing_SummaryModel.objects.get(estimation=estimation.id)
        summary_price.scope_of_work = scope_of_work_price
        summary_price.product_summary = product_summary_price
        summary_price.weightage_summary = material_summary['total_price']
        summary_price.pricing_review_summary=material_summary_price
        summary_price.material_summary=material_summary_price
        if quotation:
            summary_price.quotation=scope_of_work_price
    except Exception as e:
        summary_price = Pricing_SummaryModel(
                                                estimation=estimation, 
                                                scope_of_work=scope_of_work_price, 
                                                product_summary=product_summary_price, 
                                                weightage_summary=material_summary['total_price'], 
                                                material_summary=material_summary_price, 
                                                pricing_review_summary=material_summary_price, 
                                                quotation=scope_of_work_price if quotation else 0
                                            )
    summary_price.save()
    

def generate_random_4_digit_hex():
    """
    The function generates a random 4-digit hexadecimal number.
    :return: a randomly generated 4-digit hexadecimal number.
    """
    digits = "0123456789ABCDEF"
    random_hex = ""
    for _ in range(4):
        random_hex += random.choice(digits)
    return random_hex


def delete_files_in_folder(folder_path):
    """
    The function `delete_files_in_folder` deletes all files in a specified folder.
    
    """
    file_list = os.listdir(folder_path)
    for file_name in file_list:
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
    
     
def quotation_pdf_update(request, quotation):
    quotation = Quotations.objects.get(pk=quotation.id)
    random_4_digit_hex = generate_random_4_digit_hex()
    quotation_file_name = f'{str(quotation.estimations.enquiry.title)}_Quotation_{random_4_digit_hex}.pdf'
    buildings = EstimationBuildings.objects.filter(estimation=quotation.estimations, disabled=False).order_by('id')
    price_summary = Pricing_Summary.objects.get(estimation=quotation.estimations.id)
    quotation.quote_price = price_summary.quotation
    quotation.save()
    
    specifications_obj = EnquirySpecifications.objects.filter(estimation=quotation.estimations).distinct(
                            'categories', 
                            'panel_specification', 
                            'aluminium_system', 
                            'surface_finish', 
                            'aluminium_products',
                            'is_description'
                            )
    provisions_obj = Quotation_Provisions.objects.filter(quotation=quotation).order_by('id')
    template= 'print_templates/quotation_print_template.html'
    footer_template = get_template('print_templates/quotation_print_footer.html')
    header_template = get_template('print_templates/quotation_print_header.html')
    
    context={
            'title': f'{PROJECT_NAME}| Quotation Privew',
            'quotations': quotation,
            "specifications_obj": specifications_obj,
            "buildings": buildings,
            "filter_by_boq": False,
            "provisions_obj": provisions_obj,
            "estimation": quotation.estimations,
        }
    cmd_options = {
        'quiet': True, 
        'enable-local-file-access': True, 
        'margin-top': '38mm', 
        'header-spacing': 5,
        'minimum-font-size': 12,
        'page-size': 'A4',
        'encoding': "UTF-8",
        'print-media-type': True,
        'footer-right': "[page] / [topage]",
        'footer-font-size': 8,                    
    }
    
    if quotation.estimations.enquiry.enquiry_type == 1:
        clean_string  = re.sub(r'[^\w\s\-\.]', '', quotation_file_name)
        response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=True, 
                                        footer_template=footer_template, header_template=header_template, 
                                        template=template, context=context)
        pdf_data = io.BytesIO(response.rendered_content)
        version_str = 'Original' if quotation.estimations.version.version == '0' else 'Revision '+str(quotation.estimations.version.version)
        pdf_file_path2 = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
            str(quotation.estimations.enquiry.main_customer.name) + '/'+str(version_str)+'/' + clean_string
        
        folder = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
            str(quotation.estimations.enquiry.main_customer.name) + '/'+str(version_str)
        if not os.path.exists(folder):
            os.makedirs(folder)
        else:
            delete_files_in_folder(folder)
            
        with open(pdf_file_path2, 'wb') as f:
            f.write(pdf_data.getbuffer())
            
    else:
        for customer in quotation.prepared_for.all():
            
            clean_string  = re.sub(r'[^\w\s\-\.]', '', quotation_file_name)
            customer_name = Customers.objects.get(pk=customer.id)
            context['customer'] = customer_name
            response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=True, 
                                            footer_template=footer_template, header_template=header_template, 
                                            template=template, context=context)
            pdf_data = io.BytesIO(response.rendered_content)

            version_str = 'Original' if quotation.estimations.version.version == '0' else 'Revision '+str(quotation.estimations.version.version)
            
            pdf_file_path2 = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                str(customer_name.name) + '/'+str(version_str)+'/' + clean_string
                
            folder = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                str(customer_name.name) + '/'+str(version_str)
            if not os.path.exists(folder):
                os.makedirs(folder)
            else:
                delete_files_in_folder(folder)
                
            with open(pdf_file_path2, 'wb') as f:
                f.write(pdf_data.getbuffer())
    # return redirect('estimation_quotations_list', pk=quotation.estimations.id)
    return True


def quotation_by_boq_enquiry_function(request, pk, temp=None):
    
    if temp:
        estimation = Estimations.objects.get(pk=pk)
        buildings = EstimationBuildings.objects.filter(
            estimation=estimation).order_by('id')

        enquiry_obj = Enquiries.objects.get(pk=estimation.enquiry.id)
        boq_obj = BillofQuantity.objects.filter(
            enquiry=enquiry_obj.id).distinct('boq_number')
        context = {
            "buildings": buildings,
            "enquiry_obj": enquiry_obj,
            "estimation": estimation,
            "boq_obj": boq_obj,
            "filter_by_boq": True
        }
        return render(request, 'Enquiries/quotations/quotation_data_building_boq.html', context)
    
    else:
        estimation = Estimations.objects.get(pk=pk)
        quotation = Quotations.objects.get(estimations=pk)
        random_4_digit_hex = generate_random_4_digit_hex()
        price_summary = Pricing_Summary.objects.get(estimation=quotation.estimations.id)
        quotation.quote_price = price_summary.quotation
        quotation.save()
        quotation_file_name = f'{str(quotation.estimations.enquiry.title)}_Quotation_{random_4_digit_hex}.pdf'
        buildings = EstimationBuildings.objects.filter(estimation=quotation.estimations).order_by('id')
        boq_obj = BillofQuantity.objects.filter(enquiry=quotation.estimations.enquiry.id).distinct('boq_number')
        specifications_obj = EnquirySpecifications.objects.filter(estimation=quotation.estimations).distinct(
                                'categories', 
                                'panel_specification', 
                                'aluminium_system', 
                                'surface_finish', 
                                'aluminium_products',
                                'is_description'
                                )
        provisions_obj = Quotation_Provisions.objects.filter(quotation=quotation).order_by('id')
        template= 'print_templates/quotation_print_template.html'
        footer_template = get_template('print_templates/quotation_print_footer.html')
        header_template = get_template('print_templates/quotation_print_header.html')
        context={
                'title': f'{PROJECT_NAME}| Quotation Privew',
                'quotations': quotation,
                "specifications_obj": specifications_obj,
                "buildings": buildings,
                "filter_by_boq": True,
                "provisions_obj": provisions_obj,
                "estimation": quotation.estimations,
                "boq_obj": boq_obj,
            }
        cmd_options = {
            'quiet': True, 
            'enable-local-file-access': True, 
            'margin-top': '38mm', 
            'header-spacing': 5,
            'minimum-font-size': 12,
            'page-size': 'A4',
            'encoding': "UTF-8",
            'print-media-type': True,
            'footer-right': "[page] / [topage]",
            'footer-font-size': 8,                    
        }
        
        if quotation.estimations.enquiry.enquiry_type == 1:
            clean_string  = re.sub(r'[^\w\s\-\.]', '', quotation_file_name)
            response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=True, 
                                            footer_template=footer_template, header_template=header_template, 
                                            template=template, context=context)
            pdf_data = io.BytesIO(response.rendered_content)

            version_str = 'Original' if quotation.estimations.version.version == '0' else 'Revision '+str(quotation.estimations.version.version)
            pdf_file_path2 = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                str(quotation.estimations.enquiry.main_customer.name) + '/'+str(version_str)+'/' + clean_string
            
            folder = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                str(quotation.estimations.enquiry.main_customer.name) + '/'+str(version_str)
            if not os.path.exists(folder):
                os.makedirs(folder)
            else:
                delete_files_in_folder(folder)
                
            with open(pdf_file_path2, 'wb') as f:
                f.write(pdf_data.getbuffer())
        else:
            for customer in quotation.prepared_for.all():
                clean_string  = re.sub(r'[^\w\s\-\.]', '', quotation_file_name)
                customer_name = Customers.objects.get(pk=customer.id)
                context['customer'] = customer_name
                response = PDFTemplateResponse(request=request, cmd_options=cmd_options, show_content_in_browser=True, 
                                                footer_template=footer_template, header_template=header_template, 
                                                template=template, context=context)
                pdf_data = io.BytesIO(response.rendered_content)
                version_str = 'Original' if quotation.estimations.version.version == '0' else 'Revision '+str(quotation.estimations.version.version)
                
                pdf_file_path2 = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                    str(customer_name.name) + '/'+str(version_str)+'/' + clean_string
                    
                folder = MEDIA_URL+ 'Quotations/' + str(quotation.estimations.enquiry.enquiry_id) + '/' +\
                    str(customer_name.name) + '/'+str(version_str)
                if not os.path.exists(folder):
                    os.makedirs(folder)
                else:
                    delete_files_in_folder(folder)
                    
                with open(pdf_file_path2, 'wb') as f:
                    f.write(pdf_data.getbuffer())
        return True

def estimation_ai_rating(enquiry):
    enquiry_obj = Enquiries.objects.get(pk=enquiry)
    product_count_Original = EstimationMainProduct.objects.filter(building__estimation__enquiry=enquiry_obj, disabled=False).count()
    product_count_temp = Temp_EstimationMainProduct.objects.filter(building__estimation__enquiry=enquiry_obj, disabled=False).count()
    smallest_from_value_entry = AI_RatingModel.objects.order_by('to_value').first().to_value
    
    time_data = EnquiryUser.objects.filter(enquiry=enquiry_obj)
    total_active_time_seconds = sum([entry.active_time.total_seconds() for entry in time_data])
    
    total_product_count = product_count_Original+product_count_temp
    if total_product_count > 0:
        system_calculated_time = total_product_count*smallest_from_value_entry
        ai_label = total_active_time_seconds/total_product_count
    
        matching_entry = AI_RatingModel.objects.filter(from_value__lte=ai_label, to_value__gte=ai_label).first()
        data = {
            'matching_entry': matching_entry,
            'total_active_time_seconds': seconds_to_hh_mm(total_active_time_seconds),
        }
        return data
    else:
        return None
    
    
def seconds_to_hh_mm(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (minutes % 3600) // 360
    return "{:02d}:{:02d}:{:02d}".format(int(hours), int(minutes), int(seconds))


def min_price_setup(request, pk):
    
    PATHS = [
        
        '/Estimation/edit_estimation_pricing/',
        '/Estimation/add_estimation_pricing/',
        '/Estimation/update_pricing_summary/',
        '/Enquiries/product_duplicate/',
        '/Estimation/add_associated_product/',
        '/Estimation/multiple_scope_add/',
        '/Enquiries/building_duplicate/'
        
    ]
    
    if any(path in request.path for path in PATHS):
        MainProduct = EstimationMainProduct
        AluminiumModel = MainProductAluminium
        MainProductGlassModel = MainProductGlass
        MainProductSiliconModel = MainProductSilicon
        MainProductAccessoriesModel = MainProductAccessories
        
    else:
        MainProduct = Temp_EstimationMainProduct
        AluminiumModel = Temp_MainProductAluminium
        MainProductGlassModel = Temp_MainProductGlass
        MainProductSiliconModel = Temp_MainProductSilicon
        MainProductAccessoriesModel = Temp_MainProductAccessories
        
    # main_product= get_object_or_404(MainProduct, id=pk)
    main_product= MainProduct.objects.get(id=pk)
    # aluminium_product = get_object_or_404(AluminiumModel, estimation_product=main_product)
    aluminium_product = AluminiumModel.objects.get(estimation_product=main_product)
    # glass_product = get_object_or_404(MainProductGlassModel, estimation_product=main_product)
    try:
        glass_product = MainProductGlassModel.objects.get(estimation_product=main_product, glass_primary=True)
    except Exception as e:
        glass_product = None
    # silicon_product = get_object_or_404(MainProductSiliconModel, estimation_product=main_product)
    try:
        silicon_product = MainProductSiliconModel.objects.get(estimation_product=main_product)
    except Exception as e:
        silicon_product = None
    
    
    weight_per_unit = aluminium_product.weight_per_unit
    area = aluminium_product.area
    infill_base = 0
    silicon_price = 0
    accessory_price = 0
    tolarance_price = 0 
    surface_finish_price = 0
    
    aluminium_base_rates = PriceMaster.objects.last()
    
    base_loh = Labour_and_OverheadMaster.objects.last()
    
    
    if glass_product and glass_product.is_glass_cost:
        infill_base = (glass_product.glass_base_rate)*area
    
    if silicon_product and silicon_product.is_silicon:
        silicon_price = float(silicon_product.silicon_quoted_price)
        
    if main_product and main_product.accessory_total and main_product.is_accessory:
        accessory_price = float(main_product.accessory_total)
    if aluminium_product.surface_finish:
        surface_finish_price = float(aluminium_product.surface_finish.surface_finish_price)
    
    addon_cost = float(main_product.total_addon_cost)
    aluminium_rate = float(weight_per_unit)*float(aluminium_base_rates.price_per_kg)+float(surface_finish_price)
    minimum_com = (aluminium_rate)+float(infill_base)+float(silicon_price)+float(accessory_price)
    
    if main_product.is_tolerance:
        if main_product.tolerance_type == 1: # percentage
            tolarance = int(main_product.tolerance)/100
            tolarance_price = float(float(weight_per_unit)*float(aluminium_base_rates.price_per_kg))*tolarance
        elif main_product.tolerance_type == 2:
            tolarance_price = float(main_product.tolerance)
        else:
            tolarance_price = 0
    
    labour_price = float(minimum_com)*(float(base_loh.labour_percentage)/100)
    overhead_price = float(minimum_com)*(float(base_loh.overhead_percentage)/100)
    
   
    minimum_subtotal = float(minimum_com)+float(labour_price)+float(overhead_price)
    if main_product.specification_Identifier.specification_type == 1:
        minimum_price_per_unit = float(minimum_subtotal)+float(addon_cost)+float(tolarance_price)
    else:
        minimum_price_per_unit = main_product.specification_Identifier.minimum_price
    
    return minimum_price_per_unit


def audit_log(request, data):
    PATHS = [
        '/Estimation/edit_estimation_pricing/',
        '/Estimation/add_estimation_pricing/',
        '/Estimation/add_associated_product/',
        '/Estimation/consolidate_aluminium_update/', 
        '/Estimation/consolidate_price_update/',
        '/Estimation/consolidate_addon_update/',
        '/Estimation/consolidate_sealant_update/',
        '/Estimation/consolidate_loh_update/',
        '/Enquiries/product_category_summary/',
        '/Estimation/merge_summary_update_spec/',
        '/Estimation/merge_summary_update/',
        '/Enquiries/update_product_category_percentage/',
        '/Estimation/consolidate_unitprice_update/',
        
        
        
    ]
    if any(path in request.path for path in PATHS):
        AuditLogModelData = AuditLogModel
        EstimationsModel = Estimations
        EstimationMainProductModel = EstimationMainProduct
        AluminiumModel = MainProductAluminium
    else:
        AuditLogModelData = Temp_AuditLogModel
        EstimationsModel = Temp_Estimations
        EstimationMainProductModel = Temp_EstimationMainProduct
        AluminiumModel = Temp_MainProductAluminium
    
    user= data['user']
    estimation  = EstimationsModel.objects.get(pk=int(data['estimation']))
    product = EstimationMainProductModel.objects.get(pk=data['product'])
    aluminium_obj = AluminiumModel.objects.get(estimation_product=product)
    
    old_area = data['old_area']
    new_area = data['new_area']
    old_quantity = data['old_quantity']
    new_quantity = data['new_quantity']
    old_price = data['old_price']
    new_price = data['new_price']
    action = data['action']
    module_label = data['Module']
    old_sqm = data['old_sqm']
    new_sqm = data['new_sqm']
    
    area_change = None
    quantity_change = None
    price_change = None
    sqm_change = None
    
    message = ''
    if action == 'UPDATE':
        if old_price or new_price:
            if float(round(old_price, 1)) != float(round(new_price, 1)):
                log_price_message = "Price changed from {} to {} ".format(old_price , round(new_price, 2))
                message = log_price_message
                price_change = True
                
        if old_area or new_area:
            if float(old_area) != float(new_area):
                log_area_message = "Area changed from {} SqM to {} SqM ".format(old_area , new_area)
                message = log_area_message
                area_change = True
                
        if old_quantity or new_quantity:
            if float(old_quantity) != float(new_quantity):
                log_quantity_message = "Quantity changed from {} to {} ".format(old_quantity , new_quantity)
                message = log_quantity_message
                quantity_change = True
            
        if old_sqm and new_sqm:
            if round(float(old_sqm), 2) != round(float(new_sqm), 2):
                log_quantity_message = "SqM Price changed from {} to {} ".format(old_sqm , round(float(new_sqm), 2))
                message = log_quantity_message
                sqm_change = True
            
            
        if price_change and area_change and not quantity_change:
            message = str(log_price_message)+' and '+ str(log_area_message)
        elif price_change and quantity_change and not area_change:
            message = str(log_price_message)+' and '+ str(log_quantity_message)
        elif not price_change and quantity_change and  area_change:
            message = str(log_area_message)+' and '+str(log_quantity_message)
            
        if price_change or area_change or quantity_change:
            audit_message = aluminium_obj.product_type+' | '+product.product.product_name + ' Product Updated in '+product.building.building_name +\
                        ' Version Original with '+str(message) if product.product else aluminium_obj.product_type+' | '+product.panel_product.product_name +\
                        ' Product Updated in '+product.building.building_name+' Version Original with '+str(message) if product.building.estimation.version.version == '0'\
                        else aluminium_obj.product_type+' | '+product.product.product_name + ' Product Updated in '+product.building.building_name+\
                        +' Version Revison '+str(product.building.estimation.version.version)+' with '+str(message) if product.product else aluminium_obj.product_type+' | '+product.\
                        panel_product.product_name + ' Product updated in '+product.building.building_name+' Version Revison ' +\
                        str(product.building.estimation.version.version)+' with '+str(message)
                        
            log = AuditLogModelData(
                    message=audit_message,
                    estimation=estimation,
                    user=user,
                    product=product,
                    old_price=float(old_price) if price_change else None,
                    new_price=float(new_price) if price_change else None,
                    old_area=float(old_area) if area_change else None,
                    new_area=float(new_area) if area_change else None,
                    old_quantity=float(old_quantity) if quantity_change else None,
                    new_quantity=float(new_quantity) if quantity_change else None,
                    old_sqm=float(old_sqm) if sqm_change else None,
                    new_sqm=float(new_sqm) if sqm_change else None,
                    module=module_label,
            )
            log.save()
            
    elif action == 'ADD':
        message = "Price {} Quantity {} and Area {}".format(round(new_price, 2), new_quantity, new_area)
                        
        audit_message = aluminium_obj.product_type+' | '+product.product.product_name + ' Product Added in '+product.building.building_name +\
                        ' Version Original with '+str(message) if product.product else aluminium_obj.product_type+' | '+product.panel_product.product_name +\
                        ' Product Added in '+product.building.building_name+' Version Original with '+str(message) if product.building.estimation.version.version == '0'\
                        else aluminium_obj.product_type+' | '+product.product.product_name + ' Product Added in '+product.building.building_name+\
                        +' Version Revison '+str(product.building.estimation.version.version)+' with '+str(message) if product.product else aluminium_obj.product_type+' | '+product.\
                        panel_product.product_name + ' Product Added in '+product.building.building_name+' Version Revison ' +\
                        str(product.building.estimation.version.version)+' with '+str(message)
                        
        log = AuditLogModelData(
                message=audit_message,
                estimation=estimation,
                user=user,
                product=product,
                old_price=None,
                new_price=round(float(new_price), 2),
                old_area=None,
                new_area=float(new_area),
                old_quantity=None,
                new_quantity=float(new_quantity) if quantity_change else None,
                old_sqm=float(old_sqm) if sqm_change else None,
                new_sqm=float(new_sqm) if sqm_change else None,
                module=module_label,
            )
        log.save()
        

def set_index(request, pk):
    PATHS = [
        '/Estimation/add_estimation_pricing/',
        '/Estimation/add_associated_product/',
        '/Enquiries/product_duplicate/',
        '/Estimation/multiple_scope_add/',
    ]
    
    if any(path in request.path for path in PATHS):
        BuildingModel = EstimationBuildings
        ProductModel = EstimationMainProduct
    else:
        BuildingModel = Temp_EstimationBuildings
        ProductModel = Temp_EstimationMainProduct
        
    building = BuildingModel.objects.get(pk=pk)
    product_count = ProductModel.objects.filter(building=building).count()
    
    return product_count
        
    
def category_summary_data_excel(request, pk):
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




