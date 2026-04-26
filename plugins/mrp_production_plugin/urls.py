from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BOMViewSet, ProductionViewSet

router = DefaultRouter()
router.register(r'bom', BOMViewSet, basename='bom')
router.register(r'production', ProductionViewSet, basename='production')

urlpatterns = [
    path('', include(router.urls)),
]