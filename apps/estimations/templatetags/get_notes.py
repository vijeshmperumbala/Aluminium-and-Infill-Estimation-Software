from django import template

from apps.estimations.models import ProductCategoryRemarks, ProductComments, Temp_ProductComments

register = template.Library()


@register.simple_tag

# def get_notes(request, product_id):
#     comment_model = ProductComments if '/Estimation/estimation_list_enquiry/' in request.path or '/Enquiries/product_category_summary/' in request.path or '/Estimation/view_side_summary/' in request.path else Temp_ProductComments
#     comment = comment_model.objects.select_related('product').filter(product=product_id).order_by('id')
#     notes = ProductCategoryRemarks.objects.select_related('product').filter(product=product_id).order_by('id')

#     acknowledged = all(note.acknowledgement for note in notes)
#     return {'notes': notes, 'comment': comment, 'acknowledged': acknowledged}


def get_notes(request, product_id):
    """
    This function retrieves notes and comments related to a product and checks if all notes have been
    acknowledged.
    
    :param request: The HTTP request object that contains information about the current request, such as
    the path, headers, and user information
    :param product_id: The ID of the product for which the notes and comments are being retrieved
    :return: A dictionary containing the notes, comments, and a boolean value indicating whether all
    notes have been acknowledged or not.
    """
    PATHS = [
        '/Estimation/estimation_list_enquiry/',
        '/Enquiries/product_category_summary/',
        '/Estimation/view_side_summary/',
    ]
    
    if any(path in request.path for path in PATHS):
        comment_model = ProductComments
    else:
        comment_model = Temp_ProductComments

    comment = comment_model.objects.select_related('product').filter(product=product_id).order_by('id')
    notes = ProductCategoryRemarks.objects.select_related('product').filter(product=product_id).order_by('id')

    acknowledged = all(note.acknowledgement for note in notes)

    return {'notes': notes, 'comment': comment, 'acknowledged': acknowledged}

