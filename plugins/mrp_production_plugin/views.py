from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import BOM, Production
from .serializers import BOMSerializer, ProductionSerializer

class BOMViewSet(viewsets.ModelViewSet):
    queryset = BOM.objects.all()
    serializer_class = BOMSerializer

class ProductionViewSet(viewsets.ModelViewSet):
    queryset = Production.objects.all()
    serializer_class = ProductionSerializer

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        production = self.get_object()
        if production.status == 'completed':
            return Response({'status': 'Production is already completed'}, status=status.HTTP_400_BAD_REQUEST)
        
        production.status = 'completed'
        production.save()

        # Update product inventory (Requirement 13)
        product = production.order.product
        quantity = production.order.quantity
        product.quantity_in_stock += quantity
        product.save()

        return Response({'status': 'Production completed, inventory updated'})

    @action(detail=True, methods=['post'])
    def update_delivery(self, request, pk=None):
        production = self.get_object()
        delivery_status = request.data.get('delivery_status')
        if delivery_status in [choice[0] for choice in Production.DELIVERY_STATUS_CHOICES]:
            production.delivery_status = delivery_status
            production.save()
            return Response({'status': f'Delivery status updated to {delivery_status}'})
        return Response({'error': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
