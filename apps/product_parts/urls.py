from django.urls import path
from apps.product_parts import views


urlpatterns = [
    path('list_parts/', views.list_parts, name="list_parts"),
    path('list_parts_by_category/<int:pk>/', views.list_parts_by_category, name="list_parts_by_category"),
    path('create_parts_data/<int:pk>/', views.create_parts_data, name="create_parts_data"),
    path('edit_parts_data/<int:pk>/', views.edit_parts_data, name="edit_parts_data"),
    path('delete_parts/<int:pk>/', views.delete_parts, name="delete_parts"),
    path('create_parts_kit/<int:pk>/', views.create_parts_kit, name="create_parts_kit"),
    path('series_kit_edit/<int:pk>/', views.series_kit_edit, name="series_kit_edit"),
    path('delete_series_kit/<int:pk>/', views.delete_series_kit, name="delete_series_kit"),

    # AJAX url 
    path('get_profile_select/<int:pk>/', views.get_profile_select, name="get_profile_select"),
]
