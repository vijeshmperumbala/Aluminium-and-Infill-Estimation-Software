from django import template
from apps.projects.models import ProjectInvoicingProducts
register = template.Library()


@register.simple_tag
def side_page_invoice_details(project, product, stage):
    """
    This function retrieves invoice details for a specific project, product, and invoicing stage.
    
    """
    invoice_date = ProjectInvoicingProducts.objects.filter(project=project, product=product, invoicing_stage=stage)
    return {'invoice_data': invoice_date}