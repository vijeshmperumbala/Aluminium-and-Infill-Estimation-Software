
from django import template

from apps.estimations.models import (
    EstimationMainProduct, 
    MainProductAccessories, 
    MainProductAddonCost, 
    MainProductAluminium, 
    MainProductGlass, 
    MainProductSilicon, 
    Temp_EstimationMainProduct, 
    Temp_MainProductAccessories, 
    Temp_MainProductAddonCost, 
    Temp_MainProductAluminium, 
    Temp_MainProductGlass, 
    Temp_MainProductSilicon,
)

register = template.Library()


@register.simple_tag
def accessory_list(request, version, pk, type=None):
    """
    This function generates a list of accessories, addons, secondary glass, and sealants with their
    respective quantities based on the input parameters.
    
    :param request: The HTTP request object containing metadata about the current request
    :param version: The version of the estimation being accessed
    :param pk: The primary key of a product or panel product
    :param type: The "type" parameter is an optional parameter that is used to differentiate between two
    different types of products in the database. It is used to filter the data accordingly and retrieve
    the required information. If the value of "type" is 1, then the function retrieves data related to
    the primary product,
    :return: a dictionary containing data related to accessories, addons, secondary glass, and sealants.
    The keys of the dictionary are "accessory", "quantity", "addon_list", "addon_quantity",
    "sec_glass_list", "sce_glass_area", "sealant_list", and "sealant_data".
    """
    PATHS = [
                "/Estimation/material_summary_data/",
                "/Estimation/material_summary_data/",
                "/Estimation/material_summary_data_items/",
                "/Estimation/material_summary_data_items2/",
                "/Estimation/material_all_data_print/",
            ]

    if any(path in request.path for path in PATHS):
        MainProduct = EstimationMainProduct
        AluminiumModel = MainProductAluminium
        MainProductAddonCostModel = MainProductAddonCost
        MainProductGlassModel = MainProductGlass
        MainProductSiliconModel = MainProductSilicon
        MainProductAccessoriesModel = MainProductAccessories
    else:
        MainProduct = Temp_EstimationMainProduct
        AluminiumModel = Temp_MainProductAluminium
        MainProductAddonCostModel = Temp_MainProductAddonCost
        MainProductGlassModel = Temp_MainProductGlass
        MainProductSiliconModel = Temp_MainProductSilicon
        MainProductAccessoriesModel = Temp_MainProductAccessories


    if type == 1:
        sec_glass_obj = MainProductGlassModel.objects.filter(
                                estimation_product__building__estimation=version, 
                                estimation_product__product=pk, 
                                glass_primary=False
                            ).order_by('id')
        accessories_obj = MainProductAccessoriesModel.objects.filter(
                                            estimation_product__building__estimation=version, 
                                            estimation_product__product=pk
                                        ).order_by('id')
        addons_obj = MainProductAddonCostModel.objects.filter(
                                            estimation_product__building__estimation=version, 
                                            estimation_product__product=pk
                                        ).order_by('id')
        try:
            sealant_obj = MainProductSiliconModel.objects.filter(
                    estimation_product__building__estimation=version, 
                    estimation_product__product=pk
                )
        except Exception as e:
            sealant_obj = None
    else:
        sec_glass_obj = MainProductGlassModel.objects.filter(
                            estimation_product__building__estimation=version, 
                            estimation_product__panel_product=pk, 
                            glass_primary=False
                        ).order_by('id')
        accessories_obj = MainProductAccessoriesModel.objects.filter(
                                estimation_product__building__estimation=version, 
                                estimation_product__panel_product=pk
                            ).order_by('id')
        addons_obj = MainProductAddonCostModel.objects.filter(
                            estimation_product__building__estimation=version, 
                            estimation_product__panel_product=pk
                        ).order_by('id')
        try:
            sealant_obj = MainProductSiliconModel.objects.filter(
                                estimation_product__building__estimation=version, 
                                estimation_product__panel_product=pk
                                )
        except Exception as e:
            sealant_obj = None

    accessory_list = []
    quantity = {} 

    for accessory in accessories_obj:
        aluminium_obj = AluminiumModel.objects.get(estimation_product=accessory.estimation_product.id)
        main_product = MainProduct.objects.get(pk=accessory.estimation_product.id)

        if accessory.accessory_item not in accessory_list:
            accessory_list.append(accessory.accessory_item)
            if accessory.accessory_item.id in quantity:
                quantity[accessory.accessory_item.id] += float(main_product.accessory_quantity)\
                                *float(aluminium_obj.quantity)*float(accessory.accessory_item_quantity)
            else:
                quantity[accessory.accessory_item.id] = float(main_product.accessory_quantity)\
                                *float(accessory.accessory_item_quantity)*float(aluminium_obj.quantity)
        else:
            quantity[accessory.accessory_item.id] += float(main_product.accessory_quantity)\
                                *float(aluminium_obj.quantity)*float(accessory.accessory_item_quantity)

    addon_list = []
    addon_quantity = {}
    for addon in addons_obj:
        aluminium_obj = AluminiumModel.objects.get(estimation_product=addon.estimation_product.id)
        if addon.addons not in addon_list:
            addon_list.append(addon.addons)
            if addon.addons.id in addon_quantity:
                addon_quantity[addon.addons.id] += float(addon.addon_quantity)*float(aluminium_obj.quantity)
            else:
                addon_quantity[addon.addons.id] = float(addon.addon_quantity)*float(aluminium_obj.quantity)
        else:
            addon_quantity[addon.addons.id] += float(addon.addon_quantity)*float(aluminium_obj.quantity)


    sec_glass_list = []
    sce_glass_area = {}
    for sec_glass in sec_glass_obj:
        if sec_glass not in sec_glass_list:
            sec_glass_list.append(sec_glass)
            if sec_glass.id in sce_glass_area:
                sce_glass_area[sec_glass] += float(sec_glass.glass_area)*float(aluminium_obj.quantity)
            else:
                sce_glass_area[sec_glass] = float(sec_glass.glass_area)*float(aluminium_obj.quantity)
        else:
            sce_glass_area[sec_glass] += float(sec_glass.glass_area)*float(aluminium_obj.quantity)

    sealant_list = []
    sealant_data = {}

    if sealant_obj:
        for sealant in sealant_obj:
            aluminium_obj = AluminiumModel.objects.get(estimation_product=sealant.estimation_product.id)
            if sealant.external_sealant_type:
                sealant_list.append('External')
                if sealant.external_sealant_type in sealant_data:
                    sealant_data[sealant.external_sealant_type] += float(aluminium_obj.quantity)*float(sealant.external_lm)
                else:
                    sealant_data[sealant.external_sealant_type] = float(aluminium_obj.quantity)*float(sealant.external_lm)

            if sealant.internal_sealant_type:
                sealant_list.append('Internal')
                if sealant.internal_sealant_type in sealant_data:
                    sealant_data[sealant.internal_sealant_type] += float(sealant.internal_lm)*float(aluminium_obj.quantity)
                else:
                    sealant_data[sealant.internal_sealant_type] = float(sealant.internal_lm)*float(aluminium_obj.quantity)

    return {
        "accessory": accessory_list,
        "quantity": quantity,
        "addon_list": addon_list,
        "addon_quantity": addon_quantity,
        "sec_glass_list": sec_glass_list,
        "sce_glass_area": sce_glass_area,
        "sealant_list": sealant_list,
        "sealant_data": sealant_data,
    }
    