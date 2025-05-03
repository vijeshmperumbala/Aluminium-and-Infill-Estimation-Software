from django.urls import path
from apps.others import views

urlpatterns = [
    path('other_settings/', views.other_settings, name="other_settings"),
    path('update_ai_rating/', views.update_ai_rating, name="update_ai_rating"),
    path('add_estimation_submit_parameters/', views.add_estimation_submit_parameters, name="add_estimation_submit_parameters"),
    path('update_estimation_submit_parameters/<int:pk>/', views.update_estimation_submit_parameters, name="update_estimation_submit_parameters"),
    path('delete_parameter/<int:pk>/', views.delete_parameter, name="delete_parameter"),
    
    # path('aluminium_baserateadd/', views.aluminium_baserateadd, name="aluminium_baserateadd"),
    # path('aluminium_baserateupdate/<int:pk>/', views.aluminium_baserateupdate, name="aluminium_baserateupdate"),
    # path('delete_aluminium_baserate/<int:pk>/', views.delete_aluminium_baserate, name="delete_aluminium_baserate"),
    
    path('loh_percentage_add/', views.loh_percentage_add, name="loh_percentage_add"),
    path('loh_percentage_update/<int:pk>/', views.loh_percentage_update, name="loh_percentage_update"),
    path('delete_loh_percentage/<int:pk>/', views.delete_loh_percentage, name="delete_loh_percentage"),
    path('elevation_add/<int:pk>/', views.elevation_add, name="elevation_add"),
    path('elevation_update/<int:pk>/', views.elevation_update, name="elevation_update"),
    path('delete_elevation/<int:pk>/', views.delete_elevation, name="delete_elevation"),
    path('project_building_add/<int:pk>/', views.project_building_add, name="project_building_add"),
    path('project_building_update/<int:pk>/', views.project_building_update, name="project_building_update"),
    path('delete_project_building/<int:pk>/', views.delete_project_building, name="delete_project_building"),
    
    path('project_floor_add/<int:pk>/', views.project_floor_add, name="project_floor_add"),
    path('project_floor_update/<int:pk>/', views.project_floor_update, name="project_floor_update"),
    path('delete_project_floor/<int:pk>/', views.delete_project_floor, name="delete_project_floor"),
    
]
