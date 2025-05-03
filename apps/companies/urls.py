from django.urls import path
from apps.companies import views


urlpatterns = [
    path('company_list/', views.company_list, name="company_list"),
    path('create_company/', views.create_company, name="create_company"),
    path('edit_company/<int:pk>/', views.edit_company, name="edit_company"),
    path('delete_comapny/<int:pk>/', views.delete_comapny, name="delete_comapny"),
    # path('delete_contact/<int:pk>/', views.delete_contact, name="delete_contact"),


    # AJAX requests
    path('get_company_details/<int:pk>/',
         views.get_company_details, name="get_company_details"),
]
