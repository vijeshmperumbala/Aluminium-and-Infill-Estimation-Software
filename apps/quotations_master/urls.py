from django.urls import path
from apps.quotations_master import views


urlpatterns = [
    path('list_quotations_master/', views.list_quotations_master, name="list_quotations_master"),
    path('create_short_quotation_template/', views.create_short_quotation_template, name="create_short_quotation_template"),
    path('edit_short_quotation_template/<int:pk>/', views.edit_short_quotation_template, name="edit_short_quotation_template"),
    path('delete_quotation_template/<int:pk>/', views.delete_quotation_template, name="delete_quotation_template"),
    path('create_general_quotation_template/', views.create_general_quotation_template, name="create_general_quotation_template"),
    path('edit_general_quotation_template/<int:pk>/', views.edit_general_quotation_template, name="edit_general_quotation_template"),
    
    # AJAX Request URL
    path('get_short_quotation_template/<int:pk>/', views.get_short_quotation_template, name="get_short_quotation_template"),
    path('get_general_quotation_template/<int:pk>/', views.get_general_quotation_template, name="get_general_quotation_template"),
    path('duplicate_quotation_master/<int:pk>/', views.duplicate_quotation_master, name="duplicate_quotation_master"),

]
