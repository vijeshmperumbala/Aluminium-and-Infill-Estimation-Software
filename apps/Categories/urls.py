from django.urls import path
from apps.Categories import views


urlpatterns = [
    path('category_list/', views.category_list, name="category_list"),
    path('edit_category/<int:pk>/', views.edit_category, name="edit_category"),
    path('category_delete/<int:pk>/',
         views.category_delete, name="category_delete"),

]
