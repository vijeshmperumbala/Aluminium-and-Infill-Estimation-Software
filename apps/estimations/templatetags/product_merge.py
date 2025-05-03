from django import template
from django.db.models import Q, Sum
from django.db.models.query import QuerySet
from apps.enquiries.models import EnquirySpecifications, Temp_EnquirySpecifications
from apps.estimations.models import MainProductAluminium, MainProductGlass, MainProductAddonCost, EstimationMainProduct, MainProductSilicon \
    , MainProductAccessories
from django.db.models import Count 

register = template.Library()


@register.simple_tag
def product_merge(request, version):
    """
    The function retrieves distinct enquiry specifications based on the given version and returns them
    as a dictionary.
    
    :param request: The HTTP request object received by the view function
    :param version: The version parameter is a variable that is passed as an argument to the
    product_merge function. It is used to filter the EnquirySpecifications or Temp_EnquirySpecifications
    objects based on the estimation version
    :return: a dictionary named "data" which contains a key "categorys" with a value of a queryset of
    EnquirySpecifications or Temp_EnquirySpecifications objects filtered by the "version" parameter and
    distinct on the fields "identifier", "categories", "aluminium_products", and "panel_specification".
    """
    PATHS = [
        '/Estimation/product_merge_summary/',
        '/Estimation/merge_summary_print/',
        '/Enquiries/product_category_summary/',
        '/Estimation/merge_summary_print_2/',
    ]
    
    if any(path in request.path for path in PATHS):
        specification_obj = EnquirySpecifications.objects.filter(estimation=version).distinct(
                                        'identifier', 
                                        'categories', 
                                        'aluminium_products', 
                                        'panel_specification'
                                    )
    else:
        specification_obj = Temp_EnquirySpecifications.objects.filter(estimation=version).distinct(
                                        'identifier', 
                                        'categories', 
                                        'aluminium_products', 
                                        'panel_specification'
                                    )
    data = {
        "categorys": specification_obj
    }
    return data

