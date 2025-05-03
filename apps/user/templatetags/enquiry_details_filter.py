from django import template
from django.db.models import Count, Case, When, IntegerField, Value, CharField

from apps.enquiries.models import Enquiries
from operator import itemgetter
from itertools import groupby

register = template.Library()


@register.simple_tag
def enquiry_details_filter(type, status):
    count = Enquiries.objects.filter(enquiry_type=type, status=status).count()
    return count


@register.simple_tag()
def enquiry_graph_data():
    ongoing_data = [0] * 6
    tender_data = [0] * 6
    status_index_map = {1: 0, 2: 1, 5: 2, 8: 3, 9: 4, 10: 5}
    ongoing_enquiries = Enquiries.objects.filter(enquiry_type=1).values('status').annotate(status_count=Count('status')) #Ongoing
    
    tender_enquiries = Enquiries.objects.filter(enquiry_type=2).values('status').annotate(status_count=Count('status')) #Tender

    for ongoing in ongoing_enquiries:
        status = ongoing['status']
        status_count = ongoing['status_count']
        if status in status_index_map:
            index = status_index_map[status]
            ongoing_data[index] = status_count
            
    for tender in tender_enquiries:
        status = tender['status']
        status_count = tender['status_count']
        if status in status_index_map:
            index = status_index_map[status]
            tender_data[index] = status_count

    return {
        "Ongoing": ongoing_data,
        "Tender": tender_data,
    }

# @register.simple_tag()
# def get_enquiry_summary():
    
#     status_mapping = {
#        1: 'Created',
#        2: 'Estimating',
#        5: 'Managment Approved',
#        7: 'On Hold',
#        8: 'Awarded',
#        9: 'Management Review',
#        10: 'Quotation Sent',
#     }
#     ongoing_enquiries = Enquiries.objects.filter(enquiry_type=1).values('status')
#     ongoing_enquiries_queryset = ongoing_enquiries.annotate(
#         status_label=Case(
#             *[When(status=s, then=Value(label)) for s, label in status_mapping.items()],
#             output_field=CharField()
#         ),
#         status_count=Count('status')
#     ).order_by('-status_label')
    
#     tender_enquiries = Enquiries.objects.filter(enquiry_type=2).values('status')
#     tender_enquiries_queryset = tender_enquiries.annotate(
#         status_label=Case(
#             *[When(status=s, then=Value(label)) for s, label in status_mapping.items()],
#             output_field=CharField()
#         ),
#         status_count=Count('status')
        
#     ).order_by('-status_label')
#     combined_data = combine_enquiries(ongoing_enquiries_queryset, tender_enquiries_queryset)

    
#     data = {
#         "ongoing_enquiries": ongoing_enquiries_queryset,
#         "tender_enquiries": tender_enquiries_queryset,
#         "datas": ['Created', 'Estimating', 'Managment Approved' 'On Hold', 'Awarded', 'Management Review', 'Quotation Sent',],
#     }
#     print("combined_data==>", combined_data)
#     return data
    



# def combine_enquiries(ongoing_enquiries_queryset, tender_enquiries_queryset):
#     combined_queryset = list(ongoing_enquiries_queryset) + list(tender_enquiries_queryset)
#     combined_queryset.sort(key=itemgetter('status_label'))

#     grouped_data = {}
#     for status_label, group in groupby(combined_queryset, key=itemgetter('status_label')):
#         total_count = sum(item['status_count'] for item in group)
#         grouped_data[status_label] = total_count

#     return grouped_data

@register.simple_tag()
def get_enquiry_summary():
    
    status_mapping = {
        1: 'Yet to Start',
        2: 'Estimating',
        9: 'Management Review',
        10: 'Quotation Sent',
        8: 'Awarded',
        7: 'On Hold',
    }
    
    # [1,2,9,10,8,7]
    
    ongoing_enquiries = Enquiries.objects.filter(enquiry_type=1, status__in=[1,2,9,10,8,7]).values('status')
    ongoing_enquiries_queryset = ongoing_enquiries.annotate(
        status_label=Case(
            *[When(status=s, then=Value(label)) for s, label in status_mapping.items()],
            output_field=CharField()
        ),
        status_count=Count('status')
    ).order_by('-status_label')
    
    tender_enquiries = Enquiries.objects.filter(enquiry_type=2, status__in=[1,2,9,10,8,7]).values('status')
    tender_enquiries_queryset = tender_enquiries.annotate(
        status_label=Case(
            *[When(status=s, then=Value(label)) for s, label in status_mapping.items()],
            output_field=CharField()
        ),
        status_count=Count('status')
    ).order_by('-status_label')
    
    status_data = {}

    for label in status_mapping.values():
        status_data[label] = {
            "ongoing": 0,
            "tender": 0,
            "total": 0,
        }

    for item in ongoing_enquiries_queryset:
        # label = item['status_label']
        label = item.get('status_label', 'Unknown')
        status_data[label]['ongoing'] = item['status_count']
        status_data[label]['total'] += item['status_count']

    for item in tender_enquiries_queryset:
        # label = item['status_label']
        label = item.get('status_label', 'Unknown')
        status_data[label]['tender'] = item['status_count']
        status_data[label]['total'] += item['status_count']

    data = {
        "status_data": status_data,
        "datas": list(status_mapping.values()),  # List of all status labels
    }
    
    
    return data