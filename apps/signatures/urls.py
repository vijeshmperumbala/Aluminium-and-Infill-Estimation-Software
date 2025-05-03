from django.urls import path
from apps.signatures import views


urlpatterns = [
    path('list_signatures/<int:pk>/', views.list_signatures, name="list_signatures"),
    path('list_signatures/', views.list_signatures, name="list_signatures"),
    path('delete_signature/<int:pk>/', views.delete_signature, name="delete_signature"),
    path('sign_edit/<int:pk>/', views.sign_edit, name="sign_edit"),

]
