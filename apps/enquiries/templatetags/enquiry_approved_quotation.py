from django import template
from django.db.models import Q
from apps.enquiries.models import Estimations

from apps.estimations.models import Quotations
register = template.Library()

@register.simple_tag
def enquiry_approved_quotation(pk):
    """
    This function retrieves an approved quotation and its corresponding estimation based on a given
    primary key.
    
    :param pk: The primary key (pk) is a unique identifier for a specific record in the database. In
    this case, it is used to retrieve an estimation and quotation related to a specific enquiry
    :return: a dictionary with two keys: "estimation" and "quotation". The values of these keys are
    either the Estimations and Quotations objects that match the given conditions, or None if no
    matching objects are found.
    """
    try:
        
        estimation = Estimations.objects.filter(Q(enquiry=pk), Q(version__status=12) | Q(version__status=13)).last()
        quotation = Quotations.objects.get(estimations=estimation)
    except Exception as e:
        estimation = None
        quotation = None
    return {"estimation": estimation, "quotation": quotation}