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

    @action(detail=False, methods=['post'])
    def fetch_orders(self, request):
        from plugins.orders_plugin.models import Order
        orders = Order.objects.filter(production__isnull=True)
        count = 0
        for order in orders:
            priority = 'urgent' if order.is_urgent else 'normal'
            Production.objects.create(order=order, priority_level=priority)
            count += 1
        return Response({'status': f'Fetched and created {count} production orders.'})

    @action(detail=True, methods=['get'])
    def required_materials(self, request, pk=None):
        production = self.get_object()
        boms = BOM.objects.filter(product=production.order.product)
        order_quantity = production.order.quantity
        
        materials_needed = []
        for bom in boms:
            needed = bom.quantity_required * order_quantity
            in_stock = bom.material.quantity_in_stock
            materials_needed.append({
                'material_name': bom.material.name,
                'quantity_needed': needed,
                'in_stock': in_stock,
                'is_sufficient': in_stock >= needed
            })
            
        return Response(materials_needed)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        production = self.get_object()
        if production.status != 'pending':
            return Response({'error': 'Can only start pending productions'}, status=400)
            
        boms = BOM.objects.filter(product=production.order.product)
        order_quantity = production.order.quantity
        
        insufficient_materials = []
        for bom in boms:
            needed = bom.quantity_required * order_quantity
            if bom.material.quantity_in_stock < needed:
                insufficient_materials.append(bom.material)

        if insufficient_materials and production.priority_level != 'urgent':
            return Response({
                'error': f'Not enough stock for some materials. Found shortage for {len(insufficient_materials)} materials.'
            }, status=400)

        if insufficient_materials and production.priority_level == 'urgent':
            from plugins.notifications_plugin.models import Notification
            from django.contrib.auth import get_user_model
            User = get_user_model()
            admin_user = User.objects.filter(is_superuser=True).first()
            if admin_user:
                msg = f"URGENT Production #{production.id} started. Shortage for: " + ", ".join([m.name for m in insufficient_materials])
                Notification.objects.create(user=admin_user, message=msg)
                
        # Deduct inventory
        for bom in boms:
            needed = bom.quantity_required * order_quantity
            bom.material.quantity_in_stock -= needed
            bom.material.save()
            
        production.status = 'in_progress'
        production.save()
        return Response({'status': 'Production started. Stock deducted.'})

    @action(detail=True, methods=['post'])
    def request_materials(self, request, pk=None):
        production = self.get_object()
        boms = BOM.objects.filter(product=production.order.product)
        order_quantity = production.order.quantity
        
        shortages = []
        for bom in boms:
            needed = bom.quantity_required * order_quantity
            if bom.material.quantity_in_stock < needed:
                shortages.append(f"{bom.material.name} ({needed - bom.material.quantity_in_stock} units)")
                
        if not shortages:
            return Response({'status': 'No material shortage.'}, status=400)
            
        from plugins.notifications_plugin.models import Notification
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            Notification.objects.create(user=admin_user, message=f"Material Request for Prod #{production.id}: " + ", ".join(shortages))
            return Response({'status': 'Materials requested from warehouse.'})
        return Response({'error': 'No admin user found to send notification to.'}, status=400)
