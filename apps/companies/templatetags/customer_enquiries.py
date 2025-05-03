from django import template
from apps.customers.models import Customers
from apps.enquiries.models import Enquiries
from django.db.models import Q

from apps.estimations.models import EstimationMainProduct, Temp_EstimationMainProduct


register = template.Library()

@register.simple_tag
def customer_enquiries(pk):
    customer = Customers.objects.get(pk=pk)
    enquiries_obj = Enquiries.objects.filter(Q(main_customer=customer) | Q(customers=customer)).distinct('id')
    return enquiries_obj.count()
    
    