from django.contrib import admin
from django.urls import path, include
from apps.accessories_master import views


urlpatterns = [
    path('accessories_list/', views.accessories_list, name="accessories_list"),
    path('accessories_create/<int:pk>/',
         views.accessories_create, name="accessories_create"),
    path('accessory_edit/<int:pk>/', views.accessory_edit, name="accessory_edit"),
    path('category_wise_accessories/<int:pk>/',
         views.category_wise_accessories, name="category_wise_accessories"),
    path('accessory_deletes/<int:pk>/',
         views.accessory_deletes, name="accessory_deletes"),
    # ajax url
    path('get_country_wise_brand/<int:cat_id>/<int:pk>/',
         views.get_country_wise_brand, name="get_country_wise_brand"),

]
