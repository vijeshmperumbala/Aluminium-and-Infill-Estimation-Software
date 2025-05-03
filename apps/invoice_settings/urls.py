from django.urls import path
from apps.invoice_settings import views


urlpatterns = [
    path('invoice_settings_list/', views.invoice_settings_list, name="invoice_settings_list"),
    path('invoice_settings_list/<int:pk>/', views.invoice_settings_list, name="invoice_settings_list"),
    path('invoice_settings_delete/<int:pk>/', views.invoice_settings_delete, name="invoice_settings_delete"),

]
