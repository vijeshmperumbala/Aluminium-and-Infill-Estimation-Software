
import datetime
from django import template
from django.db.models import Count, Q, Sum

from django.utils.timezone import now as time
from apps.enquiries.models import Enquiries, EnquiryUser, Estimations, Pricing_Summary
from apps.user.models import User



register = template.Library()


@register.simple_tag
def price_slab(pk):
    estimation_counts = get_estimation_counts(pk)
    data = {
        "lessthan_1M": 0,
        "1M_5M": 0,
        "5M_10M": 0,
        "10M_15M": 0,
        "15M_20M": 0,
        "greater_20M": 0
    }
    calculate_slab(data, estimation_counts)
    return data


def get_estimation_counts(pk):
    return Estimations.objects.filter(
        Q(enquiry__enquiry_members=pk) & Q(version__status__in=[6, 12, 13, 15])
        # Q(enquiry__enquiry_members=pk) & Q(version__status__in=[3, 6, 12, 13, 15])
    ).values('pricing_summary_estimation__quotation').annotate(count=Count('pricing_summary_estimation__quotation'))


def calculate_slab(data, estimation_counts):
    for estimation in estimation_counts:
        quotation_price = estimation['pricing_summary_estimation__quotation']
        count = estimation['count']

        if quotation_price is not None:
            quotation_price = float(quotation_price)
            count = count

            if quotation_price <= 1000000:
                data["lessthan_1M"] += count
            elif quotation_price <= 5000000:
                data["1M_5M"] += count
            elif quotation_price <= 10000000:
                data["5M_10M"] += count
            elif quotation_price <= 15000000:
                data["10M_15M"] += count
            elif quotation_price <= 20000000:
                data["15M_20M"] += count
            else:
                data["greater_20M"] += count
                
@register.simple_tag
def daily_hr_report(user_id):
    user = User.objects.get(id=user_id)
    enquiry_active_times = EnquiryUser.objects.filter(
        date=time().date(),
        user=user
    ).values('enquiry__enquiry_id', 'enquiry__title').annotate(total_active_time=Sum('active_time'))
    data = []
    for entry in enquiry_active_times:
        enquiry_title = entry['enquiry__enquiry_id']
        enquiry_name = entry['enquiry__title']
        total_active_time = entry['total_active_time']
        formatted_time = str(total_active_time)
        enquiry_data = {
            "enquiry": enquiry_title,
            "enquiry_name": enquiry_name,
            "time": formatted_time,
        }
        data.append(enquiry_data)
    return data

    
    