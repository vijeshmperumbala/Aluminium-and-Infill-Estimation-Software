from django.urls import path
from apps.profiles import views


urlpatterns = [
    path('list_profiles_data/', views.list_profiles_data, name="list_profiles_data"),
    path('profile_brands/<int:cat_id>/', views.profile_brands, name="profile_brands"),
    path('list_profile_items/<int:pk>/', views.list_profile_items, name="list_profile_items"),
    path('create_profile_item/<int:pk>/', views.create_profile_item, name="create_profile_item"),
    path('edit_profile_item/<int:pk>/', views.edit_profile_item, name="edit_profile_item"),
    path('delete_profile_item/<int:pk>/', views.delete_profile_item, name="delete_profile_item"),
    path('list_profile_master_type/<int:pk>/', views.list_profile_master_type, name="list_profile_master_type"),
    path('delete_profile_type/<int:pk>/', views.delete_profile_type, name="delete_profile_type"),
    path('create_profile_type/<int:pk>/', views.create_profile_type, name="create_profile_type"),
    path('list_profile_master_series/<int:pk>/', views.list_profile_master_series, name="list_profile_master_series"),
    path('create_profile_master_series/<int:pk>/', views.create_profile_master_series, name="create_profile_master_series"),
    path('delete_profile_series/<int:pk>/', views.delete_profile_series, name="delete_profile_series"),
    
    path('aluminium_database_list/', views.aluminium_database_list, name="aluminium_database_list"),
    path('aluminium_data_export/<str:type>/', views.aluminium_data_export, name="aluminium_data_export"),
    path('aluminium_filter/<str:p_type>/', views.aluminium_filter, name="aluminium_filter"),
    path('aluminium_filter/<str:p_type>/<str:category>/', views.aluminium_filter, name="aluminium_filter"),
    path('aluminium_filter/<str:p_type>/<str:category>/<str:system>/', views.aluminium_filter, name="aluminium_filter"),
    path('addons_data_export/<str:type>/', views.addons_data_export, name="addons_data_export"),
    path('accessories_database_list/', views.accessories_database_list, name="accessories_database_list"),
    
    
    # AJAX urls
    path('get_profile_data/<int:pk>/', views.get_profile_data, name="get_profile_data"),

]
