from django.urls import path
from apps.rating import views


urlpatterns = [
    path('list_rating_head/', views.list_rating_head, name="list_rating_head"),
    path('add_rating_head/', views.add_rating_head, name="add_rating_head"),
    path('update_rating_head/<int:pk>/', views.update_rating_head, name="update_rating_head"),
    path('ratehead_delete/<int:pk>/', views.ratehead_delete, name="ratehead_delete"),

]
