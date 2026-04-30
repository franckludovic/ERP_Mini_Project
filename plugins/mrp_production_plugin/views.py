from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import BOM, Production
from .serializers import BOMSerializer, ProductionSerializer
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from plugins.notifications.utils import create_notification

User = get_user_model()


def _pm_base(request):
    """Return the correct base template for production manager based on HX-Request."""
    if request.headers.get('HX-Request'):
        return 'production_manager/partial.html'
    return 'production_manager/base.html'


@login_required
def production_page(request):
    return render(request, 'mrp/production.html', {'base_template': _pm_base(request)})


@login_required
def ledger_page(request):
    return render(request, 'mrp/ledger.html', {'base_template': _pm_base(request)})


@login_required
def history_page(request):
    return render(request, 'mrp/history.html', {'base_template': _pm_base(request)})


class BOMViewSet(viewsets.ModelViewSet):
    queryset = BOM.objects.all()
    serializer_class = BOMSerializer

class ProductionViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        from django.db.models import Case, When, Value, IntegerField
        return Production.objects.annotate(
            priority_weight=Case(
                When(item__order__priority='urgent', then=Value(1)),
                When(item__order__priority='high', then=Value(2)),
                When(item__order__priority='normal', then=Value(3)),
                When(item__order__priority='low', then=Value(4)),
                default=Value(5),
                output_field=IntegerField(),
            )
        ).order_by('priority_weight', '-start_date')
    
    serializer_class = ProductionSerializer

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        production = self.get_object()
        if production.status == 'completed':
            return Response({'status': 'Production is already completed'}, status=status.HTTP_400_BAD_REQUEST)
        
        production.status = 'completed'
        production.save()

        # Update product inventory (Requirement 13)
        product = production.item.product
        quantity = production.item.quantity

        # NEW RULE: Cannot complete if materials are insufficient, even if it was urgent
        from plugins.inventory_plugin.models import ProductMaterial
        pms = ProductMaterial.objects.filter(product=product)
        
        # Completion is allowed only if all materials for this product have stock >= 0.
        for pm in pms:
            if pm.material.quantity_in_stock < 0:
                return Response({
                    'error': f'Cannot complete: {pm.material.name} is still in deficit ({pm.material.quantity_in_stock}). Please resupply inventory first.'
                }, status=status.HTTP_400_BAD_REQUEST)

        production.status = 'completed'
        production.save()

        # Update order status
        if hasattr(production, 'item') and production.item and production.item.order:
            production.item.order.status = 'completed'
            production.item.order.save()

        if product:
            product.quantity_in_stock += quantity
            product.save()

        # Trigger notification for customer
        if hasattr(production, 'item') and production.item and production.item.order:
            create_notification('PRODUCTION_COMPLETED', production.item.order.customer.id, {
                'order_id': production.item.order.id
            })

        return Response({'status': 'Production completed, order status updated to completed, and inventory updated'})

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
        try:
            from plugins.orders_plugin.models import Order, OrderItem
            # Get all items from validated orders that don't have a production run yet
            items = OrderItem.objects.filter(order__status='validated', production__isnull=True)
            count = 0
            for item in items:
                # Use order priority as default
                priority = item.order.priority
                # Ensure priority is valid for Production model
                if priority not in ['low', 'normal', 'high', 'urgent']:
                    priority = 'normal'
                
                # Double check to prevent IntegrityError if one-to-one exists
                if not hasattr(item, 'production'):
                    Production.objects.create(item=item, priority_level=priority)
                    count += 1
            
            # Trigger auto-start check for scheduled productions
            self._check_scheduled_starts()
            
            return Response({'status': f'Fetched and created {count} production orders.'})
        except Exception as e:
            print(f"Error in fetch_orders: {str(e)}") # This will show in the terminal logs
            return Response({'error': f'Failed to fetch orders: {str(e)}'}, status=400)

    def _check_scheduled_starts(self):
        """Internal helper to start productions that reached their scheduled time"""
        from django.utils import timezone
        now = timezone.now()
        scheduled = Production.objects.filter(status='scheduled', scheduled_date__lte=now)
        for prod in scheduled:
            prod.status = 'in_progress'
            prod.save()
            # Notify
            create_notification(
                user=prod.item.order.customer,
                title="Production Started!",
                message=f"Scheduled production for your order item {prod.item.product_name} has automatically started.",
                category="PRODUCTION_STARTED"
            )
            # Notify Admin
            from django.contrib.auth import get_user_model
            User = get_user_model()
            admins = User.objects.filter(is_superuser=True)
            for admin in admins:
                create_notification(
                    user=admin,
                    title="Auto-Production Start",
                    message=f"Production for {prod.item.product_name} (Order #{prod.item.order.id}) has automatically started as scheduled.",
                    category="PRODUCTION_STARTED"
                )

    def get_queryset(self):
        # Trigger check on every list request for "automatic" feel
        self._check_scheduled_starts()
        return Production.objects.all().order_by('-start_date')

    @action(detail=True, methods=['get'])
    def required_materials(self, request, pk=None):
        production = self.get_object()
        if not production.item.product:
            return Response({'error': 'No product associated with this item'}, status=400)
            
        from plugins.inventory_plugin.models import ProductMaterial
        pms = ProductMaterial.objects.filter(product=production.item.product)
        order_quantity = production.item.quantity
        
        materials_needed = []
        for pm in pms:
            needed = pm.quantity_required * order_quantity
            in_stock = pm.material.quantity_in_stock
            materials_needed.append({
                'material_name': pm.material.name,
                'quantity_needed': needed,
                'in_stock': in_stock,
                'is_sufficient': in_stock >= needed
            })
            
        return Response({
            'product_name': production.item.product.name,
            'order_id': production.item.order.id,
            'quantity': order_quantity,
            'priority': production.item.order.priority,
            'delivery_date': production.item.order.expected_delivery_date,
            'total_value': production.item.order.total_amount,
            'materials': materials_needed
        })

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        production = self.get_object()
        if production.status not in ['pending', 'scheduled']:
            return Response({'error': 'Can only start pending or scheduled productions'}, status=400)
            
        if not production.item.product:
            return Response({'error': 'No product associated with this item'}, status=400)

        from plugins.inventory_plugin.models import ProductMaterial
        pms = ProductMaterial.objects.filter(product=production.item.product)
        order_quantity = production.item.quantity
        priority = production.item.order.priority
        
        insufficient_materials = []
        for pm in pms:
            needed_total = pm.quantity_required * order_quantity
            needed_unit = pm.quantity_required
            
            if priority == 'urgent':
                if pm.material.quantity_in_stock < needed_unit:
                    insufficient_materials.append(pm.material)
            else:
                if pm.material.quantity_in_stock < needed_total:
                    insufficient_materials.append(pm.material)

        if insufficient_materials:
            return Response({
                'error': f'Not enough stock to start. {"Even 1 unit cannot be made." if priority == "urgent" else "Full materials required for normal order."} Shortage for: {", ".join([m.name for m in insufficient_materials])}'
            }, status=400)

        if priority == 'urgent':
            # Check if there is enough for the FULL order
            partial_shortage = []
            for pm in pms:
                if pm.material.quantity_in_stock < (pm.quantity_required * order_quantity):
                    partial_shortage.append(pm.material)
            if partial_shortage:
                admin_user = User.objects.filter(is_superuser=True).first()
                if admin_user:
                    create_notification('PRODUCTION_STARTED', admin_user.id, {
                        'prod_id': production.id,
                        'order_id': production.item.order.id,
                        'shortage': ", ".join([m.name for m in partial_shortage])
                    })
                
        # Deduct inventory
        for pm in pms:
            needed = pm.quantity_required * order_quantity
            pm.material.quantity_in_stock -= needed
            pm.material.save()
            
        production.status = 'in_progress'
        production.save()

        # Trigger notification for admin on start
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            create_notification('PRODUCTION_STARTED', admin_user.id, {
                'prod_id': production.id,
                'order_id': production.item.order.id
            })

        # Trigger notification for customer on start
        if production.item.order.customer:
            create_notification('PRODUCTION_STARTED', production.item.order.customer.id, {
                'order_id': production.item.order.id,
                'product_name': production.item.product.name
            })

        return Response({'status': 'Production started. Stock deducted and notifications sent.'})

    @action(detail=True, methods=['post'])
    def schedule(self, request, pk=None):
        production = self.get_object()
        scheduled_date = request.data.get('scheduled_date')
        if not scheduled_date:
            return Response({'error': 'Scheduled date is required'}, status=400)
            
        production.status = 'scheduled'
        production.scheduled_date = scheduled_date
        production.save()

        # Trigger notification for customer
        if production.item.order.customer:
            create_notification('PRODUCTION_SCHEDULED', production.item.order.customer.id, {
                'order_id': production.item.order.id,
                'product_name': production.item.product.name,
                'scheduled_date': scheduled_date
            })

        return Response({'status': 'Production scheduled and customer notified.'})

    @action(detail=False, methods=['get'])
    def ledger_details(self, request):
        from plugins.inventory_plugin.models import ProductMaterial
        
        active_productions = Production.objects.filter(status__in=['pending', 'in_progress'])
        
        ledger_data = []
        for prod in active_productions:
            if not prod.item.product: continue
            
            pms = ProductMaterial.objects.filter(product=prod.item.product)
            for pm in pms:
                needed = pm.quantity_required * prod.item.quantity
                in_stock = pm.material.quantity_in_stock
                diff = in_stock - needed
                
                if diff > 0:
                    status_text = 'surplus'
                elif diff < 0:
                    status_text = 'shortage'
                else:
                    status_text = 'equal'
                
                ledger_data.append({
                    'material_id': pm.material.id,
                    'material_name': pm.material.name,
                    'product_name': prod.item.product.name,
                    'order_id': prod.item.order.id,
                    'needed': needed,
                    'in_stock': in_stock,
                    'balance': diff,
                    'status': status_text
                })
                
        return Response(ledger_data)

    @action(detail=False, methods=['post'])
    def request_restock(self, request):
        material_name = request.data.get('material_name')
        needed = request.data.get('needed')
        order_id = request.data.get('order_id')
        
        from plugins.notifications.models import Notification
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            msg = f"Restock request for {material_name}: Needed {needed} for Order #ORD-{order_id}"
            Notification.objects.create(user=admin_user, message=msg)
            return Response({'status': 'Restock notification sent.'})
        return Response({'error': 'No admin user found to send notification to.'}, status=400)
