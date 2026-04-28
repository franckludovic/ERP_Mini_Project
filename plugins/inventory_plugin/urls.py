from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from . import views

urlpatterns = [
    #--Product--#
    path('create-product', views.createProduct),
    path('all-products', views.getAllProducts),
    path('single-product', views.getSingleProduct),
    path('update-product', views.updateProduct),
    path('add-product', views.addProductQuantity),
    path('reduce-product', views.reduceProductQuantity),
    path('delete-product', views.deleteProduct),

    #--Material--#
    path('create-material', views.createMaterial),
    path('all-materials', views.getAllMaterials),
    path('single-material', views.getSingleMaterial),
    path('update-material', views.updateMaterial),
    path('add-material', views.addMaterialQuantity),
    path('reduce-material', views.reduceMaterialQuantity),
    path('delete-material', views.deleteMaterial),

    #--Supplier--#
    path('create-supplier', views.createSupplier),
    path('all-suppliers', views.getAllSuppliers),
    path('single-supplier', views.getSingleSupplier),
    path('update-supplier', views.updateSupplier),
    path('delete-supplier', views.deleteSupplier),

    path('token', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'), #Used to get Access and Refresh tokens
]