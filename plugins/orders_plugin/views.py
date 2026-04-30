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

        # Check if user is banned
        from plugins.users_plugin.models import User
        from django.utils import timezone
        user = User.objects.get(pk=user_id)
        if user.is_banned:
            if user.ban_until and user.ban_until > timezone.now():
                return Response({
                    'error': 'Account Banned',
                    'message': f'Your account is banned until {user.ban_until.strftime("%Y-%m-%d %H:%M")}'
                }, status=status.HTTP_403_FORBIDDEN)
            else:
                # Ban expired
                user.is_banned = False
                user.ban_until = None
                user.save()
        
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
            status='pending',
            grade=request.data.get('grade')
        )
        
        # Create order items
        created_items = []
        for item_data in items_data:
            # Auto-resolve Product FK from inventory if not provided
            product_id = item_data.get('product_id')
            product_obj = None
            from plugins.inventory_plugin.models import Product
            if product_id:
                product_obj = Product.objects.filter(pk=product_id).first()
            if not product_obj:
                product_obj = Product.objects.filter(name__iexact=item_data['product_name']).first()
            
            order_item = OrderItem.objects.create(
                order=order,
                product_name=item_data['product_name'],
                product=product_obj,
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price']
            )
            created_items.append({
                'product_name': order_item.product_name,
                'quantity': order_item.quantity,
                'unit_price': float(order_item.unit_price),
                'subtotal': float(order_item.subtotal)
            })
        
        # Trigger notification for admins
        from plugins.notifications.utils import create_notification
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admins = User.objects.filter(role='admin') | User.objects.filter(is_superuser=True)
        for admin in admins.distinct():
            create_notification('ORDER_PLACED', admin.id, {
                'order_id': order.id,
                'username': user.username
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

        # Trigger notification for customer
        from plugins.notifications.utils import create_notification
        create_notification('ORDER_VALIDATED', order.customer.id, {
            'order_id': order.id
        })

        # Trigger notification for production managers
        from django.contrib.auth import get_user_model
        User = get_user_model()
        pm_users = User.objects.filter(role='production_manager')
        for pm in pm_users:
            create_notification('ORDER_VALIDATED_PM', pm.id, {
                'order_id': order.id
            })
        
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
        
        reason = request.data.get('reason', 'No specific reason provided')
        order.status = 'rejected'
        order.save()

        # Trigger notification for customer
        from plugins.notifications.utils import create_notification
        create_notification('ORDER_REJECTED', order.customer.id, {
            'order_id': order.id,
            'reason': reason
        })
        
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

    @action(detail=True, methods=['post'])
    def confirm_receipt(self, request, pk=None):
        """Customer confirms receipt of order"""
        order = get_object_or_404(Order, pk=pk)
        
        try:
            from plugins.mrp_production_plugin.models import Production
            productions = Production.objects.filter(item__order=order)
            if productions.exists():
                productions.update(delivery_status='delivered')
                # Deduct delivered products from finished goods inventory
                for prod in productions:
                    product = prod.item.product
                    quantity = prod.item.quantity
                    if product and quantity:
                        product.quantity_in_stock = max(0, product.quantity_in_stock - quantity)
                        product.save()
        except ImportError:
            pass
            
        return Response({
            'success': True,
            'message': 'Receipt confirmed successfully'
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
    urgent_orders = Order.objects.filter(priority='urgent').exclude(status__in=['completed', 'rejected']).count()
    
    pending_count = Order.objects.filter(status='pending').count()
    rejected_count = Order.objects.filter(status='rejected').count()
    completed_count = Order.objects.filter(status='completed').count()
    
    pending_value_dict = Order.objects.filter(status='pending').aggregate(total=Sum('total_amount'))
    pending_value = pending_value_dict['total'] or 0
    
    # Grade based analytics
    grade_1_count = Order.objects.filter(grade='1st').count()
    grade_2_count = Order.objects.filter(grade='2nd').count()
    grade_3_count = Order.objects.filter(grade='3rd').count()

    # Get latest orders for the table
    from django.db.models import Subquery, OuterRef
    try:
        from plugins.mrp_production_plugin.models import Production
        delivery_status_sq = Production.objects.filter(item__order=OuterRef('pk')).values('delivery_status')[:1]
        orders = Order.objects.all().select_related('customer').annotate(delivery_status=Subquery(delivery_status_sq)).order_by('-created_at')[:20]
    except ImportError:
        orders = Order.objects.all().select_related('customer').order_by('-created_at')[:20]
    
    base_template = 'admin_dashboard/partial.html' if request.headers.get('HX-Request') else 'admin_dashboard/base.html'
    
    context = {
        'total_active_orders': total_active_orders,
        'urgent_orders': urgent_orders,
        'pending_count': pending_count,
        'rejected_count': rejected_count,
        'completed_count': completed_count,
        'pending_value': pending_value,
        'grade_1_count': grade_1_count,
        'grade_2_count': grade_2_count,
        'grade_3_count': grade_3_count,
        'orders': orders,
        'base_template': base_template,
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
    
    from plugins.users_plugin.views import _require_session_user
    customer = _require_session_user(request)
    
    if not customer:
        from django.shortcuts import redirect
        return redirect('login-template')
        
    # Calculate metrics
    completed_orders = Order.objects.filter(customer=customer, status='completed')
    completed_orders_count = completed_orders.count()
    total_spent_dict = completed_orders.aggregate(total=Sum('total_amount'))
    total_spent = total_spent_dict['total'] or 0
    
    active_shipments_count = Order.objects.filter(customer=customer).exclude(status__in=['completed', 'rejected']).count()
    
    # Get latest orders for the table
    from django.db.models import Subquery, OuterRef
    try:
        from plugins.mrp_production_plugin.models import Production
        delivery_status_sq = Production.objects.filter(item__order=OuterRef('pk')).values('delivery_status')[:1]
        orders = Order.objects.filter(customer=customer).annotate(delivery_status=Subquery(delivery_status_sq)).order_by('-created_at')[:20]
    except ImportError:
        orders = Order.objects.filter(customer=customer).order_by('-created_at')[:20]
    
    # Calculate progress to Premium (7 orders, 3M XAF)
    orders_progress = min((completed_orders_count / 7) * 100, 100)
    spent_progress = min((float(total_spent) / 3000000.0) * 100, 100)
    progress_percent = int((orders_progress + spent_progress) / 2)
    
    # Real products from inventory
    from plugins.inventory_plugin.models import Product
    real_products = Product.objects.all()
    
    context = {
        'customer': customer,
        'completed_orders_count': completed_orders_count,
        'total_spent': total_spent,
        'active_shipments_count': active_shipments_count,
        'orders': orders,
        'progress_percent': progress_percent,
        'products': real_products,
        'grade_choices': User.GRADE_CHOICES,
    }
    
    return render(request, 'customer_dashboard.html', context)


def order_history_view(request):
    """Render the HTML order history page for customers"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    from plugins.users_plugin.views import _require_session_user
    customer = _require_session_user(request)
    
    if not customer:
        from django.shortcuts import redirect
        return redirect('login-template')
        
    orders = Order.objects.filter(customer=customer).order_by('-created_at')
    
    context = {
        'customer': customer,
        'orders': orders,
    }
    return render(request, 'order_history.html', context)