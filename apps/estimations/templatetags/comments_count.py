from django import template

# from apps.estimations.models import Temp_VersionHistoryComments, VersionHistoryComments
from apps.estimations.models import Quotation_Notes_Comments, Temp_Quotation_Notes_Comments
register = template.Library()


@register.simple_tag
def comments_count(request, pk):
    """
    The function counts the number of unread comments on a quotation note or temporary quotation note.
    
    :param request: The HTTP request object that contains information about the current request being
    made by the user
    :param pk: a primary key value used to identify a specific object in the database
    :return: the count of unread comments on a quotation note or a temporary quotation note, depending
    on the URL path in the request object.
    """
    if '/Estimation/view_revision_history/' in request.path:
        comments = Quotation_Notes_Comments.objects.filter(quotation_note=pk, is_read=False).exclude(created_by=request.user).count()
    else:
        comments = Temp_Quotation_Notes_Comments.objects.filter(quotation_note=pk, is_read=False).exclude(created_by=request.user).count()
    
    return comments 
