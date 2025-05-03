from django.urls import path
from apps.pricing_master import views


urlpatterns = [
    path('list_price_master/', views.list_price_master, name="list_price_master"),
    path('edit_price_master/<int:pk>/', views.edit_price_master, name="edit_price_master"),
    path('price_delete/<int:pk>/', views.price_delete, name="price_delete"),
    path('edit_additional_price_master/<int:pk>/', views.edit_additional_price_master, name="edit_additional_price_master"),
    path('additional_delete/<int:pk>/', views.additional_delete, name="additional_delete"),
    path('edit_sealant_price_master/<int:pk>/', views.edit_sealant_price_master, name="edit_sealant_price_master"),
    path('sealant_pricing_delete/<int:pk>/', views.sealant_pricing_delete, name="sealant_pricing_delete"),

    # AJAX requests form_obj
    path('get_pricing/<int:pk>/', views.get_pricing, name="get_pricing"),
    path('get_additional_data/<int:pk>/', views.get_additional_data, name="get_additional_data"),
    # path('get_sealant_data/<int:pk>/', views.get_sealant_data, name="get_sealant_data"),
    path('delete_sealant_kit/<int:pk>/', views.delete_sealant_kit, name="delete_sealant_kit"),
    path('edit_surface_finish/<int:pk>/', views.edit_surface_finish, name="edit_surface_finish"),
    path('delete_surface_finish/<int:pk>/', views.delete_surface_finish, name="delete_surface_finish"),
    
    path('sealant_price_duplicate/<int:pk>/', views.sealant_price_duplicate, name="sealant_price_duplicate"),
]
