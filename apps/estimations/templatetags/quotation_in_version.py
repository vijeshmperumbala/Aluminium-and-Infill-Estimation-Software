from django import template

from apps.estimations.models import Quotation_Notes, Quotations, Temp_Quotation_Notes, Temp_Quotations
register = template.Library()


@register.simple_tag
def quotation_in_version(request, pk, flag=None):
    """
    This function retrieves a quotation and its notes based on a given estimation ID and a flag
    indicating whether to use temporary or permanent quotations.
    
    :param request: The HTTP request object that contains metadata about the request being made
    :param pk: pk is a parameter that represents the primary key of an object in the database. In this
    case, it is used to filter Quotations or Temp_Quotations objects based on their estimations field
    :param flag: The flag parameter is an optional parameter that is used to determine whether to
    retrieve data from the Quotations model or the Temp_Quotations model. If flag is not provided or is
    None, data will be retrieved from the Quotations model. If flag is provided, data will be retrieved
    :return: a dictionary object named `context` which contains two keys: `quotation` and `notes`. The
    values of these keys are the `quotation` and `notes` objects retrieved from the database based on
    the input parameters `pk` and `flag`. If the `flag` parameter is not provided or is `None`, the
    function retrieves the `Quotations` and
    """
    if not flag:
        try:
            quotation = Quotations.objects.filter(estimations=pk)
            notes = Quotation_Notes.objects.get(quotation=quotation.last().id)
        except:
            quotation = None
            notes = None
    else:
        try:
            quotation = Temp_Quotations.objects.filter(estimations=pk)
            notes = Temp_Quotation_Notes.objects.get(quotation=quotation.last().id)
        except:
            quotation = None
            notes = None
        
    context = {
        'quotation': quotation,
        'notes': notes
    }
    return context
