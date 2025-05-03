from django import template
from apps.enquiries.models import EnquirySpecifications, Temp_EnquirySpecifications
from apps.estimations.models import MainProductGlass

from apps.pricing_master.models import Sealant_kit

register = template.Library()


@register.simple_tag
def get_sealant_kit(pk, sealant_type):
    """
    This function retrieves data for a specific sealant kit based on its primary key and sealant type.
    
    :param pk: The primary key (unique identifier) of a Sealant_kit object in the database
    :param sealant_type: The `sealant_type` parameter is a string that specifies the type of sealant kit
    that is being requested. It is used to filter the `Sealant_kit` objects and retrieve the one with
    the matching `sealant_type`
    :return: the data of a sealant kit with a specific primary key and sealant type.
    """
    kit_data = Sealant_kit.objects.get(pk=pk, sealant_type=sealant_type)
    return kit_data


@register.simple_tag
def get_infill_specs(request, pk, panel_spec):
    PATHS = [
        '/Estimation/consolidate_price_update/',
    ]
    if any(path in request.path for path in PATHS):
        print("S")
        print("estimation==>", pk)
        print("panel_specification==>", panel_spec)
        print("S")
        specs_objs = EnquirySpecifications.objects.filter(estimation=pk, panel_specification=panel_spec)
    else:
        print("sS")
        specs_objs = Temp_EnquirySpecifications.objects.filter(estimation=pk, panel_specification=panel_spec)
    
    return specs_objs