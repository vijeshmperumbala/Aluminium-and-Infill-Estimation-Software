from django import template
from django.db.models import Sum
from apps.estimations.models import (
        EstimationMainProduct, 
        MainProductAluminium,
)
from apps.projects.models import (
        ProjectDeliveryQuantity, 
        ProjectInstalledQuantity, 
        ProjectInvoicingProducts,
        SalesOrderItems,
)

register = template.Library()

@register.simple_tag
def product_quantity_details(project, product):
    """
    This function calculates various quantities and values related to a product in a project, including
    delivered and invoiced quantities, invoiced value, and remaining quantities.
    
    """
    # products = MainProductAluminium.objects.get(estimation_product=product)
    main_product = SalesOrderItems.objects.get(pk=product)
    # main_product = EstimationMainProduct.objects.get(pk=product)
    
    qunatity = ProjectDeliveryQuantity.objects.filter(project=project, product=product).aggregate(quantity = Sum('delivered_qunatity'))
    if qunatity['quantity'] is None:
        qunatity['quantity'] = 0.00
    
    delivery_invoiced_quantity = ProjectInvoicingProducts.objects.filter(project=project, product=product, invoicing_stage__stage=1).aggregate(product_quantity = Sum('quantity'))
    if delivery_invoiced_quantity["product_quantity"] is None:
        delivery_invoiced_quantity["product_quantity"] = 0.00
        
    stage_1_invoiced_quantity = ProjectInvoicingProducts.objects.filter(project=project, product=product, invoicing_stage__stage=2).aggregate(product_quantity = Sum('quantity'))
    if stage_1_invoiced_quantity["product_quantity"] is None:
        stage_1_invoiced_quantity["product_quantity"] = 0.00
        
    stage_2_invoiced_quantity = ProjectInvoicingProducts.objects.filter(project=project, product=product, invoicing_stage__stage=3).aggregate(product_quantity = Sum('quantity'))
    if stage_2_invoiced_quantity["product_quantity"] is None:
        stage_2_invoiced_quantity["product_quantity"] = 0.00
        
    stage_3_invoiced_quantity = ProjectInvoicingProducts.objects.filter(project=project, product=product, invoicing_stage__stage=4).aggregate(product_quantity = Sum('quantity'))
    if stage_3_invoiced_quantity["product_quantity"] is None:
        stage_3_invoiced_quantity["product_quantity"] = 0.00
        
    invoiced_value = ProjectInvoicingProducts.objects.filter(project=project, product=product).aggregate(product_value = Sum('total'))
    if invoiced_value['product_value'] is None:
        invoiced_value['product_value'] = 0.00
        
    delivered_not_invoiced = round(float(qunatity['quantity']) - float(delivery_invoiced_quantity["product_quantity"]), 2)
    
    delivery_balance_quantity = float(delivery_invoiced_quantity["product_quantity"]) - float(stage_1_invoiced_quantity["product_quantity"])
    stage_1_balance_quantity = float(stage_1_invoiced_quantity["product_quantity"]) - float(stage_2_invoiced_quantity["product_quantity"])
    stage_2_balance_quantity = float(stage_2_invoiced_quantity["product_quantity"]) - float(stage_3_invoiced_quantity["product_quantity"])
    stage_3_balance_quantity = float(stage_3_invoiced_quantity["product_quantity"]) - float(stage_2_invoiced_quantity["product_quantity"])
   
    
    
    if main_product.category.invoice_in_quantity:
        balance_quantity = float(main_product.quantity) - (float(delivered_not_invoiced)+float(delivery_invoiced_quantity["product_quantity"]))
    else:
        balance_quantity = float(main_product.total_area) - (float(delivered_not_invoiced)+float(delivery_invoiced_quantity["product_quantity"]))
    data = {
        "delivered_not_invoiced": delivered_not_invoiced,
        "delivery_invoiced_quantity": delivery_invoiced_quantity["product_quantity"],
        "invoiced_value": invoiced_value["product_value"],
        "stage_1_invoiced_quantity": stage_1_invoiced_quantity["product_quantity"],
        "stage_2_invoiced_quantity": stage_2_invoiced_quantity["product_quantity"],
        "stage_3_invoiced_quantity": stage_3_invoiced_quantity["product_quantity"],
        "remaining_quantity": balance_quantity,
        
        "delivery_balance_quantity": delivery_balance_quantity,
        "stage_1_balance_quantity": stage_1_balance_quantity,
        "stage_2_balance_quantity": stage_2_balance_quantity,
        "stage_3_balance_quantity": stage_3_balance_quantity
    }
    return data

