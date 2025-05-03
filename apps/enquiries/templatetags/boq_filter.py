from django import template

from apps.estimations.models import EstimationMainProduct, Temp_EstimationMainProduct


register = template.Library()

@register.simple_tag
def boq_filter(request, pk, version):
    """
    The function filters and returns a queryset of EstimationMainProduct or Temp_EstimationMainProduct
    objects based on the provided parameters.
    
    :param request: The HTTP request object that contains information about the current request, such as
    the URL, headers, and data
    :param pk: pk is a parameter that represents the primary key of a specific object in the database.
    It is used to filter the queryset to retrieve only the objects that match the specified primary key
    :param version: The version parameter is a variable that is passed to the function as an argument.
    It is used to filter the queryset of EstimationMainProduct or Temp_EstimationMainProduct objects
    based on the version of the building estimation
    :return: The function `boq_filter` returns a queryset of `EstimationMainProduct` or
    `Temp_EstimationMainProduct` objects depending on the conditions specified in the function.
    """
    PATHS = [
        '/Enquiries/product_category_summary/',
        '/Estimation/estimation_list_by_boq_enquiry/',
        '/Enquiries/view_quotations/',
        '/Estimation/quotation_by_boq_enquiry/',
        '/Estimation/quotation_print_boq/',
        '/Estimation/quotation_print_by_customer_boq/',
        '/Estimation/export_csv_estimation_socpe_boq/',
        '/Estimation/export_category_summary_boq/',
        '/Estimation/building_price_print/',
    ]
    if pk:
        if any(path in request.path for path in PATHS):
            product = EstimationMainProduct.objects.select_related('boq_number').filter(boq_number__boq_number=pk, building__estimation=version, disabled=False).order_by('product_index')
        else:
            product = Temp_EstimationMainProduct.objects.select_related('boq_number').filter(boq_number__boq_number=pk, building__estimation=version, disabled=False).order_by('product_index')
        return product