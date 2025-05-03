from django import template
from django.db.models import Sum

from apps.projects.models import Eps_Products

register = template.Library()


@register.simple_tag
def eps_attachments_and_notes(eps):
    """
    This function retrieves the count and data of attachments and notes related to a given EPS object.
    
    """
    products = Eps_Products.objects.filter(eps_data=eps)
    attachments = products.filter(eps_product_attachment__isnull=False)
    notes = products.filter(eps_product_note__isnull=False)
    
    data = {
        'attachments_count': attachments.count(),
        'notes_count': notes.count(),
        'attachments': attachments,
        'notes': notes
    }
    return data
    