from django import template

from apps.estimations.models import EstimationMainProduct, ProductCategoryRemarks, Quotation_Notes, Temp_EstimationMainProduct


register = template.Library()

@register.simple_tag
def get_acknoledgement_data(pk):
    """
    This function checks if all the acknowledgement fields in a queryset are True and returns a boolean
    value accordingly.
    
    :param pk: The parameter "pk" is likely an abbreviation for "primary key" and is likely used to
    identify a specific record or object in a database table. In this case, it is probably being used to
    retrieve data related to a specific enquiry
    :return: a boolean value indicating whether all the ProductCategoryRemarks objects related to a
    particular enquiry (identified by the primary key 'pk') have been acknowledged or not.
    """
    data_obj = ProductCategoryRemarks.objects.filter(product__building__estimation__enquiry=pk).order_by('id')
    ack = False
    counter = 0
    for data in data_obj:
        if data.acknowledgement:
            counter += 1
    if data_obj.count() == counter:
        ack = True
    return ack