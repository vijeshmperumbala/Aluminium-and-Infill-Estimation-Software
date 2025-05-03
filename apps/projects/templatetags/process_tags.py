from django import template

from apps.projects.models import (
        Eps_Outsource_items, 
        Eps_Products, 
        Eps_infill_Details, 
        Eps_main,
)


register = template.Library()


@register.simple_tag
def schedule_eps_tag(pk):
    eps_obj = Eps_main.objects.get(pk=pk)
    # products_obj = Eps_Products.objects.filter(eps_data=eps_obj)
    outsource_objs = Eps_infill_Details.objects.filter(eps_ref=eps_obj)
    # outsource_objs = Eps_Outsource_items.objects.filter(infill_product__eps_ref=eps_obj)
    
    total_panel = 0
    rcvd_panel = 0
    remng_panel = 0
    total_area = 0
    
    for outsource_item in outsource_objs:
        total_area += outsource_item.infill_total_area
        
        total_panel += outsource_item.infill_quantity
        # total_panel += outsource_item.actual_quantity
        # rcvd_panel += outsource_item.received_quantity
        # remng_panel += outsource_item.remaining_quantity
    
    data = {
        "number_of_panels": total_panel,
        "total_area": total_area,
        "received_panels": rcvd_panel,
        "remaining_panels": remng_panel,
    }
    return data
    