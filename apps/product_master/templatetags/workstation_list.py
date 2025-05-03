import re
from django import template
from apps.Workstations.models import Workstations

from apps.product_master.models import Product_WorkStations
from apps.projects.models import Eps_Product_Details, Workstation_Associated_Products_Data, Workstation_Data
register = template.Library()


@register.simple_tag
def workstation_list(pk):
    """
    This function returns a list of workstations associated with a given product ID.
    
    :param pk: pk stands for "primary key" and is typically used as a unique identifier for a specific
    record in a database table. In this case, it is being used as a parameter for the function
    `workstation_list` to filter the `Product_WorkStations` table by the `product` field that
    :return: The function `workstation_list` returns a queryset of `Product_WorkStations` objects that
    are filtered by the `product` field matching the `pk` parameter, and ordered by their `id` field.
    """
    workstations = Product_WorkStations.objects.filter(product=pk).order_by('id')
    return workstations

@register.simple_tag
def workstation_with_quantity(pk, eps_id, p_type):
    """
    This function retrieves the quantity of workstations associated with a product and its completion
    status.
    """
    workstations = Workstations.objects.all().order_by('id')
    if p_type == 'main':
        product_workstations = Workstation_Data.objects.filter(
            eps_product_id__eps_product__product=pk, 
            eps_product_id__eps_data=eps_id,
            # qaqc_received_quantity=0,
        ).order_by('id')
    else:
        product_workstations = None

    if p_type == 'associated':
        eps_product_details = Eps_Product_Details.objects.get(pk=pk)
        
        product_workstations_associated = Workstation_Associated_Products_Data.objects.filter(
            eps_product_id=eps_product_details.main_product, 
            eps_product_id__eps_data=eps_id,
            # product__main_product=eps_product_details
        ).order_by('id')
    else:
        product_workstations_associated = None
    
    w_dict = {}
    completed = 0
    qaqc_completed = 0
    
    if p_type == 'main':
        for workstation in workstations:
            if workstation not in w_dict:
                w_dict[workstation] = {'quantity': '-', 'product': [], 'remaining_quantity': float(0), 'is_completed': None, 'completed': None, 'qaqc_completed': None}

            quantity = 0
            quantity_2 = 0
            remaining_quantity = 0
            
            if product_workstations:
                for product in product_workstations:
                    if workstation == product.workstation:
                        if not product.is_completed:
                            quantity += product.received_quantity
                            # quantity += product.eps_product_id.quantity
                            remaining_quantity += float(product.received_quantity)
                            w_dict[workstation]['quantity'] = quantity
                            w_dict[workstation]['product'] = product  
                            w_dict[workstation]['remaining_quantity'] = product.remaining_quantity #remaining_quantity
                            w_dict[workstation]['completed_quantity'] = float(product.completed_quantity)
                        else:
                            if not product.qaqc_received_quantity == 0:
                                quantity_2 += product.received_quantity
                                w_dict[workstation]['completed_quantity'] = quantity_2

                        if product.is_completed:
                            completed += product.completed_quantity

                        if product.is_qaqc_completed:
                            qaqc_completed += product.qaqc_completed_quantity

        w_dict['completed'] = completed
        w_dict['qaqc_completed'] = qaqc_completed
        return w_dict
    else:
        # if p_type == 'associated':
        #     for workstation in workstations:
        #         if product_workstations_associated:
        #             if workstation not in w_dict:
        #                 w_dict[workstation] = {'quantity': '-', 'product': [], 'remaining_quantity': float(0), 'is_completed': None} 
                        
        #             quantity = 0
        #             quantity_2 = 0
        #             remaining_quantity = 0
        #             for associated_product in product_workstations_associated:
        #                 if workstation == associated_product.workstation:
        #                     if w_dict[workstation]['product'] != associated_product:
        #                         if not associated_product.is_completed:
        #                             quantity = associated_product.received_quantity
        #                         else:
        #                             if not associated_product.qaqc_received_quantity == 0:
        #                                 quantity = associated_product.received_quantity
        #                         w_dict[workstation]['quantity'] = quantity
        #                         w_dict[workstation]['product'] = associated_product  # Update the associated product
        #                         w_dict[workstation]['remaining_quantity'] = float(associated_product.remaining_quantity)
        #                         w_dict[workstation]['completed_quantity'] = float(associated_product.completed_quantity)
        #                         if associated_product.is_completed:
        #                             completed = associated_product.completed_quantity
                                    
        #                         if associated_product.is_qaqc_completed:
        #                             qaqc_completed = associated_product.qaqc_completed_quantity
        #                     else:
        #                         if not associated_product.is_completed:
        #                             quantity = associated_product.received_quantity
        #                         else:
        #                             if not associated_product.qaqc_received_quantity == 0:
        #                                 quantity += associated_product.received_quantity
                                    
        #                             w_dict[workstation]['quantity'] = quantity
        #                             w_dict[workstation]['product'] = associated_product 
        #                             w_dict[workstation]['remaining_quantity'] = float(associated_product.remaining_quantity)
        #                             w_dict[workstation]['completed_quantity'] = float(associated_product.completed_quantity)
        #                             if associated_product.is_completed:
        #                                 completed = associated_product.completed_quantity
                                        
        #                             if associated_product.is_qaqc_completed:
        #                                 qaqc_completed = associated_product.qaqc_completed_quantity
                                
        #     w_dict['completed'] = completed
        #     w_dict['qaqc_completed'] = qaqc_completed
            
        #     return w_dict
        
        if p_type == 'associated':
            completed = 0
            qaqc_completed = 0
            
            for workstation in workstations:
                if product_workstations_associated:
                    if workstation not in w_dict:
                        w_dict[workstation] = {
                            'quantity': '-', 
                            'product': None, 
                            'remaining_quantity': 0.0, 
                            'completed_quantity': 0.0,
                            'is_completed': None
                        }

                    for associated_product in product_workstations_associated:
                        if workstation == associated_product.workstation:
                            
                            if w_dict[workstation]['product'] != associated_product:
                                if not associated_product.is_completed or associated_product.qaqc_received_quantity != 0:
                                    quantity = associated_product.received_quantity
                                    remaining_quantity = associated_product.remaining_quantity
                                    completed_quantity = associated_product.completed_quantity
                                else:
                                    quantity = 0
                                    remaining_quantity = 0
                                    completed_quantity = 0

                                w_dict[workstation].update({
                                    'quantity': quantity,
                                    'product': associated_product,
                                    'remaining_quantity': float(remaining_quantity),
                                    'completed_quantity': float(completed_quantity),
                                })

                                if associated_product.is_completed:
                                    completed = associated_product.completed_quantity

                                if associated_product.is_qaqc_completed:
                                    qaqc_completed = associated_product.qaqc_completed_quantity
                            else:
                                
                                quantity += associated_product.received_quantity
                                remaining_quantity += associated_product.remaining_quantity
                                completed_quantity += associated_product.completed_quantity

                                w_dict[workstation].update({
                                    'quantity': quantity,
                                    'product': associated_product,
                                    'remaining_quantity': float(remaining_quantity),
                                    'completed_quantity': float(completed_quantity),
                                })

                                if associated_product.is_completed:
                                    completed = associated_product.completed_quantity

                                if associated_product.is_qaqc_completed:
                                    qaqc_completed = associated_product.qaqc_completed_quantity

            w_dict['completed'] = completed
            w_dict['qaqc_completed'] = qaqc_completed

            return w_dict

            

                    

   
