from django import template

from apps.estimations.models import Quotations, Quote_Send_Detail
register = template.Library()

@register.simple_tag
def enquiry_quotation(pk):
    return (
        Quote_Send_Detail.objects.filter(quotation=quotations.id).last()
        if (
            quotations := Quotations.objects.filter(
                estimations__enquiry=pk
            ).last()
        )
        else None
    )
    