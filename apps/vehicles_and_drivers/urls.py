
from django.urls import path
from apps.vehicles_and_drivers import views


urlpatterns = [
    path('list_vehicles_and_drivers/', views.list_vehicles_and_drivers, name="list_vehicles_and_drivers"),
    path('add_vehicles_and_drivers/<str:type>/', views.add_vehicles_and_drivers, name="add_vehicles_and_drivers"),
    path('update_vehicles_and_drivers/<int:pk>/<str:type>/', views.update_vehicles_and_drivers, name="update_vehicles_and_drivers"),
    path('vehicles_and_drivers_delete/<int:pk>/<str:type>/', views.vehicles_and_drivers_delete, name="vehicles_and_drivers_delete"),
    
]
