from django import template

from apps.customers.models import Customers
from apps.enquiries.models import Enquiries, Estimations
register = template.Library()


@register.simple_tag
def customer_quotations(pk):
    customer_obj = Customers.objects.get(pk=pk)
    enquiries = Enquiries.objects.filter(customers=customer_obj)
    return enquiries


@register.simple_tag
def enquiry_versions(pk):
    versions = Estimations.objects.filter(enquiry=pk)
    return versions