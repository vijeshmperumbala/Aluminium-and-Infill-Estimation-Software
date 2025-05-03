from django import template
from django.db.models import Sum
from apps.estimations.models import EstimationMainProduct, MainProductAluminium
from apps.projects.models import Eps_Associated_sub_Products, Eps_Product_Details, ProjectDeliveryQuantity, ProjectInstalledQuantity, ProjectInvoicingProducts, Workstation_Associated_Products_Data
register = template.Library()


@register.simple_tag
def eps_associated_data(pk):
    """
    This function retrieves associated sub-products data for a given main product primary key.
    
    """
    try:
        data = Eps_Associated_sub_Products.objects.get(main_product=pk)
    except Exception:
        data = None
    return data


@register.simple_tag
def eps_associated_products(pk):
    """
    This function retrieves data on associated sub-products of a main product and calculates the total
    received quantity.
    
    """
    print("pk==>", pk)
    print("")
    print("")
    try:
        completed_flag = True
        data = Eps_Product_Details.objects.get(pk=pk)
        data2 = Eps_Associated_sub_Products.objects.filter(main_product__main_product=data.main_product.id)
        # for product in data:
        print("data==>", data)
        print("data.main_product.id==>", data.main_product.id)
        try:
            # completed = Workstation_Associated_Products_Data.objects.get(eps_product_id=data.main_product.id, product__main_product=data, is_completed=True)
            completed = Workstation_Associated_Products_Data.objects.get(eps_product_id=data.main_product.id, product__main_product=data, is_completed=True)
        except Exception as ee:
            print("EXCE==>")
            completed = Workstation_Associated_Products_Data.objects.filter(eps_product_id=data.main_product.id, product__main_product=data, is_completed=False).first()
            completed_flag = None
            print('E==>', ee)
            
    except Exception as e:
        print('EE==>', e)
        data = None
        data2 = None
    if data2:
        received_quantity = sum(item.received_quantity for item in data2)
    else:
        received_quantity = None
    
    return {
        'product': completed.product if completed else None,
        'received_quantity': received_quantity,
        'completed': completed,
        'completed_flag': completed_flag or None,
    }
    