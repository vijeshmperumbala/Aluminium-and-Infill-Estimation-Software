
from django import template

from apps.accessories_kit.models import AccessoriesKit
from apps.profiles.models import Profiles

register = template.Library()


@register.simple_tag
def aluminium_profile_data(pk):
    return Profiles.objects.filter(
        profile_master_series__profile_master_type__profile_master_type=pk
    ).order_by(
        'profile_master_series__profile_master_type__profile_master_category',
        'profile_master_series__profile_master_type__profile_master_brand',
        'profile_master_series__profile_master_series',
    )


@register.simple_tag
def accessory_product_from_category(pk):
    
    return AccessoriesKit.objects.filter(product__product_category=pk)