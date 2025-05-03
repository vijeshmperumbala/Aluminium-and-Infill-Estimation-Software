from django.urls import path
from apps.shopfloors import views


urlpatterns = [
    path('shopfloor_list/', views.shopfloor_list, name="shopfloor_list"),
    path('shopfloor_update/<int:pk>/', views.shopfloor_update, name="shopfloor_update"),
    path('shopfloor_delete/<int:pk>/', views.shopfloor_delete, name="shopfloor_delete"),

]
