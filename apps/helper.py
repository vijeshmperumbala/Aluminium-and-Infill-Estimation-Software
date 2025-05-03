from datetime import timedelta, datetime
from decimal import Decimal, ROUND_HALF_EVEN

import django
from apps.customers.models import Customer_Log
from apps.enquiries.models import Enquiry_Log
# from apps.estimations.models import AuditLogModel, Temp_AuditLogModel
from apps.user.models import User
import os
from django.conf import settings
from django.http import HttpResponse, Http404

    
def one_month():
    """
        The function returns the date that is 30 days from the current date and time in the timezone set in
        Django.
    """
    return django.utils.timezone.now().date() + django.utils.timezone.timedelta(days=30)


def enquiry_logger(enquiry=None, message=None, action=None, user=None):
    """
    This function logs an enquiry with relevant details such as message, action, and user.
    """
    log = Enquiry_Log(
        created_by=user,
        message=message,
        action=action,
        enquiry=enquiry,
    )
    log.save()
    

def customer_logger(customer=None, message=None, action=None, user=None):
    """
    This function creates a log entry for a customer with details such as message, action, and user.
    """
    log = Customer_Log(
        customer=customer,
        message=message,
        action=action,
        created_by=user,
    )
    log.save()
    
    
def reset_users(password=None):
    """
    This function resets the password for all users in the User model to a specified password.
    
    :param password: The password parameter is an optional argument that can be passed to the function.
    If a password is provided, it will be used to reset the password for all users in the database. If
    no password is provided, the function will not reset any passwords and will simply return True
    :return: a boolean value of True.
    """
    users = User.objects.all()
    for user in users:
        user.set_password(password)
        user.save()
    return True


def associated_key_gen(long_string):
    """
    The function takes a long string as input and returns a string consisting of the first letter of
    each word in the input string.
    
    :param long_string: The input string from which the function generates an associated key
    :return: a string that consists of the first letter of each word in the input string after splitting
    it by whitespace.
    """
    return "".join(word[0] for word in long_string.split())


# def sum_times(times):    # sourcery skip: avoid-builtin-shadow
#     """
#     The function takes a list of time strings and returns the sum of those times in hours and minutes
#     format.
#     """
#     sum = timedelta(0)
#     for time in times:
#         time_split = time.split(':')
#         if len(time_split) == 2:
#             t_delt = timedelta(
#                                 hours=int(time_split[0]),
#                                 minutes=int(time_split[1])
#                             )
#         else: 
#             t_delt = timedelta(
#                                 hours=int(time_split[0]),
#                                 minutes=int(time_split[1])
#                                 #seconds=int(time_split[2])
#                                )
#         sum += t_delt
        
#     return ':'.join(str(sum).split(':')[:2])


def sum_times(times, types=None):  # sourcery skip: avoid-builtin-shadow
    """
    The function takes a list of time strings and returns the sum of those times in hours and minutes
    format.
    """
    sum = timedelta(0)
    for time in times:
        time_split = time.split(':')
        if len(time_split) == 2: 
            t_delt = timedelta(hours=int(time_split[0]),
                               minutes=int(time_split[1]))
        else: 
            t_delt = timedelta(hours=int(time_split[0]),
                               minutes=int(time_split[1]),
                               seconds=int(time_split[2])
                               )
        sum += t_delt
    if types:
        return ':'.join(str(sum).split(':')[:2])
    else:
        return ':'.join(str(sum).split(':')[:4])

def calculate_time_difference(time1, time2):
    """
    Calculates the difference between two time durations and returns the result in "HH:MM:SS" format.

    :param time1: A string representing the first time duration in "HH:MM:SS" format.
    :param time2: A string representing the second time duration in "HH:MM:SS" format.
    :return: A string representing the difference between time1 and time2 in "HH:MM:SS" format.
    """
    time_format = "%H:%M:%S"
    dt1 = datetime.strptime(time1, time_format)
    dt2 = datetime.strptime(time2, time_format)

    diff = abs(dt1 - dt2)
    duration = timedelta(seconds=diff.seconds)

    hours = duration.seconds // 3600
    minutes = (duration.seconds // 60) % 60
    seconds = duration.seconds % 60

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def seconds_to_hh_mm_ss(seconds):
    """
    Converts the given number of seconds to the HH:MM:SS format.

    :param seconds: The number of seconds.
    :return: A string representing the time in the format HH:MM:SS.
    """
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"


def round_half_even(num, decimal_places=0):
    # Convert the number to a Decimal
    num_decimal = Decimal(str(num))
    
    # Round using ROUND_HALF_EVEN
    rounded = num_decimal.quantize(Decimal('1.' + '0'*decimal_places), rounding=ROUND_HALF_EVEN)
    
    return rounded