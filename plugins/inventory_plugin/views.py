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

#Add product quantity
@api_view(['PATCH'])
def addProductQuantity(request):
    serializer = addOrRemoveProductSerializer(data=request.data, partial=True)
    if serializer.is_valid():
        product_id = serializer.validated_data['id']
        try:
            product = Product.objects.get(id=product_id)
            currentQuantity = product.quantity_in_stock
            newQuantity = currentQuantity + serializer.validated_data['quantity']
            serializer.update(product, {"quantity_in_stock" : newQuantity})
            return Response({"Message": f"Quantity Successfully updated for product with id {product_id}"})
        except Product.DoesNotExist:
            return Response({"Error": "Product with this id not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response({"Error": "Invalid Payload"}, status=status.HTTP_400_BAD_REQUEST)

#Reduce product quantity
@api_view(['PATCH'])
def reduceProductQuantity(request):
    serializer = addOrRemoveProductSerializer(data=request.data, partial=True)
    if serializer.is_valid():
        product_id = serializer.validated_data['id']
        try:
            product = Product.objects.get(id=product_id)
            currentQuantity = product.quantity_in_stock
            newQuantity = currentQuantity - serializer.validated_data['quantity']
            serializer.update(product, {"quantity_in_stock" : newQuantity})
            return Response({"Message": f"Quantity Successfully updated for product with id {product_id}"})
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
#Create a new material
@api_view(['POST'])
def createMaterial(request):
    serializer = MaterialSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    else:
        return Response({"Error": "Invalid Payload"}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"Message": "Material successfully created"})

#Retrieve all the materials
@api_view(['GET'])
def getAllMaterials(request):
    materials = Material.objects.select_related('supplier').all()
    serializer = MaterialSerializer(materials, many=True) #many=True means that we are serializing multiple items, else put it to false
    return Response(serializer.data)

#Retrieve a single material
@api_view(['GET'])
def getSingleMaterial(request):
    serializer = GetSingleMaterialSerializer(data=request.data)
    if serializer.is_valid():
        material_id = serializer.validated_data['id']
        try:
            material = Material.objects.get(id=material_id)
            serializer_data = MaterialSerializer(material, many=False)
            return Response(serializer_data.data)
        except Product.DoesNotExist:
            return Response({"Error": "Material with this id not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response({"Error": "Invalid Payload"}, status=status.HTTP_400_BAD_REQUEST)

#Update Material
@api_view(['PATCH'])
def updateMaterial(request):
    serializer = UpdateMaterialSerializer(data=request.data, partial=True)
    if serializer.is_valid():
        material_id = serializer.validated_data['id']
        try:
            material = Material.objects.get(id=material_id)
            updatedMaterial = serializer.update(material, serializer.validated_data)
            return Response({"Message": f"Material with id {material_id} successfully updated"})
        except Material.DoesNotExist:
            return Response({"Error": "Material with this id not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response({"Error": "Invalid Payload"}, status=status.HTTP_400_BAD_REQUEST)

#Add product quantity
@api_view(['PATCH'])
def addMaterialQuantity(request):
    serializer = addOrRemoveMaterialSerializer(data=request.data, partial=True)
    if serializer.is_valid():
        material_id = serializer.validated_data['id']
        try:
            material = Material.objects.get(id=material_id)
            currentQuantity = material.quantity_in_stock
            newQuantity = currentQuantity + serializer.validated_data['quantity']
            serializer.update(material, {"quantity_in_stock" : newQuantity})
            return Response({"Message": f"Quantity Successfully updated for material with id {material_id}"})
        except Material.DoesNotExist:
            return Response({"Error": "Material with this id not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response({"Error": "Invalid Payload"}, status=status.HTTP_400_BAD_REQUEST)

#Reduce product quantity
@api_view(['PATCH'])
def reduceMaterialQuantity(request):
    serializer = addOrRemoveMaterialSerializer(data=request.data, partial=True)
    if serializer.is_valid():
        material_id = serializer.validated_data['id']
        try:
            material = Material.objects.get(id=material_id)
            currentQuantity = material.quantity_in_stock
            newQuantity = currentQuantity - serializer.validated_data['quantity']
            serializer.update(material, {"quantity_in_stock" : newQuantity})
            return Response({"Message": f"Quantity Successfully updated for material with id {material_id}"})
        except Material.DoesNotExist:
            return Response({"Error": "Material with this id not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response({"Error": "Invalid Payload"}, status=status.HTTP_400_BAD_REQUEST)

#Delete product
@api_view(['DELETE'])
def deleteMaterial(request):
    serializer = DeleteProductSerializer(data=request.data)
    if serializer.is_valid():
        material_id = serializer.validated_data['id']
        try:
            material = Material.objects.get(id=material_id)
            material.delete()
            return Response({"Message": f"Material with id {material_id} successfully deleted"}, status=status.HTTP_204_NO_CONTENT)
        except Product.DoesNotExist:
            return Response({"Error": "Material with this id not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response({"Error": "Invalid Payload"}, status=status.HTTP_400_BAD_REQUEST)


###############-----------SUPPLIER--------------############
#Create a new supplier
@api_view(['POST'])
def createSupplier(request):
    serializer = SupplierSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
    else:
        return Response({"Error": "Invalid Payload"}, status=status.HTTP_400_BAD_REQUEST)
    return Response({"Message": "Supplier successfully created"})

#Retrieve all the suppliers
@api_view(['GET'])
def getAllSuppliers(request):
    suppliers = Supplier.objects.all()
    serializer = SupplierSerializer(suppliers, many=True)
    return Response(serializer.data)

#Retrieve a single supplier
@api_view(['GET'])
def getSingleSupplier(request):
    serializer = GetSingleSupplierSerializer(data=request.data)
    if serializer.is_valid():
        material_id = serializer.validated_data['id']
        try:
            material = Material.objects.get(id=material_id)
            serializer_data = MaterialSerializer(material, many=False)
            return Response(serializer_data.data)
        except Material.DoesNotExist:
            return Response({"Error": "Material with this id not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response({"Error": "Invalid Payload"}, status=status.HTTP_400_BAD_REQUEST)

#Update Supplier
@api_view(['PATCH'])
def updateSupplier(request):
    serializer = UpdateSupplierSerializer(data=request.data, partial=True)
    if serializer.is_valid():
        supplier_id = serializer.validated_data['id']
        try:
            supplier = Supplier.objects.get(id=supplier_id)
            updatedSupplier = serializer.update(supplier, serializer.validated_data)
            return Response({"Message": f"Product with id {supplier_id} successfully updated"})
        except Supplier.DoesNotExist:
            return Response({"Error": "Supplier with this id not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response({"Error": "Invalid Payload"}, status=status.HTTP_400_BAD_REQUEST)

#Delete supplier
@api_view(['DELETE'])
def deleteSupplier(request):
    serializer = DeleteSupplierSerializer(data=request.data)
    if serializer.is_valid():
        supplier_id = serializer.validated_data['id']
        try:
            supplier = Supplier.objects.get(id=supplier_id)
            supplier.delete()
            return Response({"Message": f"Supplier with id {supplier_id} successfully deleted"}, status=status.HTTP_204_NO_CONTENT)
        except Supplier.DoesNotExist:
            return Response({"Error": "Supplier with this id not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response({"Error": "Invalid Payload"}, status=status.HTTP_400_BAD_REQUEST)