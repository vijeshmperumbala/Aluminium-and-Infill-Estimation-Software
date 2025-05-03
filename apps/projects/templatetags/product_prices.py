from django import template
import math
from apps.estimations.models import (
            MainProductAluminium, 
            MainProductGlass, 
            EstimationMainProduct, 
            MainProductSilicon, 
            PricingOption,
            MainProductAddonCost
)
from apps.projects.models import Eps_Products, Eps_infill_Details, SalesOrderItems
from django.shortcuts import get_object_or_404
register = template.Library()



def get_aluminium_total(estimation_product_id):
    aluminium_obj = get_object_or_404(MainProductAluminium, estimation_product=estimation_product_id)

    if (aluminium_obj.product_configuration or aluminium_obj.custom_price or aluminium_obj.price_per_kg) and aluminium_obj.al_quoted_price:
        return float(aluminium_obj.al_quoted_price)
    
    return 0

def get_glass_total(estimation_product_id):
    glass_obj = get_object_or_404(MainProductGlass, estimation_product=estimation_product_id, glass_primary=True)
    second_glass_objs = MainProductGlass.objects.filter(estimation_product=estimation_product_id, glass_primary=False).order_by('id')
    
    glass_total = 0
    
    if glass_obj and glass_obj.glass_base_rate:
        glass_total += float(glass_obj.glass_quoted_price)
    
    for second_glass in second_glass_objs:
        if second_glass.glass_base_rate:
            glass_total += float(second_glass.glass_quoted_price)
    
    return glass_total

def get_silicon_total(estimation_product_id):
    silicon_obj = get_object_or_404(MainProductSilicon, estimation_product=estimation_product_id)
    
    if silicon_obj and silicon_obj.silicon_quoted_price:
        return float(silicon_obj.silicon_quoted_price)
    
    return 0

def get_total_addon_cost(estimation_product_id):
    main_product = get_object_or_404(EstimationMainProduct, pk=estimation_product_id)
    
    if main_product.enable_addons:
        return float(main_product.total_addon_cost)
    
    return 0

def get_total_access_price(estimation_product_id):
    main_product = get_object_or_404(EstimationMainProduct, pk=estimation_product_id)
    
    if main_product.accessory_total and main_product.is_accessory:
        return float(main_product.accessory_total)
    
    return 0

def calculate_labour_price(material_total, labour_percentage):
    return float(material_total) * float(labour_percentage / 100)

def calculate_overhead_price(material_total, overhead_percentage):
    return float(material_total) * float(overhead_percentage / 100)

def calculate_tolerance_price(main_product, aluminium_total):
    if aluminium_total and main_product.is_tolerance:
        if main_product.tolerance_type == 1:
            tolerance = float(main_product.tolerance) / 100
            return float(aluminium_total) * tolerance
        elif main_product.tolerance_type == 2:
            return main_product.tolerance
        else:
            return 0
    
    return 0

def calculate_rate_per_unit(material_total, tolerance_price, labour_price, overhead_price, total_addon_cost, deduction_method, after_deduction_price):
    if (
        deduction_method != 2
        and not after_deduction_price
        or deduction_method == 2
    ):
        return float(material_total) + float(tolerance_price) + float(labour_price) + float(overhead_price) + float(total_addon_cost)
    else:
        return float(after_deduction_price)

@register.simple_tag
def product_prices(pk):
    main_product = get_object_or_404(SalesOrderItems, pk=pk)
    # aluminium_total = get_aluminium_total(pk)
    # glass_total = get_glass_total(pk)
    # silicon_total = get_silicon_total(pk)
    # total_addon_cost = get_total_addon_cost(pk)
    # total_access_price = get_total_access_price(pk)

    # material_total = (aluminium_total + glass_total + total_access_price + silicon_total)

    # pricing_control = get_object_or_404(PricingOption, estimation_product=pk)
    # labour_percent_price = calculate_labour_price(material_total, pricing_control.labour_perce)
    # overhead_percent_price = calculate_overhead_price(material_total, pricing_control.overhead_perce)
    # tolerance_price = calculate_tolerance_price(main_product, aluminium_total)

    # rate_per_unit = calculate_rate_per_unit(material_total, tolerance_price, labour_percent_price, overhead_percent_price, total_addon_cost, main_product.deduction_method, main_product.after_deduction_price)
    # glass_total += get_glass_total(pk)

    # if main_product.category.invoice_in_quantity:
    #     return round(float(rate_per_unit), 2)
    
    # aluminium_obj = get_object_or_404(MainProductAluminium, estimation_product=pk)
    if main_product.eps_uom == 1:
        price = main_product.unit_price
    else:
        price = round((float(main_product.unit_price) / float(main_product.area)), 2)
    return price

    
    
    
@register.simple_tag        
def eps_products(pk, type=None):
    if type:
        products_obj = Eps_infill_Details.objects.filter(form_infill_eps=True, eps_ref=pk)
    else:
        products_obj = Eps_Products.objects.filter(eps_data=pk)        
    return products_obj