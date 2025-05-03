from django import template
from apps.projects.models import ProjectInvoicingProducts
register = template.Library()


@register.simple_tag
def invoiced_product_quantity(project, product, stage, invoice_num):
    """
    This function retrieves the quantity of a specific product invoiced for a project at a specific
    stage and invoice number.
    
    """
    invoice_date = ProjectInvoicingProducts.objects.get(project=project, product=product, invoicing_stage=stage, invoice=invoice_num)
    return {'quantity': invoice_date.quantity}