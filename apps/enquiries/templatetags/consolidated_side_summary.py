from django import template
from apps.Categories.models import Category
from django.db.models.query import QuerySet
from apps.estimations.models import (
    EstimationBuildings,
    EstimationMainProduct,
    MainProductAluminium,
    Temp_EstimationMainProduct,
)

register = template.Library()
@register.simple_tag
def consolidated_side_summary(request, version_id):
    """
    The function returns a queryset of EstimationMainProduct or Temp_EstimationMainProduct objects
    filtered by version_id and grouped by category, depending on the request path.
    
    :param request: The HTTP request object that contains information about the current request, such as
    the path, method, headers, and body
    :param version_id: The version ID is a parameter that is passed to the function. It is used to
    filter the EstimationMainProduct or Temp_EstimationMainProduct objects based on the building's
    estimation version. The function returns a QuerySet of the filtered objects grouped by category
    :return: a QuerySet object that contains EstimationMainProduct or Temp_EstimationMainProduct objects
    filtered by the version_id parameter and grouped by category. The type of object returned depends on
    the path of the request.
    """
    PATHS = [
        '/Estimation/estimation_list_enquiry/',
        '/Estimation/estimation_list_by_boq_enquiry/',
        '/Estimation/summary_view_all/',
    ]
    if any(path in request.path for path in PATHS):
        products = EstimationMainProduct.objects.select_related('building').filter(building__estimation=version_id).query
        products.grouped_by = ['category']
        results = QuerySet(query=products, model=EstimationMainProduct)
    else:
        products = Temp_EstimationMainProduct.objects.select_related('building').filter(building__estimation=version_id).query
        products.grouped_by = ['category']
        results = QuerySet(query=products, model=Temp_EstimationMainProduct)
    return results