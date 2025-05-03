from django.urls import path
from apps.addon_master import views


urlpatterns = [
    path('list_addons/', views.list_addons, name="list_addons"),
    path('list_addons/<int:pk>/', views.list_addons, name="list_addons"),
    path('addon_delete/<int:pk>/', views.addon_delete, name="addon_delete"),
    path('addons_database_list/', views.addons_database_list, name="addons_database_list"),

    # AJAX requests
    path('addon_data_estimation/<int:pk>/', views.addon_data_estimation, name="addon_data_estimation"),

]
