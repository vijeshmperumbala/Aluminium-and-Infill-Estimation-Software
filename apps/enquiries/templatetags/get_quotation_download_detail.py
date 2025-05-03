from django import template

from apps.estimations.models import EstimationMainProduct, QuotationDownloadHistory, Temp_EstimationMainProduct


register = template.Library()

@register.simple_tag
def get_quotation_download_detail(user, q_id):
    """
    This function retrieves the download history of a specific quotation for a given user.
    
    :param user: The user parameter is an object representing a customer who has downloaded a quotation
    :param q_id: q_id is a variable that represents the ID of a quotation. It is used as a parameter in
    the function get_quotation_download_detail() to retrieve the details of a quotation download history
    for a specific quotation
    :return: the last QuotationDownloadHistory object that matches the given quotation_customer (user)
    and quotation_data (q_id) parameters. If no matching object is found, it returns None.
    """
    try:
        data = QuotationDownloadHistory.objects.filter(quotation_customer=user, quotation_data=q_id).last()
    except Exception as e:
        data = None
    return data
