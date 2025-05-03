from django.urls import path
from apps.enquiry_type import views


urlpatterns = [
    path('enquiry_type_list/', views.enquiry_type_list, name="enquiry_type_list"),
    path('enquiry_type_list/<int:pk>/', views.enquiry_type_list, name="enquiry_type_list"),
    path('enquiry_type_delete/<int:pk>/', views.enquiry_type_delete, name="enquiry_type_delete"),
]
