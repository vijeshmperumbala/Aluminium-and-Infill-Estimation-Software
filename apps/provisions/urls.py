from django.urls import path
from apps.provisions import views


urlpatterns = [
    path('provisions_list/', views.provisions_list, name="provisions_list"),
    path('provisions_list/<int:pk>/', views.provisions_list, name="provisions_list"),
    path('provisions_delete/<int:pk>/', views.provisions_delete, name="provisions_delete"),
    # Ajax requests
    path('get_provisions_data/<int:pk>/', views.get_provisions_data, name="get_provisions_data"),
]
