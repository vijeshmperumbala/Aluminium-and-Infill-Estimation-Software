from django import template
from apps.accessories_master.models import Accessories
from apps.profiles.models import Profiles
# from apps.accessories_kit.models import AccessoriesKitItem
register = template.Library()


@register.simple_tag
def get_profile_data(profile_series, parts):
    """
    This function retrieves profile data from a database based on a given profile series and part.
    
    :param profile_series: This parameter is likely an identifier or reference to a specific series of
    profiles. It is used to filter the Profiles objects to only include those that belong to the
    specified series
    :param parts: It is a variable that represents the part number of a profile. It is used as a filter
    parameter to retrieve a specific profile from the database
    :return: a queryset of Profiles objects filtered by the profile_master_series_id and
    profile_master_part parameters passed to the function.
    """
    profile = Profiles.objects.filter(profile_master_series_id=profile_series, profile_master_part=parts)
    return profile