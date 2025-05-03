from django.urls import path
from apps.profile_types import views


urlpatterns = [
    path('profile_type_list/', views.profile_type_list, name="profile_type_list"),
    path('profile_type_list/<int:pk>/', views.profile_type_list, name="profile_type_list"),
    path('profile_type_delete/<int:pk>/', views.profile_type_delete, name="profile_type_delete"),

]
