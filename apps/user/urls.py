from django.contrib import admin
from django.urls import path, include
from apps.user import views


urlpatterns = [
    # Basic functions
    path('', views.signin, name="signin"),
    path('logout', views.signout, name="logout"),
    
    # User related function
    path('dashboard/', views.dashboard, name="dashboard"),
    path('list_user_roles/', views.list_user_roles, name="list_user_roles"),
    path('create_uesr_role/', views.create_uesr_role, name="create_uesr_role"),
    path('update_user_role/<int:pk>/', views.update_user_role, name="update_user_role"),
    path('view_role/<int:pk>/', views.view_role, name="view_role"),
    
    path('list_users/', views.list_users, name="list_users"),
    path('create_user/', views.create_user, name="create_user"),
    path('view_user_profile/<int:pk>/', views.view_user_profile, name="view_user_profile"),
    path('update_user_details/<int:pk>/', views.update_user_details, name="update_user_details"),
    
    path('user_inactive/<int:pk>/', views.user_inactive, name="user_inactive"),
    path('user_active/<int:pk>/', views.user_active, name="user_active"),
    path('password_set/<int:pk>/', views.password_set, name="password_set"),
    path('side_settings_menu/', views.side_settings_menu, name="side_settings_menu"),
    path('permission_not_allowed/', views.permission_not_allowed, name="permission_not_allowed"),
    path('reset_data/<str:str>/', views.reset_data, name="reset_data"),
    path('backup/', views.backup_database, name='backup'),
    path('backup/<str:s_type>/', views.backup_database, name='backup'),
]

handler404 = views.error_404_view
