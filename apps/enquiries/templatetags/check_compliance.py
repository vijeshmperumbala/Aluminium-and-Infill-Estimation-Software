from django import template
from apps.estimations.models import EstimationProductComplaints, Temp_EstimationProductComplaints

register = template.Library()


@register.simple_tag
def check_compliance(request, pk):
    """
    The function checks if a given specification has complaints related to aluminium, panel, or surface
    finish and returns a dictionary with relevant information.
    
    :param request: The HTTP request object that contains information about the current request, such as
    the path and any data submitted with the request
    :param pk: pk is a parameter that represents the primary key of a specific object in the database.
    It is used to retrieve the object from the database and perform operations on it
    :return: a dictionary object named 'data' which contains the values of various fields related to
    compliance check of a product specification. The fields include 'aluminium_complaint',
    'is_aluminium_complaint', 'panel_complaint', 'is_panel_complaint', 'surface_finish_complaint',
    'is_surface_finish_complaint', and 'check'. The values of these fields are obtained by querying
    """
    try:
        if '/Enquiries/enquiry_profile/' in request.path:
            specification = EstimationProductComplaints.objects.get(specification=pk)
        else:
            specification = Temp_EstimationProductComplaints.objects.get(specification=pk)
            
        if not(specification.is_aluminium_complaint) and not(specification.is_panel_complaint) and not(specification.is_surface_finish_complaint):
            check = True
        else:
            check = False
        data = {
            'aluminium_complaint': specification.aluminium_complaint,
            'is_aluminium_complaint': specification.is_aluminium_complaint,
            'panel_complaint': specification.panel_complaint,
            'is_panel_complaint': specification.is_panel_complaint,
            'surface_finish_complaint': specification.surface_finish_complaint,
            'is_surface_finish_complaint': specification.is_surface_finish_complaint,
            'check': check
        }
       
    except Exception as e:
        print("Exception:", e)
        data = None
        
    return data