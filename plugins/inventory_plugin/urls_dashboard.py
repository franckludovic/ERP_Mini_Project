from django.urls import path
from .views import inventory_dashboard_view

urlpatterns = [
    path('', inventory_dashboard_view, name='inventory_dashboard'),
]
