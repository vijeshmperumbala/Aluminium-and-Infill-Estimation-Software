from django.utils import timezone
from django import template
from django.db.models import Sum, Q
from apps.Categories.models import Category
from apps.estimations.models import EstimationMainProduct, MainProductAluminium

from apps.projects.models import Eps_Products, ProjectContractItems, SalesOrderItems, Schedule_Product
register = template.Library()


@register.simple_tag
def get_auth_quantity(request, pk):
    """
    This function retrieves and calculates the difference between the authorized quantity and the main
    product quantity or area for a given project contract item.
    
    """
    try:
        product = ProjectContractItems.objects.get(product=pk)
        try:
            main_product = MainProductAluminium.objects.get(estimation_product=pk)
            if product.product.eps_uom == 1:
                qty_diff = float(main_product.quantity) - float(product.authorised_quantity)
            else:
                qty_diff = float(main_product.total_area) - float(product.authorised_quantity)
                
                
            # if main_product.estimation_product.category.is_curtain_wall:
            #     qty_diff = float(main_product.area) - float(product.authorised_quantity)
            # else:
            #     qty_diff = float(main_product.quantity) - float(product.authorised_quantity)
        except Exception as e:
            main_product = None
            qty_diff = 0

    except Exception as e:
        product = None
        qty_diff = 0
    return (
        {
            'infill_quantity': product.infill_quantity,
            'authorised_quantity': product.authorised_quantity,
            'qty_diff': round(qty_diff, 2),
            'issued_quantity': product.issued_quantity,
        }
        if product
        else {
            'infill_quantity': '0.00',
            'authorised_quantity': '0.00',
            'qty_diff': '0.00',
            'issued_quantity': '0.00',
        }
    )
    

    
@register.simple_tag
def get_scheduled_data(pk):
    products = Eps_Products.objects.get(pk=pk)
    date_flag = None
    
    try:
        schecule_producted = Schedule_Product.objects.get(product__main_products__main_product=products)
        
        current_date = timezone.now().date()
        if schecule_producted.start_date >= current_date:
            date_flag = True
       
        data = {
            'schecule_producted': schecule_producted.id,
            'schecule_status': schecule_producted.shopfloor_status,
            'date_flag': date_flag,
        }
        
    except Exception as e:
        print("EXCE==>", e) 
        data = {
            'schecule_producted': None,
            'date_flag': date_flag,
            'schecule_status': None,
        }
        
    return data
    
    
@register.simple_tag
def sales_items_bygroup(pk):
    return SalesOrderItems.objects.filter(sales_group=pk, product_type__in=[1,2]).order_by('id')

@register.simple_tag
def sales_items_bygroup_eps_uom(pk):
    return SalesOrderItems.objects.filter(sales_group=pk, product_type__in=[1,2], eps_uom__isnull=False).order_by('id')

@register.simple_tag
def sales_items_bygroup_for_elevation_assign(pk):
    return SalesOrderItems.objects.filter(sales_group=pk, product_type__in=[1,2], 
                                          building__isnull=True, 
                                          elevation__isnull=True, 
                                          floor__isnull=True
                                        ).order_by('id')

@register.simple_tag
# def sales_items_bygroup_for_category_filter(pk, category=None):
#     if category:
#         return SalesOrderItems.objects.filter(sales_group=pk, category=category, 
#                                               specification_Identifier__aluminium_system=True, 
#                                               specification_Identifier__aluminium_specification=True, 
#                                               specification_Identifier__aluminium_series=True,
#                                             ).order_by('id')
#     else:
#         return SalesOrderItems.objects.filter(sales_group=pk,
#                                               specification_Identifier__aluminium_system=True, 
#                                               specification_Identifier__aluminium_specification=True, 
#                                               specification_Identifier__aluminium_series=True,
#                                             ).order_by('id')

def sales_items_bygroup_for_category_filter(pk, category=None):
    base_filter = Q(sales_group=pk)

    if category:
        category_obj = Category.objects.get(pk=category)
        category_filter = Q(category=category)
        if not category_obj.one_D:
            aluminium_filter = Q()
        else:
            aluminium_filter = (
                # Q(specification_Identifier__aluminium_system__isnull=False)
                Q(specification_Identifier__aluminium_system__isnull=False) &
                Q(specification_Identifier__aluminium_specification__isnull=False) &
                Q(specification_Identifier__aluminium_series__isnull=False) 
            )
            
    else:
        category_filter = Q()
        aluminium_filter = Q()
        
    #     aluminium_filter = ( 
    #             Q(specification_Identifier__aluminium_system__isnull=False) &
    #             Q(specification_Identifier__aluminium_specification__isnull=False) &
    #             Q(specification_Identifier__aluminium_series__isnull=False) if not specification_Identifier__category__one_D = True else None
                
    #         )
        
    combined_filter = base_filter & category_filter & aluminium_filter

    return SalesOrderItems.objects.filter(combined_filter).order_by('id')
        


@register.simple_tag
def sales_item_details(pk):
    try:
        details = SalesOrderItems.objects.get(pk=pk)
    except Exception:
        details = None
    return details


@register.simple_tag
def process_product_check(pk):
    product = SalesOrderItems.objects.get(pk=pk)
    try:
        if product.category.is_curtain_wall:
            flag = ProjectContractItems.objects.get(product=product, authorised_quantity=product.area)
        else:
            flag = ProjectContractItems.objects.get(product=product, authorised_quantity=product.quantity)
    except Exception as w:
        flag = None
            
    return flag
