from django import template
from apps.enquiries.models import (
    Enquiries, 
    EnquiryUser, 
    Estimations, 
    Temp_Estimations,
)

from apps.estimations.models import (
    Estimation_UserTimes, 
    EstimationMainProduct, 
    EstimationVersions,
    Temp_Estimation_UserTimes, 
    Temp_EstimationMainProduct,
)
from apps.others.models import AI_RatingModel

register = template.Library()


@register.simple_tag
def get_version(pk):
    """
    The function returns the ID of the latest version of an Estimations object related to a given
    Enquiry object.
    
    :param pk: The parameter "pk" is likely an abbreviation for "primary key". It is used as an argument
    to filter the Estimations objects by their related Enquiry object's primary key. The function then
    returns the ID of the last Estimations object that matches the filter criteria
    :return: the ID of the latest version of an Estimations object related to a given Enquiry object
    (identified by its primary key 'pk'). If there are no Estimations objects related to the Enquiry
    object, it will return 0. If there is an exception raised during the execution of the function, it
    will also return 0.
    """
    try:
        version = Estimations.objects.select_related('enquiry').filter(enquiry=pk).last()
        return version
    except Exception:
        return 0


@register.simple_tag
def estimation_ai_rating(estimation, temp=None):
    product_count_unit = 0
    total_active_time_seconds_unit = 0
    
    if not temp:
        estimation_obj = Estimations.objects.get(pk=estimation)
        if estimation_obj.version.version == '0':
            product_count = EstimationMainProduct.objects.filter(building__estimation=estimation_obj).count()
            time_data = Estimation_UserTimes.objects.filter(estimation=estimation_obj)
            total_active_time_seconds = sum([entry.active_time.total_seconds() for entry in time_data])
                
        else:
            sub_estimation_objs = Estimations.objects.filter(enquiry=estimation_obj.enquiry.id)
            
            for sub_estimation_obj in sub_estimation_objs:
                if estimation_obj.version.version >= sub_estimation_obj.version.version:
                    product_count_unit += EstimationMainProduct.objects.filter(building__estimation=sub_estimation_obj).count()
                    product_count = product_count_unit
                    time_data = Estimation_UserTimes.objects.filter(estimation=sub_estimation_obj)
                    total_active_time_seconds_unit += sum([entry.active_time.total_seconds() for entry in time_data])
                    total_active_time_seconds = total_active_time_seconds_unit
                else:
                    product_count = None
                    time_data = None
                    total_active_time_seconds = None
    else: 
        try:
            estimation_obj = Temp_Estimations.objects.get(pk=estimation)
            product_count = Temp_EstimationMainProduct.objects.filter(building__estimation=estimation_obj).count()
            time_data = Temp_Estimation_UserTimes.objects.filter(estimation=estimation_obj)
            total_active_time_seconds = sum([entry.active_time.total_seconds() for entry in time_data])
            product_count_unit += product_count
            total_active_time_seconds_unit += total_active_time_seconds
            
            sub_estimation_objs = Estimations.objects.filter(enquiry=estimation_obj.enquiry.id)
            for sub_estimation_obj in sub_estimation_objs:
                
                if estimation_obj.version.version >= sub_estimation_obj.version.version:
                    product_count_unit += EstimationMainProduct.objects.filter(building__estimation=sub_estimation_obj).count()
                    product_count = product_count_unit
                    time_data = Estimation_UserTimes.objects.filter(estimation=sub_estimation_obj)
                    total_active_time_seconds_unit += sum([entry.active_time.total_seconds() for entry in time_data])
                    total_active_time_seconds = total_active_time_seconds_unit
                else:
                    product_count = None
                    time_data = None
                    total_active_time_seconds = None
            
        except Exception as e:
            print('EXCEPTION==>', e)
            estimation_obj = None
            time_data = None
            product_count = None
        
    smallest_from_value_entry = AI_RatingModel.objects.order_by('to_value').first().to_value
    if product_count:
        total_product_count = product_count
    else:
        total_product_count = 0

    if total_product_count > 0 and total_active_time_seconds:
        system_calculated_time = total_product_count*smallest_from_value_entry
        ai_label = total_active_time_seconds/total_product_count

        matching_entry = AI_RatingModel.objects.filter(from_value__lte=ai_label, to_value__gte=ai_label).first()
        
        data = {
            'matching_entry': matching_entry,
            'total_active_time_seconds': seconds_to_hh_mm(total_active_time_seconds),
        }
        return data

    else:
        return None
    

def seconds_to_hh_mm(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (minutes % 3600) // 360
    return "{:02d}:{:02d}:{:02d}".format(int(hours), int(minutes), int(seconds))
