from django import template
from django.db.models import Sum
from apps.estimations.models import (
        EstimationMainProduct, 
)
from apps.projects.models import (
        Eps_Products, 
        ProjectContractItems, 
        ProjectDeliveryQuantity, 
        ProjectInstalledQuantity,
        SalesOrderItems, 
        Workstation_Data,
)
register = template.Library()


@register.simple_tag
def project_qunatity_check(project, product, type):
    """
    The function takes in a project, product, and type and returns the delivered or installed quantity
    of the product for the project, or 0 if there is no data.
    """
    
    if type == 'delivered_quantity':
        qunatity = ProjectDeliveryQuantity.objects.filter(project=project, product=product).aggregate(quantity = Sum('delivered_qunatity'))
        data = qunatity['quantity']
        
    elif type == 'installed_quantity':
        qunatity = ProjectInstalledQuantity.objects.filter(project=project, product=product).aggregate(quantity = Sum('installed_qunatity'))
        data = qunatity['quantity']
    else:
        data = 0
        
    if not data:
            data = 0
    return data


@register.simple_tag
def get_eps_quantity(pk, project, types=None):
    """
        This function calculates the EPS quantity, delivered quantity, and remaining EPS quantity for a
        given project and project item.
    """
    if not types:
        project_item = ProjectContractItems.objects.get(pk=pk)
        eps_product = Eps_Products.objects.filter(eps_product=project_item, eps_data__project=project)
        estimation_product = SalesOrderItems.objects.get(pk=project_item.product.id)
        # estimation_product = EstimationMainProduct.objects.get(pk=project_item.product.id)
    else:
        try:
            project_item = ProjectContractItems.objects.get(product=pk)
        except Exception:
            project_item = None
            
        eps_product = Eps_Products.objects.filter(eps_product__product=pk, eps_data__project=project)
        estimation_product = SalesOrderItems.objects.get(pk=pk)
        # estimation_product = EstimationMainProduct.objects.get(pk=pk)
        
    wd_data = Workstation_Data.objects.filter(eps_product_id__in=[item.id for item in eps_product])
    # estimation_alum = MainProductAluminium.objects.get(estimation_product=estimation_product.id)

    eps_quantity = 0
    delivered_quantity = 0
    auth_remaining_qty = 0
    
    if estimation_product.category.is_curtain_wall:
        estim_qty = estimation_product.quantity
        # estim_qty = estimation_product.area

        for wd_product in wd_data:
            if wd_product.is_delivered:
                delivered_quantity = estimation_product.quantity
                # delivered_quantity = estimation_product.area
    else:
        estim_qty = estimation_product.quantity

        for wd_product in wd_data:
            delivered_quantity += wd_product.delivery_completed_quantity

    for product in eps_product:
        # if estimation_product.eps_uom
        if product.quantity:
            eps_quantity += product.quantity

    eps_remaining_qty = float(estim_qty)-float(eps_quantity)
    
    try:
        auth_remaining_qty = float(estim_qty)-float(project_item.authorised_quantity)
    except Exception:
        auth_remaining_qty = 0

    return {
        'pk': estimation_product.id,
        'eps_quantity': eps_quantity,
        'delivered_quantity': delivered_quantity,
        'eps_remaining_qty': eps_remaining_qty,
        'auth_remaining_qty': auth_remaining_qty,
        'eps_balance': float(project_item.eps_balance) if project_item else 0,
    }
    

@register.simple_tag
def scope_import_data(pk):
    return (
        EstimationMainProduct.objects.select_related('building')
        .filter(building=pk, convert_to_sales=False)
        .order_by('associated_key', 'id')
    )