from django.urls import path
from apps.sealant_types import views


urlpatterns = [
    path('sealant_type_list/', views.sealant_type_list, name="sealant_type_list"),
    path('sealant_type_list/<int:pk>/', views.sealant_type_list, name="sealant_type_list"),
    path('sealant_type_delete/<int:pk>/', views.sealant_type_delete, name="sealant_type_delete"),

]
