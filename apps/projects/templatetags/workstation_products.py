from django import template
from apps.projects.models import Workstation_Associated_Products_Data, Workstation_Data
register = template.Library()


@register.simple_tag
def workstation_products(pk, eps_product_id, complete=None):
    """
    This function retrieves workstation products based on the provided parameters.
    
    """
    return (
        Workstation_Data.objects.filter(
            workstation=pk, eps_product_id=eps_product_id, is_completed=False
        )
        if not complete
        else Workstation_Data.objects.filter(
            product__main_products__main_product__eps_data=pk,
            eps_product_id=eps_product_id,
            is_completed=True,
        )
    )


@register.simple_tag
def get_workstation_associated_products(pk, eps_product_id, main_product, complete=None):
    """
    This function retrieves workstation associated products based on certain criteria.
    """
    return (
        Workstation_Associated_Products_Data.objects.filter(
            workstation=pk, eps_product_id=eps_product_id, is_completed=False
        )
        if not complete
        else Workstation_Associated_Products_Data.objects.filter(
            product__main_product__main_product__eps_data=pk,
            eps_product_id=eps_product_id,
            is_completed=True,
        )
    )