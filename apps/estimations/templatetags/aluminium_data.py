
from django import template
from apps.estimations.models import MainProductAluminium, MainProductGlass, EstimationMainProduct, Temp_EstimationMainProduct, Temp_MainProductAluminium
register = template.Library()


PATHS = [
    '/Estimation/edit_estimation_pricing/',
    '/Estimation/estimation_pricing_summary/',
    '/Estimation/estimation_list_enquiry/',
    '/Estimation/edit_estimation_pricing/',
    '/Estimation/export_csv_estimation_socpe/',
    '/Estimation/export_csv_estimation_socpe_boq/',
    '/Estimation/export_category_summary/',
    '/Estimation/product_merge/',
    '/Estimation/building_wise_products/',
    '/Enquiries/product_category_summary/',
    '/Estimation/estimation_list_by_boq_enquiry/',
    '/Estimation/estimation_detail_summary/',
    '/Project/project_scop/',
    '/Project/project_budgeting/',
    '/Estimation/export_category_summary_building/',
    '/Estimation/export_category_summary_boq/',
    '/Estimation/product_merge_summary/',
    '/Project/project_accounts/',
    '/Project/create_project_invoice/',
    '/Project/view_invoice_normal/',
    '/Project/edit_project_invoice/',
    '/Project/create_project_wcr/',
    '/Project/view_wcr/',
    '/Project/project_contract_items/',
    '/Project/proccess_quotation/',
    '/Project/update_quotation_item/',
    '/Project/add_eps_item/',
    '/Project/create_eps/',
    '/Project/view_eps/',
    '/Project/eps_view_fabrications/',
    '/Project/eps_production_view/',
    '/Project/general_production_view/',
    '/Project/eps_outsource_view/',
    '/Project/eps_shopfloor_view/',
    '/Project/workstaions_view/',
    '/Project/qaqc_view/',
    '/Project/products_for_delivery_view/',
    '/Project/fabrication_details/',
    '/Project/fabrication_product_detail_view/',
    '/Project/production_product_detail_view/',
    '/Project/shopfloor_details/',
    '/Project/shopfloor_product_detail_view/',
    '/Project/qaqc_details/',
    '/Project/qaqc_product_detail_view/',
    '/Project/general_product_for_delivery_details/',
    '/Project/product_for_delivery_product_detail_view/',
    '/Project/workstation_projects/',
    '/Project/workstation_side_data/',
    '/Project/general_workstation_view',
    '/Project/view_eps_product/',
    '/Project/general_fabrications_view/',
    '/Project/general_shopfloor_view/',
    '/Project/shopfloor_filter/',
    '/Project/general_qaqc_view/',
    '/Project/inspection_list/',
    '/Project/inspection_view/',
    '/Project/os_recive/',
    '/Project/workstation_completed/',
    '/Project/workstation_projects_cmpld/',
    '/Project/workstation_side_data_cmpltd/',
    '/Project/outsource_print/',
    '/Project/eps_print/',
    '/Estimation/merge_summary_update_spec/',
    '/Estimation/consolidate_aluminium_update/',
    '/Estimation/category_wise_product/',
    '/Enquiries/create_quotation_base/',
    '/Enquiries/edit_quotation/',
    '/Enquiries/view_quotations/',
    '/Estimation/quotation_print/',
    '/Estimation/quotation_print_by_customer/',
    '/Estimation/quotation_print_by_customer_boq/',
    '/Estimation/quotation_print_view/',
    '/Estimation/sync_quotation/',
    '/Estimation/building_summary/',
    '/Project/project_eps/',
    '/Project/edit_project_wcr/',
    '/Enquiries/get_customer_data/',
    '/Estimation/sync_quotation/',
    '/Estimation/scope_view/',
    '/Estimation/scope_with_material/',
    '/Estimation/quotation_by_boq_enquiry/',
    '/Estimation/estimation_product_delete/',
    '/Estimation/submit_estimation/',
    '/Enquiries/new_quotaion_customers/',
    '/Estimation/estimation_quotations_list/',
    '/Estimation/quotation_by_boq_enquiry/',
    '/Project/create_glass_eps/',
    '/Project/eps_collaps_data/',
    '/Project/glass_eps_collaps_data/',
    '/Project/eps_side_details/',
    '/Project/import_from_scope/',
    '/Project/completed_inspection_list/',
    '/Estimation/quotation_unit_price/',
    '/Estimation/disable_products/',
    '/Estimation/disabled_scope_view/',
    '/Estimation/quotation_excel_import_view/',
]

@register.simple_tag
def aluminium_data(request, pk):
    """
    This function returns either a MainProductAluminium or a Temp_MainProductAluminium object based on
    the request path and a given primary key.
    
    :param request: The request object represents the HTTP request that the user has made to the server.
    It contains information such as the URL, headers, and any data that was sent with the request
    :param pk: pk stands for "primary key". It is a unique identifier for a specific record in a
    database table. In this code snippet, it is used to retrieve a specific record from either the
    MainProductAluminium or Temp_MainProductAluminium table, depending on the request path
    :return: The function `aluminium_data` returns either a `MainProductAluminium` object or a
    `Temp_MainProductAluminium` object based on the value of `pk` and whether any of the paths in
    `PATHS` are present in the `request.path`.
    """
    
    if any(path in request.path for path in PATHS):
        return MainProductAluminium.objects.get(estimation_product=pk)
    else:
        return Temp_MainProductAluminium.objects.get(estimation_product=pk)
    

def associated_data(pk):
    """
    This function returns the name of the associated product for a given primary key.
    
    :param pk: The parameter "pk" is an integer value that represents the primary key of a main product
    in the database
    :return: the name of the associated product for a given primary key (pk) if it exists, otherwise it
    returns None.
    """
    associated_product = EstimationMainProduct.objects.filter(main_product=pk, product_type=2, disabled=False).last()
    if associated_product:
        if associated_product.product:
            if associated_product.is_display_data:
                name = associated_product.display_product_name
            elif associated_product.product.quotation_product_name:
                name = associated_product.product.quotation_product_name
            else:
                name = associated_product.product.product_name
        else:
            if associated_product.is_display_data:
                name = associated_product.display_product_name
            elif associated_product.panel_product.quotation_product_name:
                name = associated_product.panel_product.quotation_product_name
            else:
                name = associated_product.panel_product.product_name
        return name
    else:
        return None

def temp_associated_data(pk):
    """
    This function retrieves the name of a product associated with a given primary key.
    
    :param pk: The parameter "pk" is an integer value that represents the primary key of a
    Temp_EstimationMainProduct object. This function retrieves the associated data of the
    Temp_EstimationMainProduct object with the given primary key
    :return: the name of the associated product for a given primary key (pk) if it exists, otherwise it
    returns None.
    """
    associated_product = Temp_EstimationMainProduct.objects.filter(main_product=pk, product_type=2, disabled=False).last()
    if associated_product:
        if associated_product.product:
            if associated_product.is_display_data:
                name = associated_product.display_product_name
            elif associated_product.product.quotation_product_name:
                name = associated_product.product.quotation_product_name
            else:
                name = associated_product.product.product_name
        else:
            if associated_product.is_display_data:
                name = associated_product.display_product_name
            elif associated_product.panel_product.quotation_product_name:
                name = associated_product.panel_product.quotation_product_name
            else:
                name = associated_product.panel_product.product_name
        return name
    else:
        return None
            

@register.simple_tag
def display_product_name(request, pk):
    """
    This function returns the name of a product based on certain conditions and parameters.
    
    :param request: The HTTP request object
    :param pk: The primary key of the EstimationMainProduct or Temp_EstimationMainProduct object that we
    want to display the name of
    :return: the name of a product based on certain conditions and inputs.
    """
    if any(path in request.path for path in PATHS):
        EstimationMainProductModel = EstimationMainProduct
        Function = associated_data
    else:
        Function = temp_associated_data
        EstimationMainProductModel = Temp_EstimationMainProduct
        
    product = EstimationMainProductModel.objects.get(pk=pk)
    if product.product:
        if product.have_merge:
            associated_product = Function(product.id)
            if product.product_type == 1 and product.is_display_data:
                name = str(product.display_product_name)+' with '+str(associated_product)
            elif product.product_type == 1 and not product.is_display_data:
                if product.product.quotation_product_name:
                    name = str(product.product.quotation_product_name)+' with '+str(associated_product)
                else:
                    name = str(product.product.product_name)+' with '+str(associated_product)
            elif not product.product_type == 1 and not product.is_display_data:
                if product.product.quotation_product_name:
                    name = str(product.product.quotation_product_name)
                else:
                    name = str(product.product.product_name)
            else:
                name = '----'
        else:
            if product.is_display_data:
                name = product.display_product_name
            elif product.product.quotation_product_name:
                name = product.product.quotation_product_name
            else:
                name = product.product.product_name
    else:
        if product.have_merge:
            associated_product = Function(product.id)
            if product.product_type == 1 and product.is_display_data:
                name = str(product.display_product_name)+' with '+str(associated_product)
            elif product.product_type == 1 and not product.is_display_data:
                if product.panel_product.quotation_product_name:
                    name = str(product.panel_product.quotation_product_name)+' with '+str(associated_product)
                else:
                    name = str(product.panel_product.product_name)+' with '+str(associated_product)
                    
            elif not product.product_type == 1 and not product.is_display_data:
                if product.panel_product.quotation_product_name:
                    name = str(product.panel_product.quotation_product_name)
                else:
                    name = str(product.panel_product.product_name)
            else:
                name = '----'
        else:
            
            if product.is_display_data:
                name = product.display_product_name
            elif product.panel_product.quotation_product_name:
                name = product.panel_product.quotation_product_name
            else:
                name = product.panel_product.product_name
    # else:
    #     product = Temp_EstimationMainProduct.objects.get(pk=pk)
    #     if product.product:
    #         if product.have_merge:
    #             associated_product = temp_associated_data(product.id)
    #             if product.product_type == 1 and product.is_display_data:
    #                 name = str(product.display_product_name)+' with '+str(associated_product)
    #             elif product.product_type == 1 and not product.is_display_data:
    #                 if product.product.quotation_product_name:
    #                     name = str(product.product.quotation_product_name)+' with '+str(associated_product)
    #                 else:
    #                     name = str(product.product.product_name)+' with '+str(associated_product)
    #             elif not product.product_type == 1 and not product.is_display_data:
    #                 if product.product.quotation_product_name:
    #                     name = str(product.product.quotation_product_name)
    #                 else:
    #                     name = str(product.product.product_name)
    #             else:
    #                 name = '----'
    #         else:
    #             if product.is_display_data:
    #                 name = product.display_product_name
    #             elif product.product.quotation_product_name:
    #                 name = product.product.quotation_product_name
    #             else:
    #                 name = product.product.product_name
    #     else:
            
    #         if product.have_merge:
    #             associated_product = temp_associated_data(product.id)
    #             if product.product_type == 1 and product.is_display_data:
    #                 name = str(product.display_product_name)+' with '+str(associated_product)
    #             elif product.product_type == 1 and not product.is_display_data:
    #                 if product.panel_product.quotation_product_name:
    #                     name = str(product.panel_product.quotation_product_name)+' with '+str(associated_product)
    #                 else:
    #                     name = str(product.panel_product.product_name)+' with '+str(associated_product)
                        
    #             elif not product.product_type == 1 and not product.is_display_data:
    #                 if product.panel_product.quotation_product_name:
    #                     name = str(product.panel_product.quotation_product_name)
    #                 else:
    #                     name = str(product.panel_product.product_name)
    #             else:
    #                 name = '----'
    #         else:
    #             if product.is_display_data:
    #                 name = product.display_product_name
    #             elif product.panel_product.quotation_product_name:
    #                 name = product.panel_product.quotation_product_name
    #             else:
    #                 name = product.panel_product.product_name
    return name 




            
    