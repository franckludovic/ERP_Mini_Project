from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404, render
from .models import Order, OrderItem
from .serializers import CreateOrderSerializer, OrderDetailSerializer

class OrderViewSet(viewsets.ModelViewSet):

    queryset = Order.objects.all().order_by('-created_at')
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'retrieve':
            return OrderDetailSerializer
        return OrderDetailSerializer
    
    def get_permissions(self):
        """Set permissions based on action"""
        # Temporarily allow any access for testing purposes
        return [AllowAny()]
    
    @action(detail=False, methods=['post'])
    @transaction.atomic
    def place_order(self, request):
        """Create an order with multiple products"""
        
        # Validate input
        serializer = CreateOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'Validation failed',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        user_id = validated_data['user_id']
        items_data = validated_data['items']
        
        # Calculate subtotal
        subtotal = 0
        for item in items_data:
            subtotal += item['quantity'] * item['unit_price']
        
        # Calculate discount for premium customers
        discount_percentage = 0
        discount_amount = 0
        
        customer_orders = Order.objects.filter(customer_id=user_id, status='completed')
        order_count = customer_orders.count()
        total_spent = customer_orders.aggregate(total=Sum('total_amount'))['total'] or 0
        
        if order_count >= 7 and total_spent >= 3000000:
            discount_percentage = 4
            discount_amount = (subtotal * discount_percentage) / 100
        
        total_price = subtotal - discount_amount
        
        # Create order
        order = Order.objects.create(
            customer_id=user_id,
            total_amount=total_price,
            discount_applied=discount_amount,
            priority='normal',
            status='pending'
        )
        
        # Create order items
        created_items = []
        for item_data in items_data:
            order_item = OrderItem.objects.create(
                order=order,
                product_name=item_data['product_name'],
                product_id=item_data.get('product_id'),
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price']
            )
            created_items.append({
                'product_name': order_item.product_name,
                'quantity': order_item.quantity,
                'unit_price': float(order_item.unit_price),
                'subtotal': float(order_item.subtotal)
            })
        
        response_data = {
            'success': True,
            'order_id': order.id,
            'message': 'Order placed successfully!',
            'summary': {
                'subtotal': subtotal,
                'discount_percentage': discount_percentage,
                'discount_amount': discount_amount,
                'total_amount': float(order.total_amount),
                'currency': 'FCFA'
            },
            'items': created_items,
            'status': order.status,
            'created_at': order.created_at
        }
        
        if discount_percentage > 0:
            response_data['message'] = f'Order placed successfully! {discount_percentage}% discount applied as premium customer.'
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def validate_order(self, request, pk=None):
        """Admin validates an order"""
        
        order = get_object_or_404(Order, pk=pk)
        
        if order.status != 'pending':
            return Response({
                'error': f'Cannot validate order. Current status: {order.status}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        total_quantity = order.items.aggregate(total=Sum('quantity'))['total'] or 0
        
        if total_quantity > 100:
            order.priority = 'urgent'
        
        order.status = 'validated'
        order.save()
        
        return Response({
            'success': True,
            'order_id': order.id,
            'status': order.status,
            'priority': order.priority,
            'message': f'Order validated as {order.priority.upper()} priority'
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def pending_orders(self, request):
        """Get all pending orders"""
        pending_orders = Order.objects.filter(status='pending')
        serializer = OrderDetailSerializer(pending_orders, many=True)
        return Response({
            'count': pending_orders.count(),
            'orders': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def urgent_orders(self, request):
        """Get all urgent orders"""
        urgent_orders = Order.objects.filter(priority='urgent')
        serializer = OrderDetailSerializer(urgent_orders, many=True)
        return Response({
            'count': urgent_orders.count(),
            'orders': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def ready_for_production(self, request):
        """Get validated orders ready for production"""
        ready_orders = Order.objects.filter(status='validated')
        serializer = OrderDetailSerializer(ready_orders, many=True)
        return Response({
            'count': ready_orders.count(),
            'orders': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def reject_order(self, request, pk=None):
        """Admin rejects an order"""
        order = get_object_or_404(Order, pk=pk)
        
        if order.status != 'pending':
            return Response({
                'error': f'Cannot reject order with status: {order.status}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        reason = request.data.get('reason', 'No reason provided')
        order.status = 'rejected'
        order.save()
        
        return Response({
            'success': True,
            'order_id': order.id,
            'status': 'rejected',
            'reason': reason,
            'message': 'Order rejected successfully'
        })
    
    @action(detail=True, methods=['post'])
    def mark_completed(self, request, pk=None):
        """Mark order as completed"""
        order = get_object_or_404(Order, pk=pk)
        
        if order.status != 'validated':
            return Response({
                'error': f'Only validated orders can be completed. Current status: {order.status}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        order.status = 'completed'
        order.save()
        
        return Response({
            'success': True,
            'order_id': order.id,
            'status': 'completed',
            'message': 'Order completed successfully'
        })

    @action(detail=True, methods=['post'])
    def mark_urgent(self, request, pk=None):
        """Admin marks an order as urgent"""
        order = get_object_or_404(Order, pk=pk)
        
        if order.status in ['completed', 'rejected']:
            return Response({
                'error': f'Cannot change priority of {order.status} order'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        order.priority = 'urgent'
        order.save()
        
        return Response({
            'success': True,
            'order_id': order.id,
            'priority': 'urgent',
            'message': 'Order marked as urgent'
        })
    
    @action(detail=True, methods=['get'])
    def get_order_with_items(self, request, pk=None):
        """Get complete order details including all items"""
        order = get_object_or_404(Order, pk=pk)
        serializer = OrderDetailSerializer(order)
        return Response(serializer.data)


def dashboard_view(request):
    """Render the HTML dashboard for order management"""
    
    # Calculate metrics
    total_active_orders = Order.objects.exclude(status__in=['completed', 'rejected']).count()
    urgent_mismatches = Order.objects.filter(priority='urgent', status__in=['pending', 'validated']).count()
    
    pending_value_dict = Order.objects.filter(status='pending').aggregate(total=Sum('total_amount'))
    pending_value = pending_value_dict['total'] or 0
    
    # Get latest orders for the table
    orders = Order.objects.all().select_related('customer').order_by('-created_at')[:20]
    
    context = {
        'total_active_orders': total_active_orders,
        'urgent_mismatches': urgent_mismatches,
        'pending_value': pending_value,
        'orders': orders,
    }
    
    return render(request, 'order_dashboard.html', context)


# from django.contrib.auth.decorators import login_required
# @login_required
def customer_dashboard_view(request):
    """Render the HTML customer dashboard"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # --- FUTURE PRODUCTION CODE (Uncomment when User Management is ready) ---
    # customer = request.user
    # ------------------------------------------------------------------------
    
    # --- CURRENT DEVELOPMENT CODE (Delete this block when User Management is ready) ---
    if request.user.is_authenticated:
        customer = request.user
    else:
        customer = User.objects.filter(role='customer').first()
        
    if not customer:
        customer = User.objects.first() # Fallback if no customers exist
    # ----------------------------------------------------------------------------------
        
    # Calculate metrics
    completed_orders = Order.objects.filter(customer=customer, status='completed')
    completed_orders_count = completed_orders.count()
    total_spent_dict = completed_orders.aggregate(total=Sum('total_amount'))
    total_spent = total_spent_dict['total'] or 0
    
    active_shipments_count = Order.objects.filter(customer=customer).exclude(status__in=['completed', 'rejected']).count()
    
    # Get latest orders for the table
    orders = Order.objects.filter(customer=customer).order_by('-created_at')[:20]
    
    # Calculate progress to Premium (7 orders, 3M XAF)
    orders_progress = min((completed_orders_count / 7) * 100, 100)
    spent_progress = min((float(total_spent) / 3000000.0) * 100, 100)
    progress_percent = int((orders_progress + spent_progress) / 2)
    
    # Mock products for the order form (to be replaced with inventory integration)
    mock_products = [
        {'id': 1, 'name': 'Industrial Raw Materials', 'unit_price': 15000},
        {'id': 2, 'name': 'Office Supplies', 'unit_price': 2500},
        {'id': 3, 'name': 'Tech Components', 'unit_price': 45000},
    ]
    
    context = {
        'customer': customer,
        'completed_orders_count': completed_orders_count,
        'total_spent': total_spent,
        'active_shipments_count': active_shipments_count,
        'orders': orders,
        'progress_percent': progress_percent,
        'mock_products': mock_products,
    }
    
    return render(request, 'customer_dashboard.html', context)