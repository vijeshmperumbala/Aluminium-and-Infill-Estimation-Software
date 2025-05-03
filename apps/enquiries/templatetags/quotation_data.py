from django import template

from apps.estimations.models import Quotations, Temp_Quotations
register = template.Library()

@register.simple_tag
def quotation_data(request, pk):
    """
    This function retrieves a quotation object based on the primary key of an estimation.
    
    :param request: The HTTP request object that contains information about the current request, such as
    the URL, headers, and data
    :param pk: pk is a parameter that represents the primary key of an object in the database. In this
    case, it is used to filter Quotations or Temp_Quotations objects based on their estimations field.
    The function returns the first object that matches the filter criteria
    :return: a quotation object. The quotation object is either retrieved from the Quotations model or
    the Temp_Quotations model based on the value of the 'pk' parameter passed to the function.
    """
    return (
        Quotations.objects.filter(estimations=pk).first()
        if '/Estimation/estimation_notes/' in request.path
        or '/Enquiries/enquiry_notes/' in request.path
        else Temp_Quotations.objects.filter(estimations=pk).first()
    )
    