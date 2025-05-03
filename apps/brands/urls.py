from django.urls import path
from apps.brands import views


urlpatterns = [
    path('list_brands/', views.list_brands, name="list_brands"),
    path('create_category_brand/<int:pk>/', views.create_category_brand, name="create_category_brand"),
    path('update_category_brand/<int:pk>/', views.update_category_brand, name="update_category_brand"),
    path('delete_category_brand/<int:pk>/', views.delete_category_brand, name="delete_category_brand"),
    path('delete_accessory_brand/<int:pk>/', views.delete_accessory_brand, name="delete_accessory_brand"),
    path('create_accessory_brand/<int:pk>/', views.create_accessory_brand, name="create_accessory_brand"),
    path('update_accessory_brand/<int:pk>/', views.update_accessory_brand, name="update_accessory_brand"),
    path('create_base_brand/', views.create_base_brand, name="create_base_brand"),
    path('edit_base_brand/<int:pk>/', views.edit_base_brand, name="edit_base_brand"),
    path('delete_base/<int:pk>/', views.delete_base, name="delete_base"),

]
