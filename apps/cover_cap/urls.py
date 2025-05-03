from django.urls import path
from apps.cover_cap import views


urlpatterns = [
    path('covercap_list/', views.covercap_list, name="covercap_list"),
    path('delete_covercap_pressure_plate/<int:pk>/', views.delete_covercap_pressure_plate, name="delete_covercap_pressure_plate"),
    path('edit_covercap/<int:pk>/', views.edit_covercap, name="edit_covercap"),
]
