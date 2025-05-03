from django.urls import path
from apps.Workstations import views


urlpatterns = [
    path('list_workstations/', views.list_workstations, name="list_workstations"),
    path('list_workstations/<int:pk>/', views.list_workstations, name="list_workstations"),
    path('workstations_delete/<int:pk>/', views.workstations_delete, name="workstations_delete"),

]
