from django.urls import path
from . import views

urlpatterns = [
    path('', views.notifications_page, name='admin_notifications'),
]
