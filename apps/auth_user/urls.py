from django.contrib import admin
from django.urls import path, include
from apps.auth_user import views


urlpatterns = [
    path('two_step_ver/', views.two_step_verification, name="two_step_verification"),
    # path('two_step_ver/', views.two_step_verification, name="two_step_verification"),

]
