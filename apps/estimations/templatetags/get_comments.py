from django import template

from apps.estimations.models import ProductComments, Temp_ProductComments

register = template.Library()


@register.simple_tag
def get_comments(request, product_id):
    """
    This function retrieves comments for a product based on its ID, using either the ProductComments or
    Temp_ProductComments model depending on the request path.
    
    """
    PATHS = [
        '/Estimation/estimation_list_enquiry/',
        '/Enquiries/product_category_summary/',
        '/Estimation/view_side_summary/',
    ]
    
    if any(path in request.path for path in PATHS):
        ProductCommentsModel = ProductComments
    else:
        ProductCommentsModel = Temp_ProductComments
        
    comment = ProductCommentsModel.objects.select_related('product').filter(product=product_id).order_by('id')
        
    return comment

