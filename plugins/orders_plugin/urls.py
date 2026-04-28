from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'orders', views.OrderViewSet, basename='order')

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='order-dashboard'),
    path('customer-dashboard/', views.customer_dashboard_view, name='customer-dashboard'),
    path('', include(router.urls)),
]