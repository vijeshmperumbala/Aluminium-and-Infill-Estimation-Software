from django.contrib import admin
from django.urls import path, include
from apps.associated_product import views


urlpatterns = [
    path('list_associated_products/', views.list_associated_products, name="list_associated_products"),
    path('list_associated_products/<int:pk>/', views.list_associated_products, name="list_associated_products"),
    path('delete_associated_product/<int:pk>/', views.delete_associated_product, name="delete_associated_product"),
    
    # path('accessories_create/<int:pk>/',
    #      views.accessories_create, name="accessories_create"),

]
