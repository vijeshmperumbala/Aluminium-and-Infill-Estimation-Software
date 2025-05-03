from django.urls import path
from apps.panels_and_others import views


urlpatterns = [
    path('panel_master_base/', views.panel_master_base, name="panel_master_base"),
    path('add_panel_category/', views.add_panel_category, name="add_panel_category"),
    path('delete_panel_category/<int:pk>/', views.delete_panel_category, name="delete_panel_category"),
    path('panel_brands_list/<int:pk>/', views.panel_brands_list, name="panel_brands_list"),
    path('add_panel_brands/<int:pk>/', views.add_panel_brands, name="add_panel_brands"),
    path('delete_panel_brand/<int:pk>/', views.delete_panel_brand, name="delete_panel_brand"),
    path('list_panel_series/<int:pk>/', views.list_panel_series, name="list_panel_series"),
    path('add_panel_series/<int:pk>/', views.add_panel_series, name="add_panel_series"),
    path('delete_panel_series/<int:pk>/', views.delete_panel_series, name="delete_panel_series"),
    path('list_panel_specification/<int:pk>/', views.list_panel_specification, name="list_panel_specification"),
    path('add_specification/<int:pk>/', views.add_specification, name="add_specification"),
    path('delete_panel_spec/<int:pk>/', views.delete_panel_spec, name="delete_panel_spec"),
    path('panel_item_details/<int:pk>/', views.panel_item_details, name="panel_item_details"),
    path('panel_config_add/<int:pk>/', views.panel_config_add, name="panel_config_add"),
    path('panel_config_edit/<int:pk>/', views.panel_config_edit, name="panel_config_edit"),
    path('delete_panel_config/<int:pk>/', views.delete_panel_config, name="delete_panel_config"),
    path('glass_database_list/', views.glass_database_list, name="glass_database_list"),
    
    path('glass_database_filter/<int:brand>/<int:series>/', views.glass_database_filter, name="glass_database_filter"),
    path('glass_database_filter/<int:brand>/', views.glass_database_filter, name="glass_database_filter"),
    path('glass_database_filter/<int:series>/', views.glass_database_filter, name="glass_database_filter"),
    path('glass_database_filter/', views.glass_database_filter, name="glass_database_filter"),
    path('export_glass_data/<str:type>/', views.export_glass_data, name="export_glass_data"),
    # path('glass_database_table/', views.glass_database_table, name="glass_database_table"),

]
