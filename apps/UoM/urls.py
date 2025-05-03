from django.urls import path
from apps.UoM import views


urlpatterns = [
    path('uom_list/', views.uom_list, name="uom_list"),
    path('uom_list/<int:pk>/', views.uom_list, name="uom_list"),
    path('uom_delete/<int:pk>/', views.uom_delete, name="uom_delete"),

]
