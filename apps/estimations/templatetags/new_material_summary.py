from django import template

from apps.estimations.models import EstimationMainProduct, MainProductAccessories, MainProductAddonCost, MainProductAluminium, MainProductGlass, MainProductSilicon, Temp_EstimationMainProduct, Temp_MainProductAccessories, Temp_MainProductAddonCost, Temp_MainProductAluminium, Temp_MainProductGlass, Temp_MainProductSilicon
from apps.product_parts.models import Profile_items

register = template.Library()

@register.simple_tag
def new_material_summary(request, pk):
    """
    This function retrieves data related to a main product for use in generating a summary.
    
    :param request: The HTTP request object sent by the client
    :param pk: pk is a parameter that represents the primary key of a MainProduct object, which is used
    to retrieve information about a specific product in the database
    :return: a dictionary object named "data" which contains various model objects and querysets related
    to a main product in an estimation. These objects include profiles, aluminium, accessories, addons,
    sealant, glass, and secondary glass.
    """
    if '/Estimation/edit_estimation_pricing/' in request.path:
        MainProduct = EstimationMainProduct
        AluminiumModel = MainProductAluminium
        MainProductGlassModel = MainProductGlass
        MainProductSiliconModel = MainProductSilicon
        MainProductAccessoriesModel = MainProductAccessories
        MainProductAddonCostModel = MainProductAddonCost
    else:
        MainProduct = Temp_EstimationMainProduct
        AluminiumModel = Temp_MainProductAluminium
        MainProductGlassModel = Temp_MainProductGlass
        MainProductSiliconModel = Temp_MainProductSilicon
        MainProductAccessoriesModel = Temp_MainProductAccessories
        MainProductAddonCostModel = Temp_MainProductAddonCost
        
    main_product = MainProduct.objects.get(pk=pk)
    aluminium_obj = AluminiumModel.objects.get(estimation_product=main_product)
    try:
        glass_obj = MainProductGlassModel.objects.get(estimation_product=main_product, glass_primary=True)
        sec_glass_obj = MainProductGlassModel.objects.filter(estimation_product=main_product, glass_primary=False).order_by('id')
    except:
        glass_obj = None
        sec_glass_obj = None
        
    accessories_obj = MainProductAccessoriesModel.objects.filter(estimation_product=main_product).order_by('id')
    addons_obj = MainProductAddonCostModel.objects.filter(estimation_product=main_product).order_by('id')
    try:
        sealant_obj = MainProductSiliconModel.objects.get(estimation_product=main_product)
    except:
        sealant_obj = None
    
    profiles = Profile_items.objects.filter(profile_kit=main_product.series).order_by('id')
    
    data = {
        "profiles": profiles,
        "aluminium_obj": aluminium_obj,
        "accessories_obj": accessories_obj,
        "addons_obj": addons_obj,
        "main_product": main_product,
        "sealant_obj": sealant_obj,
        "glass_obj": glass_obj,
        "sec_glass_obj": sec_glass_obj
    }
    return data