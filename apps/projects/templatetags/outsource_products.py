from django import template
from django.db.models import Sum, F, Q
from django.http import JsonResponse
from django.contrib.postgres.aggregates import ArrayAgg
from apps.estimations.models import (
        EstimationMainProduct, 
        MainProductAccessories, 
        MainProductAluminium, 
        MainProductGlass,
)

from apps.projects.models import (
        Eps_Outsource_items, 
        Eps_Outsourced_Data, 
        Eps_Product_Details,
        Eps_Products, 
        Eps_infill_Details,
        Outsource_receive_items,
        Outsource_receive_recode,
        SalesOrderAccessories,
        SalesOrderInfill,
        SalesOrderItems,
        Workstation_Associated_Products_Data,
        Workstation_Data,
)

register = template.Library()


# @register.simple_tag
# def outsource_products(infill, eps_product, types=None):
#     """
#     This function retrieves data related to outsourced products based on specified infill and EPS
#     parameters.
    
#     """
#     eps_product = Eps_Products.objects.get(pk=eps_product)
#     if not types:
#         infill_data_details = Eps_Outsource_items.objects.filter(
#             infill_product__main_product=eps_product,
#             infill_product__infill__panel_specification=infill,
#             infill_product__is_outsourced=True,
#             out_source_batch__isnull=False,
#         ).values(
#             'infill_product__infill__panel_specification__specifications',
#             'infill_product__infill_width',
#             'infill_product__infill_code',
#             'infill_product__infill_height',
#             'infill_product__infill_area',
#         ).annotate(
#             total_infill_quantity=Sum('infill_product__infill_quantity'),
#             received_quantities=Sum('received_quantity'),
#             remaining_quantities=Sum('remaining_quantity'),
#             ids=ArrayAgg('id'),
#             estimation_product=ArrayAgg('infill_product__main_product__eps_product__product'),
#             infill_status=F('status')
#         )

#     else:
#         infill_data_details = Eps_Outsource_items.objects.filter(
#             infill_product__main_product=eps_product,
#             infill_product__infill__panel_specification=infill,
#             infill_product__is_outsourced=True,
#             out_source_batch__isnull=True,
#         ).values(
#             'infill_product__infill__panel_specification__specifications',
#             'infill_product__infill_width',
#             'infill_product__infill_code',
#             'infill_product__infill_height',
#             'infill_product__infill_area',
#         ).annotate(
#             total_infill_quantity=Sum('infill_product__infill_quantity'),
#             received_quantities=Sum('received_quantity'),
#             remaining_quantities=Sum('remaining_quantity'),
#             ids=ArrayAgg('id'),
#             estimation_product=ArrayAgg('infill_product__main_product__eps_product__product'),
#             infill_status=F('status')
#         )
#     id_list = [infill['ids'] for infill in infill_data_details]
#     flat_list = [item for sublist in id_list for item in sublist]
#     new_ids = []
#     for infills in infill_data_details:
#         new_ids.extend(iter(infills['ids']))
#     outsource_data = Eps_Outsourced_Data.objects.filter(
#         eps=eps_product.eps_data, products__infill_product__infill__panel_specification__in=[infill], products__in=new_ids
#     ).distinct('outsource_number')

#     return {
#         'infill_data_details': infill_data_details,
#         'ids': flat_list,
#         'outsource_data': outsource_data,
#     }
    
@register.simple_tag
def outsource_products(infill, eps_product):
    """
    This function retrieves data related to outsourced products based on specified infill and EPS
    parameters.
    
    """
    eps_product = Eps_Products.objects.get(pk=eps_product)
    infill_objs = Eps_infill_Details.objects.filter(
        infill__panel_specification=infill,
        main_product=eps_product,
        eps_ref=eps_product.eps_data,
    )
    return infill_objs

@register.simple_tag
def eps_infill_details(spec, pk):
    """
    This function returns EPS infill details for a specific glass specification and main product.
    """
    
    details_objs = Eps_infill_Details.objects.filter(
        infill__panel_specification=spec, main_product=pk
    )
    return details_objs

@register.simple_tag
def product_data(pk):
    """
    The function retrieves a single instance of EstimationMainProduct model based on the primary key
    provided.
    
    """
    return SalesOrderItems.objects.get(pk=pk)

@register.simple_tag
def product_infill_data(pk):
    """
    The function retrieves the primary glass data for a given estimation product ID.
    
    """
    return SalesOrderInfill.objects.get(product=pk, infill_primary=True)

@register.simple_tag
def product_alumin_data(pk):
    """
    This function retrieves data for a specific MainProductAluminium object based on its primary key.
    
    """
    return MainProductAluminium.objects.get(estimation_product=pk)

@register.simple_tag
def product_accessories(pk):
    """
    This function calculates the total quantity of accessories required for a given main product and its
    details.
    
    """
    products = Eps_Product_Details.objects.filter(main_product=pk)

    data_list = []
    for product in products:
        # data = MainProductAccessories.objects.filter(estimation_product=product.main_product.eps_product.product.id)
        data = SalesOrderAccessories.objects.filter(product=product.main_product.eps_product.product.id)
        for accossory in data:
            formula = accossory.accessory_item.accessory_formula
            width = product.product_width
            height = product.product_height
            quantity = 0
            
            if formula:
                new_formula = formula.replace('W', str(width)).replace('H', str(height))
                if formula == 0:
                    quantity = eval(new_formula)/1000
                else:
                    quantity = accossory.accessory_item_quantity

            total_quantity = float(quantity)*float(product.product_quantity)
            accossory_name = accossory.accessory_item.accessory.accessory_name
            if accossory_dic := next(
                (item for item in data_list if item["Name"] == accossory_name),
                None,
            ):
                # accossory_dic['quantity'] += round(quantity, 2)
                accossory_dic['total_quantity'] += round(total_quantity, 2)
            else:
                quantity = accossory.accessory_item_quantity
                total_quantity = float(quantity)*float(product.product_quantity)

                accossory_dic = {
                    'Name': accossory_name,
                    'quantity': round(quantity, 2),
                    'total_quantity': round(total_quantity, 2),
                    'uom': accossory.accessory_item.accessory.uom.uom
                }
                data_list.append(accossory_dic)

    return data_list

@register.simple_tag
def get_product_details(pk):
    """
    This function retrieves all product details for a given main product ID.
    """
    return Eps_Product_Details.objects.filter(main_product=pk)

@register.simple_tag
def get_associated_product(pk):
    main_product = Workstation_Data.objects.get(pk=pk)
    return Workstation_Associated_Products_Data.objects.filter(
        eps_product_id=main_product.eps_product_id,
        product__main_product=main_product.product.main_products,
        is_completed=True,
    ) 
    
# @register.simple_tag
# def outsource_item_remaning(pk):
#     outsourced_products = Eps_Outsource_items.objects.filter(infill_product=pk)
#     remaining = 0
#     pro_remaining = 0
    
#     if outsourced_products:
#         print("SS")
#         for outsourced_product in outsourced_products:
#             print("KJKS")
#             infill_pro = Eps_infill_Details.objects.get(pk=outsourced_product.infill_product.id)
#             pro_remaining += outsourced_product.actual_quantity
#             print("outsourced_product.actual_quantity==>", outsourced_product.actual_quantity)
#             print("outsourced_product.actual_quantity==>", outsourced_product.actual_quantity)
#         remaining += infill_pro.infill_quantity - pro_remaining
#     else:
#         print("USn")
#         infill_pro = Eps_infill_Details.objects.get(pk=pk)
#         remaining = infill_pro.infill_quantity
        
#     data = {
#         "remaining": remaining,
#     }
#     return data
@register.simple_tag
def outsource_item_remaning(pk):
    outsourced_products = Eps_Outsource_items.objects.filter(infill_product=pk)
    infill_obj = Eps_infill_Details.objects.get(pk=pk)
    remaining = 0
    pro_remaining = 0
    # infill_pro = 0

    if outsourced_products.exists():
        for outsourced_product in outsourced_products:
            pro_remaining += outsourced_product.actual_quantity
        remaining = infill_obj.infill_quantity - pro_remaining
    else:
        # infill_pro = Eps_infill_Details.objects.get(pk=pk)
        remaining = infill_obj.infill_quantity

    data = {
        "remaining": remaining,
    }
    return data



@register.simple_tag
def outsource_item_details(pk):
    outsourced_products = Eps_Outsource_items.objects.filter(infill_product=pk)
    infill_obj = Eps_infill_Details.objects.get(pk=pk)
    
    # if not outsourced_products:
    #     remaining = infill_obj.infill_quantity
    # else:
    remaining = 0
        
    outsource_qty = 0
    recvd_qty = 0
    recv_remaing = 0
    act_qty = 0
    
    for outsourced_product in outsourced_products:
        infill_pro = Eps_infill_Details.objects.get(pk=outsourced_product.infill_product.id)
        act_qty += outsourced_product.actual_quantity
        # remaining += infill_pro.infill_quantity - outsourced_product.actual_quantity
        outsource_qty += outsourced_product.actual_quantity
        recvd_qty += outsourced_product.received_quantity
        recv_remaing += outsourced_product.remaining_quantity
    remaining = infill_obj.infill_quantity - act_qty
    
    data = {
        "outsourced_products": outsourced_products,
        "remaining_qty": remaining,
        "outsource_qty": outsource_qty,
        "recvd_qty": recvd_qty,
        "recv_remaing": recv_remaing,
        
    }
    return data

@register.simple_tag
def outsource_batch_data(pk, spec):
    outsource_objs = Eps_Outsourced_Data.objects.filter(
        products__infill_product__infill__panel_specification=spec, 
        products__infill_product__main_product=pk
        ).distinct('batch_number')
        # ).distinct('outsource_number')
    
    
    
    return outsource_objs

@register.simple_tag
def outsource_recived_details(pk, spec):
    batch = Outsource_receive_recode.objects.filter(
        received_items__infill_product__infill__panel_specification=spec,
        received_items__infill_product__main_product=pk
    ).distinct('OS_delivery_number')
    
    return batch

@register.simple_tag
def outsourced_items(pk):
    return Outsource_receive_items.objects.filter(
        received_batch=pk
    )