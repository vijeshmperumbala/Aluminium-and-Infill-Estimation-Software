from django import template
from apps.enquiries.models import Estimations
from apps.estimations.models import EstimationVersions, Quotations

register = template.Library()


@register.simple_tag
def get_submited_version(pk):
    """
    This function retrieves the ID of the latest submitted version of an estimation for a given enquiry.
    
    :param pk: The primary key of an Enquiry object
    :return: either the ID of the estimation with a version status of 3, or 0 if there are no
    estimations with a version status of 3 or if an exception occurs.
    """
    try:
        estimations = Estimations.objects.select_related('enquiry').filter(enquiry=pk).order_by('id')
        for estimate in estimations:
            if estimate.version.status == 3:
                return estimate.id
            else:
                return 0
    except Exception as e:
        return 0
