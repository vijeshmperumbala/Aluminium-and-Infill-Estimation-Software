from django import template
# from apps.accessories_kit.models import AccessoriesKitItem
from apps.estimations.models import MainProductAccessories, MainProductAluminium, MainProductGlass, MainProductAddonCost, \
    EstimationMainProduct, MainProductSilicon, PricingOption, Temp_EstimationMainProduct, Temp_MainProductAccessories, Temp_MainProductAddonCost, \
        Temp_MainProductAluminium, Temp_MainProductGlass, Temp_MainProductSilicon, Temp_PricingOption

register = template.Library()


@register.simple_tag
def summary_calc(request, pk):
    """
    The function takes a request and a primary key as input, and returns a dictionary of related objects
    based on the path of the request.
    
    :param request: The HTTP request object that contains information about the current request, such as
    the URL, headers, and data
    :param pk: pk is a parameter that represents the primary key of an object in the database. It is
    used to retrieve a specific object from the database. In this case, it is used to retrieve an
    EstimationMainProduct object and related objects from the database
    :return: a dictionary named "main_products" which contains various objects related to an estimation
    product identified by the primary key "pk". The objects include the main product, aluminium object,
    glass object, addons, silicon object, second glass object, pricing control object, and accessories
    object. The specific models used to retrieve these objects depend on the URL path of the request.
    """
    
    PATHS = [
        '/Estimation/estimation_pricing_summary/',
        '/Estimation/edit_estimation_pricing/',
        '/Estimation/view_side_summary/',
        '/Estimation/edit_estimation_pricing_confirmation/',
        '/Estimation/merge_summary_update/',
        '/Estimation/material_summary_data/',
        '/Estimation/material_summary_data_export/',
        '/Estimation/material_summary_data_items/',
        '/Estimation/material_overview/',
        '/Estimation/material_overview_print/',
        '/Enquiries/product_category_summary/',
        '/Estimation/material_summary_data/',
        '/Estimation/consolidate_price_update/',
        '/Estimation/consolidate_summary_glass_items/',
        '/Estimation/material_summary_data_items2/',
        '/Estimation/material_all_data_print/',
        '/Estimation/merge_summary_update_spec/',
        '/Estimation/consolidate_addon_update/',
        '/Estimation/addons_filter_for_consolidate_update/',
        '/Estimation/consolidate_aluminium_update/',
        '/Estimation/category_wise_product/',
        '/Estimation/consolidate_sealant_update/',
        '/Estimation/consolidate_sealant_products/',
        '/Estimation/consolidate_loh_update/',
        '/Estimation/spec_data_loh/',
        '/Estimation/consolidate_unitprice_update/',
        '/Estimation/consolidate_unit_product/',
        '/Estimation/deduction_material_summary/',
    ]

    if any(path in request.path for path in PATHS):
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


    main_product = EstimationMainProductModel.objects.get(pk=pk)
    try:
        aluminium_obj = MainProductAluminiumModel.objects.get(estimation_product=pk)
    except Exception:
        aluminium_obj = None
    try:
        glass_obj = MainProductGlassModel.objects.get(estimation_product=pk, glass_primary=True)
        second_glass_obj = MainProductGlassModel.objects.select_related('estimation_product').filter(estimation_product=pk, glass_primary=False)
    except Exception:
        glass_obj = None
        second_glass_obj = None
    try:
        silicon_obj = MainProductSiliconModel.objects.get(estimation_product=pk)
    except Exception:
        silicon_obj = None
    addons = MainProductAddonCostModel.objects.select_related('estimation_product').filter(estimation_product=pk)
    try:
        pricing_control = PricingOptionModel.objects.get(estimation_product=pk)
    except Exception as e:
        pricing_control = None
    accessories_obj = MainProductAccessoriesModel.objects.filter(estimation_product=pk).order_by('id')


    return {
        "product": main_product,
        "aluminium_product": aluminium_obj,
        "glass_product": glass_obj,
        "addons": addons,
        "silicon_obj": silicon_obj,
        "second_glass_obj": second_glass_obj,
        "pricing_control": pricing_control,
        "accessories_obj": accessories_obj,
    }


