from django.urls import path
from apps.designations import views


urlpatterns = [
    path('list_add_designation/', views.list_add_designation, name="list_add_designation"),
    path('list_add_designation/<int:pk>/', views.list_add_designation, name="list_add_designation"),
    path('designation_delete/<int:pk>/', views.designation_delete, name="designation_delete"),

]
