from django.urls import path
from apps.accessories_kit import views


urlpatterns = [
    path('accessories_kit_list/', views.accessories_kit_list,
         name="accessories_kit_list"),
    path('kit_products_list/<int:pk>/',
         views.kit_products_list, name="kit_products_list"),
    path('kit_list/<int:pk>/', views.kit_list, name="kit_list"),
    path('kit_create/<int:pk>/', views.kit_create, name="kit_create"),
    path('kit_edit/<int:pk>/', views.kit_edit, name="kit_edit"),
    # ajax url
    path('kit_delete/<int:pk>/', views.kit_delete, name="kit_delete"),
    path('kit_item_brand/<int:pk>/', views.kit_item_brand, name="kit_item_brand"),
    path('get_access_data/<int:pk>/', views.get_access_data, name="get_access_data"),
    path('get_product_accessory/<int:pk>/', views.get_product_accessory, name="get_product_accessory"),


]
