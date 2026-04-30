from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_management_template, name='admin_users'),
]
