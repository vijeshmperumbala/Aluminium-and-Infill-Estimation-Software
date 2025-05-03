from django import template
from apps.enquiries.models import Temp_EstimationNotes, EstimationNotes

register = template.Library()


@register.simple_tag
def note_replays(request, pk):
    """
    This function retrieves all the replay notes related to a specific note object in either the
    EstimationNotes or Temp_EstimationNotes model.
    
    :param request: The HTTP request object that contains information about the current request, such as
    the URL, headers, and data
    :param pk: pk is a parameter that represents the primary key of a specific note object. It is used
    to retrieve the note object from the database
    :return: a queryset of replay notes related to a specific note object. The queryset is filtered
    based on the estimation and main_note of the note object, and ordered by id. The specific model used
    for the queryset depends on the URL path.
    """
    if '/Estimation/estimation_notes/' in request.path:
        EstimationNotesModel = EstimationNotes
    else:
        EstimationNotesModel = Temp_EstimationNotes
        
    note_obj = EstimationNotesModel.objects.get(pk=pk)
    replay = EstimationNotesModel.objects.select_related('estimation', 'main_note').filter(
                                        estimation=note_obj.estimation, 
                                        is_replay=True, 
                                        main_note=note_obj
                                    ).order_by('id')
    return replay

