from django.urls import path
from apps.project_specifications import views


urlpatterns = [
    path('list_project_specifications/', views.list_project_specifications, name="list_project_specifications"),
    path('list_project_specifications/<int:pk>/', views.list_project_specifications, name="list_project_specifications"),
    path('project_spec_delete/', views.project_spec_delete, name="project_spec_delete"),
    path('project_spec_delete/<int:pk>/', views.project_spec_delete, name="project_spec_delete"),
    # # Ajax requests
    # path('get_provisions_data/<int:pk>/', views.get_provisions_data, name="get_provisions_data"),
]
