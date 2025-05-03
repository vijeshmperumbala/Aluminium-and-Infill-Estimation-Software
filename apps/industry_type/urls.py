from django.urls import path
from apps.industry_type import views


urlpatterns = [
    path('industry_type_list/', views.industry_type_list, name="industry_type_list"),
    path('industry_type_list/<int:pk>/', views.industry_type_list, name="industry_type_list"),
    path('industry_type_delete/<int:pk>/', views.industry_type_delete, name="industry_type_delete"),
]
