from django import template
from apps.estimations.models import (
                EstimationMainProduct, 
                MainProductAluminium, 
                EstimationMainProduct, 
                Temp_EstimationMainProduct, 
                Temp_MainProductAluminium
)
from apps.functions import product_unit_price
register = template.Library()


@register.simple_tag
def merge_summary_count(request, pk, version, sqm=None, base_rate=None, product=None):
    """
    This function calculates various summary counts and prices for a given set of products in an
    estimation.
    """
    sqm2 = int(sqm) if sqm else None
    PATHS = [
        '/Estimation/product_merge_summary/',
        '/Estimation/merge_summary_print/',
        '/Enquiries/product_category_summary/',
        '/Estimation/merge_summary_print_2/',
        '/Estimation/costing_summary/',
    ]

    if any(path in request.path for path in PATHS):
        EstimationMainProductModel = EstimationMainProduct
        MainProductAluminiumModel = MainProductAluminium
    else:
        EstimationMainProductModel = Temp_EstimationMainProduct
        MainProductAluminiumModel = Temp_MainProductAluminium


    if base_rate:
        products = EstimationMainProductModel.objects.filter(
                            building__estimation=version, 
                            specification_Identifier=pk,
                            product_base_rate=base_rate,
                            disabled=False,
                        )
    elif sqm2:
        products = EstimationMainProductModel.objects.filter(
                                    building__estimation=version, 
                                    specification_Identifier=pk, 
                                    product_sqm_price_without_addon__startswith=str(sqm2), 
                                    disabled=False,
                                )
    else:
        products = EstimationMainProductModel.objects.filter(
                        building__estimation=version, 
                        specification_Identifier=pk,
                        disabled=False,
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
    unit_price_for_merge = 0
    sub_total_area = 0
    ids = []

    for pro in products:
        product = EstimationMainProductModel.objects.get(pk=pro.id)
        aluminium = MainProductAluminiumModel.objects.get(estimation_product=product.id)

        if pro.building.typical_buildings_enabled:
            typical_qty = pro.building.no_typical_buildings
        else:
            typical_qty = 1
            
        quantity += float(aluminium.total_quantity)*float(typical_qty)
        if pro.deduction_method == 2 or pro.deduction_method == 1:
            total_area += (float(aluminium.total_area) - (float(pro.deducted_area)*float(aluminium.total_quantity))) * float(typical_qty)
        # elif pro.deduction_method == 3:
        #     associated_products = EstimationMainProductModel.objects.filter(main_product=pro, product_type=2)
        #     for associated in associated_products:
        #         sub_aluminium = MainProductAluminiumModel.objects.get(estimation_product=associated.id)
        #         sub_total_area += float(sub_aluminium.area) * float(sub_aluminium.total_quantity)
                
        #     total_area += float(aluminium.area) * float(aluminium.total_quantity) + float(sub_total_area)
        else:
            total_area += float(aluminium.area) * float(aluminium.total_quantity) * float(typical_qty)
            
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
        unit_price_for_merge += float(product_prices['unit_price_massupdate'])*float(typical_qty)

        if pro.product_type == 1:
            if not pro.have_merge:
                total_price1 = (float(product_prices['total_price'])*float(typical_qty))
                total_price += total_price1

                round_total_price += (
                    (
                        float(product_prices["round_total_price"])
                        * float(aluminium.total_quantity)
                        * float(typical_qty)
                    )
                    if pro.have_merge
                    else (
                        float(product_prices["round_total_price"])
                        * float(typical_qty)
                    )
                )
            else:
                # total_price1 = (float(product_prices['total_price'])*float(typical_qty))
                total_price1 = (float(product_prices['unit_price_massupdate'])*float(typical_qty))
                total_price += total_price1

                round_total_price += (
                    (
                        # float(product_prices["round_total_price"])
                        float(product_prices["unit_price_massupdate"])
                        * float(aluminium.total_quantity)
                        * float(typical_qty)
                    )
                    if pro.have_merge
                    else (
                        # float(product_prices["round_total_price"])
                        float(product_prices["unit_price_massupdate"])
                        * float(typical_qty)
                    )
                )
                
        else:
            if not pro.have_merge:
                total_price += (float(product_prices['total_price'])*float(typical_qty))
                round_total_price += (float(product_prices["round_total_price"] )*float(typical_qty))
            else:
                total_price += (float(product_prices['unit_price_massupdate'])*float(typical_qty))
                round_total_price += (float(product_prices["unit_price_massupdate"] )*float(typical_qty))
        
        area = float(aluminium.area)
        ids.append(product.id)
        
    return {
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
        'unit_price_for_merge': unit_price_for_merge,
    }    