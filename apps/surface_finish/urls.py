from django.urls import path
from apps.surface_finish import views


urlpatterns = [
    path('surface_finish_list/', views.surface_finish_list, name="surface_finish_list"),
    path('surface_finish_list/<int:pk>/', views.surface_finish_list, name="surface_finish_list"),
    path('surface_finish_delete/<int:pk>/', views.surface_finish_delete, name="surface_finish_delete"),
    path('create_sf_color/<int:pk>/', views.create_sf_color, name="create_sf_color"),
    path('update_sf_color/<int:pk>/', views.update_sf_color, name="update_sf_color"),
    path('delete_secondary_product/<int:pk>/', views.delete_secondary_product, name="delete_secondary_product"),


    # AJAX URL 
    path('get_surface_price/<int:pk>/', views.get_surface_price, name="get_surface_price"),
]
