from django.urls import path, re_path
from apps.estimations.consumers import (
        EstimationNotesConsumer, 
        EnquiryUserActivetime,
        NotificationsConsumer,
        EstimationNotesIndication,
        EnquiryNotesConsumer,
)

ws_urlpatterns = [
    re_path(r'ws/estimation/(?P<estimation_id>\w+)/(?P<temp>\w+)/$', EstimationNotesConsumer.as_asgi()),
    re_path(r'ws/active_timer/(?P<enquiry_id>\w+)/(?P<user_id>\w+)/$', EnquiryUserActivetime.as_asgi()),
    re_path(r'ws/notifications/(?P<user_id>\w+)/$', NotificationsConsumer.as_asgi()),
    re_path(r'ws/notification_indications/(?P<enquiry_id>\w+)/(?P<temp>\w+)/$', EstimationNotesIndication.as_asgi()),
    re_path(r'ws/enquiry_messages/(?P<enquiry_id>\w+)/$', EnquiryNotesConsumer.as_asgi()),
    
]
