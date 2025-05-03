from django import template
import json
from django.http import JsonResponse

from apps.estimations.models import MainProductAccessories, MainProductAluminium, MainProductGlass, MainProductAddonCost, EstimationMainProduct, MainProductSilicon, \
    PricingOption, Temp_EstimationMainProduct, Temp_MainProductAccessories, Temp_MainProductAddonCost, Temp_MainProductAluminium, Temp_MainProductGlass, Temp_MainProductSilicon, Temp_PricingOption
from apps.panels_and_others.models import PanelMasterConfiguration
from apps.product_parts.models import Profile_items

register = template.Library()


@register.simple_tag
def material_summmary_consolidate(request, version, pk, type):
    """
        Material Summary Data For Consolidate View
    """
    if '/Estimation/material_summary_data/' in request.path:
        EstimationMainProductModel = EstimationMainProduct
        MainProductAluminiumModel = MainProductAluminium
        MainProductGlassModel = MainProductGlass
        MainProductSiliconModel = MainProductSilicon
        PricingOptionModel = PricingOption
        MainProductAddonCostModel = MainProductAddonCost
        MainProductAccessoriesModel = MainProductAccessories
    else:
        EstimationMainProductModel = Temp_EstimationMainProduct
        MainProductAluminiumModel = Temp_MainProductAluminium
        MainProductGlassModel = Temp_MainProductGlass
        MainProductSiliconModel = Temp_MainProductSilicon
        PricingOptionModel = Temp_PricingOption
        MainProductAddonCostModel = Temp_MainProductAddonCost
        MainProductAccessoriesModel = Temp_MainProductAccessories
        
        
    try:
        if type == "pro":
            main_product = EstimationMainProductModel.objects.filter(building__estimation=version, product=pk)
        elif type == "panel":
            main_product = EstimationMainProductModel.objects.filter(building__estimation=version, panel_product=pk)
    except:
        main_product = None

    data_context = {
        "product": None,
        "product_id": pk,
        "aluminum": None,
        "profile_data": [{
            "code": None,
            "name": None,
            "quantity": None,
            "total_quantity": None,
            "unit_price": None,
            "total_price": None
        }],
        "glass": None,
        "glass_data": [{
            "spec": None,
            "quantity": None,
            "total_quantity": None,
            "unit_price": None,
            "total_price": None
        }],
        "sealant": None,
        "sealant_data": [{
            "name": None,
            "quantity": None,
            "total_quantity": None,
            "unit_price": None,
            "total_price": None
        }],
        "accessory": None,
        "accessory_data": [{
            "name": None,
            "quantity": None,
            "total_quantity": None,
            "unit": None,
            "unit_price": None,
            "total_price": None
        }],
        "addons": None,
        "addon_data": [{
            "name": None,
            "quantity": None,
            "total_quantity": None,
            "unit_price": None,
            "total_price": None
        }],

    }
    profile_data = {}
    glass_data = {}
    silicon_data = {}
    accessory_data = {}
    addon_data = {}
    

    for product in main_product:
        try:
            aluminium_obj = MainProductAluminiumModel.objects.get(
                estimation_product=product)
        except:
            aluminium_obj = None
        try:
            glass_obj = MainProductGlassModel.objects.get(
                estimation_product=product, glass_primary=True)
            second_glass_obj = MainProductGlassModel.objects.select_related(
                'estimation_product').filter(estimation_product=product, glass_primary=False)
        except:
            glass_obj = None
            second_glass_obj = None
        try:
            silicon_obj = MainProductSiliconModel.objects.get(
                estimation_product=product)
        except:
            silicon_obj = None
        try:
            pricing_control = PricingOptionModel.objects.get(
                estimation_product=product)
        except Exception as e:
            pricing_control = None
        addons = MainProductAddonCostModel.objects.select_related(
            'estimation_product').filter(estimation_product=product)

        accessories_obj = MainProductAccessoriesModel.objects.filter(estimation_product=product)
        if product.product:
            product_name = product.product
        else:
            product_name = product.panel_product
        data_context['product'] = str(product_name)
        # data_context['product_id'] = int(product.id)
        
        width = round(aluminium_obj.width, 2)
        height = round(aluminium_obj.height, 2)
        quantity = aluminium_obj.total_quantity

        divisions = aluminium_obj.enable_divisions
        horizontal = aluminium_obj.horizontal
        vertical = aluminium_obj.vertical
        curtainwall_type = aluminium_obj.curtainwall_type
        if aluminium_obj.is_conventional:
            is_conventional = aluminium_obj.is_conventional
            is_two_way = None
        else:
            is_two_way = aluminium_obj.is_two_way
            is_conventional = None
            
        price_per_kg = (float(product.building.estimation.enquiry.price_per_kg)*(float(product.building.estimation.enquiry.price_per_kg_markup)/100
                                                                                    ))+float(product.building.estimation.enquiry.price_per_kg)
        
        kit_items = Profile_items.objects.filter(
            profile_kit=product.series).order_by('id')
        

        for kit_item in kit_items:
            data_context['aluminum'] = aluminium_obj.id
            wight_per_lm = kit_item.profile.weight_per_lm
            if divisions:
                if kit_item.profile.profile_master_part.parts_name.lower() == 'mullion':
                    if curtainwall_type:
                        if is_conventional:
                            formula = 2*width+2*height
                        elif is_two_way:
                            formula = 2*width
                        else:
                            formula = kit_item.formula.replace("W", str(width)).replace("H", str(height))
                    else:
                        formula = kit_item.formula.replace("W", str(width)).replace("H", str(height))
                        
                    formulas = '(('+str(formula)+'+' + \
                        str(vertical)+'*'+str(height)+'))/1000'
                    lenght = eval(formulas)
                    weight = float(round(wight_per_lm, 2))*float(round(lenght, 2))
                elif kit_item.profile.profile_master_part.parts_name.lower() == 'transom':
                    if curtainwall_type:
                        if is_conventional:
                            formula = 2*width+2*height
                        elif is_two_way:
                            formula = 2*width
                        else:
                            formula = kit_item.formula.replace("W", str(width)).replace("H", str(height))
                    else:
                        formula = kit_item.formula.replace("W", str(width)).replace("H", str(height))
                    formulas = '(('+str(formula)+'+' + \
                        str(horizontal)+'*'+str(width)+'))/1000'
                    lenght = eval(formulas)
                    weight = float(round(wight_per_lm, 2))*float(round(lenght, 2))
                else:
                    if curtainwall_type:
                        if is_conventional:
                            formula = 2*width+2*height
                        elif is_two_way:
                            formula = 2*width
                        else:
                            formula = kit_item.formula.replace("W", str(width)).replace("H", str(height))
                    else:
                        formula = kit_item.formula.replace("W", str(width)).replace("H", str(height))
                    formulas = '('+str(formula)+')/1000'
                    lenght = eval(formulas)
                    weight = float(round(wight_per_lm, 2))*float(round(lenght, 2))
            else:
                if is_conventional:
                    formula = 2*width+2*height
                elif is_two_way:
                    formula = 2*width
                else:
                    formula = kit_item.formula.replace("W", str(width)).replace("H", str(height))
                formulas = '('+str(formula)+')/1000'
                lenght = eval(formulas)
                weight = float(round(wight_per_lm, 2))*float(round(lenght, 2))
            
            profile_data_sub = {}
            if not kit_item.profile.profile_master_part.parts_name in profile_data.keys():
                profile_data_sub['name'] = kit_item.profile.profile_master_part.parts_name
                profile_data_sub['code'] = kit_item.profile.profile_code
                profile_data_sub['quantity'] = weight
                profile_data_sub['total_quantity'] = float(
                    weight)*float(quantity)
                profile_data_sub['unit_price'] = price_per_kg
                profile_data_sub['total_price'] = float(
                    price_per_kg)*(float(weight)*float(quantity))
                profile_data[kit_item.profile.profile_master_part.parts_name] = profile_data_sub
            else:
                profile_data[kit_item.profile.profile_master_part.parts_name]['quantity'] = \
                    float(
                        profile_data[kit_item.profile.profile_master_part.parts_name]['quantity'])+float(weight)
                profile_data[kit_item.profile.profile_master_part.parts_name]['total_quantity'] = \
                    float(profile_data[kit_item.profile.profile_master_part.parts_name]
                            ['total_quantity'])+float(float(weight)*float(quantity))
                profile_data[kit_item.profile.profile_master_part.parts_name]['total_price'] = \
                    float(profile_data[kit_item.profile.profile_master_part.parts_name]['total_price']) +\
                    float(float(price_per_kg) *
                            (float(weight)*float(quantity)))
            data_context['profile_data'] = profile_data
        if glass_obj:
            glass_config = PanelMasterConfiguration.objects.filter(
                panel_specification=glass_obj.glass_specif).first()
            if glass_config:
                gl_unit_price = (float(glass_config.price_per_sqm)*(
                    float(glass_config.markup_percentage)/100))+float(glass_config.price_per_sqm)
            else:
                gl_unit_price = 0
                
            if not glass_obj.glass_specif.specifications in glass_data.keys():
                glass_data_sub = {}
                glass_data_sub['name'] = glass_obj.glass_specif.specifications
                glass_data_sub['code'] = '-'
                glass_data_sub['quantity'] = float(glass_obj.total_area_glass)
                glass_data_sub['total_quantity'] = float(
                    glass_obj.total_area_glass)*float(quantity)
                glass_data_sub['unit_price'] = gl_unit_price
                glass_data_sub['total_price'] = float(
                    gl_unit_price)*(float(glass_obj.total_area_glass)*float(quantity))
                glass_data[glass_obj.glass_specif.specifications] = glass_data_sub
            else:
                glass_data[glass_obj.glass_specif.specifications]['quantity'] = float(glass_data[glass_obj.glass_specif.specifications]['quantity'])+float(glass_obj.total_area_glass)
                glass_data[glass_obj.glass_specif.specifications]['total_quantity'] = float(glass_data[glass_obj.glass_specif.specifications]['total_quantity']) +\
                    float(float(glass_obj.total_area_glass)*float(quantity))
                glass_data[glass_obj.glass_specif.specifications]['total_price'] = float(glass_data[glass_obj.glass_specif.specifications]['total_price']) +\
                    float(float(gl_unit_price) *
                            (float(glass_obj.total_area_glass)*float(quantity)))
            if second_glass_obj:
                for sec_gl in second_glass_obj:
                    glass_config2 = PanelMasterConfiguration.objects.filter(
                        panel_specification=sec_gl.glass_specif).first()
                    if glass_config2:
                        gl_unit_price2 = (float(glass_config2.price_per_sqm)*(
                            float(glass_config2.markup_percentage)/100))+float(glass_config2.price_per_sqm)
                    else:
                        gl_unit_price2 = 0
                        
                    if not sec_gl.glass_specif.specifications in glass_data.keys():
                        glass_data_sub = {}
                        glass_data_sub['name'] = sec_gl.glass_specif.specifications
                        glass_data_sub['code'] = '-'
                        glass_data_sub['quantity'] = float(sec_gl.total_area_glass)
                        glass_data_sub['total_quantity'] = float(
                            sec_gl.total_area_glass)*float(quantity)
                        glass_data_sub['unit_price'] = gl_unit_price2
                        glass_data_sub['total_price'] = float(
                            gl_unit_price2)*(float(sec_gl.total_area_glass)*float(quantity))
                        glass_data[sec_gl.glass_specif.specifications] = glass_data_sub
                    else:
                        glass_data[sec_gl.glass_specif.specifications]['quantity'] = float(glass_data[sec_gl.glass_specif.specifications]['quantity'])+float(sec_gl.total_area_glass)
                        glass_data[sec_gl.glass_specif.specifications]['total_quantity'] = float(glass_data[sec_gl.glass_specif.specifications]['total_quantity']) +\
                            float(float(sec_gl.total_area_glass)*float(quantity))
                        glass_data[sec_gl.glass_specif.specifications]['total_price'] = float(glass_data[sec_gl.glass_specif.specifications]['total_price']) +\
                            float(float(gl_unit_price2) *
                                (float(sec_gl.total_area_glass)*float(quantity)))
            data_context['glass'] = glass_obj.id
            data_context['glass_data'] = glass_data
            
        if product.category.is_curtain_wall:
            if silicon_obj:
                if  silicon_obj.is_silicon:
                    if silicon_obj.external_base_rate and silicon_obj.external_sealant_type:
                        silicon_data_sub = {}
                        sealant_type = "External - "+silicon_obj.external_sealant_type.sealant_type.sealant_type
                        sealant_lm = silicon_obj.external_lm
                        sealant_total_lm = float(sealant_lm)*float(quantity)
                        sealant_unit_price = (float(silicon_obj.external_base_rate)*(float(silicon_obj.external_markup)/100))+float(silicon_obj.external_base_rate)
                        sealant_totla_price = float(sealant_unit_price)*float(sealant_total_lm)
                        if not sealant_type in silicon_data.keys():
                            silicon_data_sub['name'] = sealant_type
                            silicon_data_sub['code'] = '-'
                            silicon_data_sub['quantity'] = float(sealant_lm)
                            silicon_data_sub['total_quantity'] = sealant_total_lm
                            silicon_data_sub['unit_price'] = sealant_unit_price
                            silicon_data_sub['total_price'] = sealant_totla_price
                            silicon_data[sealant_type] = silicon_data_sub
                        else:
                            silicon_data[sealant_type]['quantity'] = float(silicon_data[sealant_type]['quantity'])+float(sealant_lm)
                            silicon_data[sealant_type]['total_quantity'] = float(silicon_data[sealant_type]['total_quantity'])+float(sealant_total_lm)
                            silicon_data[sealant_type]['total_price'] = float(silicon_data[sealant_type]['total_price'])+float(sealant_totla_price)
                    if silicon_obj.internal_base_rate and silicon_obj.internal_sealant_type:
                        silicon_data_sub = {}
                        sealant_type = "Internal - "+silicon_obj.internal_sealant_type.sealant_type.sealant_type
                        sealant_lm = silicon_obj.internal_lm
                        sealant_total_lm = float(sealant_lm)*float(quantity)
                        sealant_unit_price = (float(silicon_obj.internal_base_rate)*(float(silicon_obj.external_markup)/100))+float(silicon_obj.internal_base_rate)
                        sealant_totla_price = float(sealant_unit_price)*float(sealant_total_lm)
                        if not sealant_type in silicon_data.keys():
                            silicon_data_sub['name'] = sealant_type
                            silicon_data_sub['code'] = '-'
                            silicon_data_sub['quantity'] = float(sealant_lm)
                            silicon_data_sub['total_quantity'] = sealant_total_lm
                            silicon_data_sub['unit_price'] = sealant_unit_price
                            silicon_data_sub['total_price'] = sealant_totla_price
                            silicon_data[sealant_type] = silicon_data_sub
                        else:
                            silicon_data[sealant_type]['quantity'] = float(silicon_data[sealant_type]['quantity'])+float(sealant_lm)
                            silicon_data[sealant_type]['total_quantity'] = float(silicon_data[sealant_type]['total_quantity'])+float(sealant_total_lm)
                            silicon_data[sealant_type]['total_price'] = float(silicon_data[sealant_type]['total_price'])+float(sealant_totla_price)
                    if silicon_obj.polyamide_base_rate:
                        silicon_data_sub = {}
                        sealant_type = silicon_obj.polyamide_gasket.sealant_type.sealant_type
                        sealant_lm = silicon_obj.polyamide_lm
                        sealant_total_lm = float(sealant_lm)*float(quantity)
                        sealant_unit_price = (float(silicon_obj.polyamide_base_rate)*(float(silicon_obj.polyamide_markup)/100))+float(silicon_obj.polyamide_base_rate)
                        sealant_totla_price = float(sealant_unit_price)*float(sealant_total_lm)
                        if not sealant_type in silicon_data.keys():
                            silicon_data_sub['name'] = sealant_type
                            silicon_data_sub['code'] = '-'
                            silicon_data_sub['quantity'] = float(sealant_lm)
                            silicon_data_sub['total_quantity'] = sealant_total_lm
                            silicon_data_sub['unit_price'] = sealant_unit_price
                            silicon_data_sub['total_price'] = sealant_totla_price
                            silicon_data[sealant_type] = silicon_data_sub
                        else:
                            silicon_data[sealant_type]['quantity'] = float(silicon_data[sealant_type]['quantity'])+float(sealant_lm)
                            silicon_data[sealant_type]['total_quantity'] = float(silicon_data[sealant_type]['total_quantity'])+float(sealant_total_lm)
                            silicon_data[sealant_type]['total_price'] = float(silicon_data[sealant_type]['total_price'])+float(sealant_totla_price)
                            
                    if silicon_obj.transom_base_rate:
                        silicon_data_sub = {}
                        sealant_type = silicon_obj.transom_gasket.sealant_type.sealant_type
                        sealant_lm = silicon_obj.transom_lm
                        sealant_total_lm = float(sealant_lm)*float(quantity)
                        sealant_unit_price = (float(silicon_obj.transom_base_rate)*(float(silicon_obj.transom_markup)/100))+float(silicon_obj.transom_base_rate)
                        sealant_totla_price = float(sealant_unit_price)*float(sealant_total_lm)
                        if not sealant_type in silicon_data.keys():
                            silicon_data_sub['name'] = sealant_type
                            silicon_data_sub['code'] = '-'
                            silicon_data_sub['quantity'] = float(sealant_lm)
                            silicon_data_sub['total_quantity'] = sealant_total_lm
                            silicon_data_sub['unit_price'] = sealant_unit_price
                            silicon_data_sub['total_price'] = sealant_totla_price
                            silicon_data[sealant_type] = silicon_data_sub
                        else:
                            silicon_data[sealant_type]['quantity'] = float(silicon_data[sealant_type]['quantity'])+float(sealant_lm)
                            silicon_data[sealant_type]['total_quantity'] = float(silicon_data[sealant_type]['total_quantity'])+float(sealant_total_lm)
                            silicon_data[sealant_type]['total_price'] = float(silicon_data[sealant_type]['total_price'])+float(sealant_totla_price)
                            
                    if silicon_obj.mullion_base_rate:
                        silicon_data_sub = {}
                        sealant_type = silicon_obj.mullion_gasket.sealant_type.sealant_type
                        sealant_lm = silicon_obj.mullion_lm
                        sealant_total_lm = float(sealant_lm)*float(quantity)
                        sealant_unit_price = (float(silicon_obj.mullion_base_rate)*(float(silicon_obj.mullion_markup)/100))+float(silicon_obj.mullion_base_rate)
                        sealant_totla_price = float(sealant_unit_price)*float(sealant_total_lm)
                        if not sealant_type in silicon_data.keys():
                            silicon_data_sub['name'] = sealant_type
                            silicon_data_sub['code'] = '-'
                            silicon_data_sub['quantity'] = float(sealant_lm)
                            silicon_data_sub['total_quantity'] = sealant_total_lm
                            silicon_data_sub['unit_price'] = sealant_unit_price
                            silicon_data_sub['total_price'] = sealant_totla_price
                            silicon_data[sealant_type] = silicon_data_sub
                        else:
                            silicon_data[sealant_type]['quantity'] = float(silicon_data[sealant_type]['quantity'])+float(sealant_lm)
                            silicon_data[sealant_type]['total_quantity'] = float(silicon_data[sealant_type]['total_quantity'])+float(sealant_total_lm)
                            silicon_data[sealant_type]['total_price'] = float(silicon_data[sealant_type]['total_price'])+float(sealant_totla_price)

                    data_context['sealant'] = silicon_obj.id
                    data_context['sealant_data'] = silicon_data
        else:
            if accessories_obj:  
                for accessory in accessories_obj:
                    accessory_data_sub = {}
                    if not accessory.accessory_item.accessory.accessory_name in accessory_data.keys():
                        
                        accessory_data_sub['name'] = accessory.accessory_item.accessory.accessory_name
                        accessory_data_sub['code'] = '-' 
                        accessory_data_sub['quantity'] = float(accessory.accessory_item_quantity)
                        accessory_data_sub['total_quantity'] = float(accessory.accessory_item_quantity)*float(quantity)
                        accessory_data_sub['unit'] = accessory.accessory_item.accessory.uom.uom
                        accessory_data_sub['unit_price'] = float(accessory.accessory_item_price)
                        accessory_data_sub['total_price'] = float(accessory.accessory_item_price)*(float(accessory.accessory_item_quantity)*float(quantity))
                        accessory_data[accessory.accessory_item.accessory.accessory_name] = accessory_data_sub
                    else:
                        accessory_data[accessory.accessory_item.accessory.accessory_name]['quantity'] = float(accessory_data[accessory.accessory_item.\
                                        accessory.accessory_name]['quantity'])+float(accessory.accessory_item_quantity)
                        accessory_data[accessory.accessory_item.accessory.accessory_name]['total_quantity'] = float(accessory_data[accessory.accessory_item.\
                            accessory.accessory_name]['total_quantity'])+(float(accessory.accessory_item_quantity)*float(quantity))
                        accessory_data[accessory.accessory_item.accessory.accessory_name]['total_price'] = float(accessory_data[accessory.\
                            accessory_item.accessory.accessory_name]['total_price'])+(float(accessory.accessory_item_price)*\
                                (float(accessory.accessory_item_quantity)*float(quantity)))
                data_context['accessory'] = True
                data_context['accessory_data'] = accessory_data
        if addons:
            for addon in addons:
                addon_data_sub = {}
                if addon.addons:
                    if not addon.addons.addon in addon_data.keys():
                        addon_data_sub['name'] = addon.addons.addon
                        addon_data_sub['code'] = '-'
                        addon_data_sub['quantity'] = float(addon.addon_quantity)
                        addon_data_sub['total_quantity'] = float(addon.addon_quantity)*float(quantity)
                        addon_data_sub['unit_price'] = float(addon.base_rate)
                        addon_data_sub['total_price'] = float(addon.base_rate)*(float(addon.addon_quantity)*float(quantity))
                        addon_data[addon.addons.addon] = addon_data_sub
                    else:
                        addon_data[addon.addons.addon]['quantity'] = float(addon_data[addon.addons.addon]['quantity'])+float(addon.addon_quantity)
                        addon_data[addon.addons.addon]['total_quantity'] = float(addon_data[addon.addons.addon]['total_quantity'])+(float(addon.addon_quantity)*float(quantity))
                        addon_data[addon.addons.addon]['total_price'] = float(addon_data[addon.addons.addon]['total_price'])+(float(addon.base_rate)*(float(addon.addon_quantity)*float(quantity)))
            data_context['addons'] = True
            data_context['addon_data'] = addon_data
    return json.dumps(data_context)

    
    
    