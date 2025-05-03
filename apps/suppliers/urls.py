from django.urls import path
from apps.suppliers import views


urlpatterns = [
    path('list_suppliers/', views.list_suppliers, name="list_suppliers"),
    path('list_suppliers/<int:pk>/', views.list_suppliers, name="list_suppliers"),
    path('suppliers_delete/<int:pk>/', views.suppliers_delete, name="suppliers_delete"),
    path('list_add_boq/', views.list_add_boq, name="list_add_boq"),
    path('list_add_boq/<int:pk>/', views.list_add_boq, name="list_add_boq"),
    path('delete_boq/<int:pk>/', views.delete_boq, name="delete_boq"),
    
]
