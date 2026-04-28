from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from . import views

urlpatterns = [
    path('create-product', views.createProduct),
    path('all-products', views.getAllProducts),
    path('single-product', views.getSingleProduct),
    path('update-product', views.updateProduct),
    path('delete-product', views.deleteProduct),
    path('token', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'), #Used to get Access and Refresh tokens
]