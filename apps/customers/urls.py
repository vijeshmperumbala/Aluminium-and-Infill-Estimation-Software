from django.urls import path
from apps.customers import views


urlpatterns = [
    path('list_add_customers/', views.list_add_customers, name="list_add_customers"),
    path('view_customer/<int:pk>/', views.view_customer, name="view_customer"),
    path('list_contacts/<int:pk>/', views.list_contacts, name="list_contacts"),
    path('edit_contact/<int:pk>/', views.edit_contact, name="edit_contact"),
    path('delete_contact/<int:pk>/', views.delete_contact, name="delete_contact"),
    path('search_customers/', views.search_customers, name="search_customers"),
    path('customer_log_modal/<int:pk>/', views.customer_log_modal, name="customer_log_modal"),
    path('get_enquiry_versions/<int:enquiry_id>/<int:customer_id>/', views.get_enquiry_versions, name="get_enquiry_versions"),
    path('version_quotation/<int:enquiry_id>/<int:customer_id>/<int:version_id>/', views.version_quotation, name="version_quotation"),
    path('edit_customer/<int:pk>/', views.edit_customer, name="edit_customer"),
    path('delete_customer/<int:pk>/', views.delete_customer, name="delete_customer"),

]
