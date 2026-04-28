from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.forms.models import model_to_dict
from .models import *
from .serializers import *

###############-----------PRODUCT--------------############
#Create a new product
@api_view(['POST'])
def createProduct(request):
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save() #This will create new item in database
    else:
        return Response({"Error": "Invalid Payload"}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"Message": "Product successfully created"})

#Retrieve all the products
@api_view(['GET'])
# @permission_classes([AllowAny])
def getAllProducts(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True) #many=True means that we are serializing multiple items, else put it to false
    return Response(serializer.data)

#Retrieve a single product
@api_view(['GET'])
def getSingleProduct(request):
    serializer = GetSingleProductSerializer(data=request.data)
    if serializer.is_valid():
        product_id = serializer.validated_data['id']
        try:
            product = Product.objects.get(id=product_id)
            serializer_data = ProductSerializer(product, many=False)
            return Response(serializer_data.data)
        except Product.DoesNotExist:
            return Response({"Error": "Product with this id not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response({"Error": "Invalid Payload"}, status=status.HTTP_400_BAD_REQUEST)

#Update Product
@api_view(['PATCH'])
def updateProduct(request):
    serializer = UpdateProductSerializer(data=request.data, partial=True)
    if serializer.is_valid():
        product_id = serializer.validated_data['id']
        try:
            product = Product.objects.get(id=product_id)
            updatedProduct = serializer.update(product, serializer.validated_data)
            return Response({"Message": f"Product with id {product_id} successfully updated"})
        except Product.DoesNotExist:
            return Response({"Error": "Product with this id not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response({"Error": "Invalid Payload"}, status=status.HTTP_400_BAD_REQUEST)

#Delete product
@api_view(['DELETE'])
def deleteProduct(request):
    serializer = DeleteProductSerializer(data=request.data)
    if serializer.is_valid():
        product_id = serializer.validated_data['id']
        try:
            product = Product.objects.get(id=product_id)
            product.delete()
            return Response({"Message": f"Product with id {product_id} successfully deleted"}, status=status.HTTP_204_NO_CONTENT)
        except Product.DoesNotExist:
            return Response({"Error": "Product with this id not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response({"Error": "Invalid Payload"}, status=status.HTTP_400_BAD_REQUEST)

###############-----------MATERIAL--------------############
###############-----------SUPPLIER--------------############