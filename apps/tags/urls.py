
from django.urls import path
from apps.tags import views


urlpatterns = [
    path('list_tags/', views.list_tags, name="list_tags"),
    path('list_tags/<int:pk>/', views.list_tags, name="list_tags"),
    path('delete_tag/<int:pk>/', views.delete_tag, name="delete_tag"),
    # path('surface_finish_delete/<int:pk>/', views.surface_finish_delete, name="surface_finish_delete"),


    # # AJAX URL 
    # path('get_surface_price/<int:pk>/', views.get_surface_price, name="get_surface_price"),
]
