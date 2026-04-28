from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from plugins.inventory_plugin.models import Product
from .models import Order, OrderItem

User = get_user_model()

class OrderAPITestCase(APITestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='test_customer',
            password='testpass123',
            role='customer',
            grade='3rd'
        )
        # Authenticate client
        self.client.force_authenticate(user=self.user)
        
        # Create test products
        self.product1 = Product.objects.create(
            name='Wood Desk',
            quantity_in_stock=100,
            unit_price=15000
        )
        self.product2 = Product.objects.create(
            name='Office Chair',
            quantity_in_stock=50,
            unit_price=25000
        )
        
        # Define base URL
        self.place_order_url = '/api/orders/orders/place_order/'
        
    def test_place_order_success(self):
        """Test successful order creation with multiple items"""
        payload = {
            'user_id': self.user.id,
            'items': [
                {
                    'product_name': self.product1.name,
                    'product_id': self.product1.id,
                    'quantity': 2,
                    'unit_price': 15000
                },
                {
                    'product_name': self.product2.name,
                    'product_id': self.product2.id,
                    'quantity': 1,
                    'unit_price': 25000
                }
            ]
        }
        response = self.client.post(self.place_order_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 2)
        
        order = Order.objects.first()
        self.assertEqual(order.status, 'pending')
        self.assertEqual(order.total_amount, 55000) # (2*15000) + (1*25000)
        self.assertEqual(order.customer, self.user)

    def test_place_order_validation_error(self):
        """Test that negative quantities fail validation"""
        payload = {
            'user_id': self.user.id,
            'items': [
                {
                    'product_name': self.product1.name,
                    'product_id': self.product1.id,
                    'quantity': -5, # Invalid quantity
                    'unit_price': 15000
                }
            ]
        }
        response = self.client.post(self.place_order_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Order.objects.count(), 0)

    def test_premium_discount_logic(self):
        """Test 4% discount for users with >=7 orders and >=3,000,000 spent"""
        # Create 7 completed dummy orders to qualify user for discount
        for _ in range(7):
            Order.objects.create(
                customer=self.user,
                total_amount=500000,
                status='completed'
            )
            
        payload = {
            'user_id': self.user.id,
            'items': [
                {
                    'product_name': self.product1.name,
                    'product_id': self.product1.id,
                    'quantity': 10,
                    'unit_price': 15000 # subtotal = 150,000
                }
            ]
        }
        response = self.client.post(self.place_order_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify 4% discount applied (4% of 150,000 = 6,000. Total = 144,000)
        order_id = response.data['order_id']
        order = Order.objects.get(id=order_id)
        self.assertEqual(order.discount_applied, 6000)
        self.assertEqual(order.total_amount, 144000)

    def test_validate_order_auto_urgent(self):
        """Test validation sets priority to urgent if quantity > 100"""
        order = Order.objects.create(customer=self.user, status='pending')
        OrderItem.objects.create(order=order, product_name='Nails', quantity=150, unit_price=10)
        
        url = f'/api/orders/orders/{order.id}/validate_order/'
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        order.refresh_from_db()
        self.assertEqual(order.status, 'validated')
        self.assertEqual(order.priority, 'urgent')

    def test_reject_order(self):
        """Test rejecting a pending order"""
        order = Order.objects.create(customer=self.user, status='pending')
        url = f'/api/orders/orders/{order.id}/reject_order/'
        
        response = self.client.post(url, {'reason': 'Out of stock'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        order.refresh_from_db()
        self.assertEqual(order.status, 'rejected')

    def test_mark_completed(self):
        """Test marking a validated order as completed"""
        order = Order.objects.create(customer=self.user, status='validated')
        url = f'/api/orders/orders/{order.id}/mark_completed/'
        
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        order.refresh_from_db()
        self.assertEqual(order.status, 'completed')

    def test_get_pending_orders(self):
        """Test retrieving only pending orders"""
        Order.objects.create(customer=self.user, status='pending')
        Order.objects.create(customer=self.user, status='completed')
        
        url = '/api/orders/orders/pending_orders/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['orders'][0]['status'], 'pending')