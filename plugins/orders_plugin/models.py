from django.db import models
from django.conf import settings
from plugins.inventory_plugin.models import Product

# class Order(models.Model):
#     customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     quantity = models.IntegerField()
#     total_price = models.DecimalField(max_digits=10, decimal_places=2)
#     is_urgent = models.BooleanField(default=False)
#     status = models.CharField(max_length=20, default='pending') # pending, validated, completed
#     created_at = models.DateTimeField(auto_now_add=True)
class Order(models.Model):
    """Order header - contains customer and summary info"""
    
    PRIORITY_CHOICES = [
        ('normal', 'Normal'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Validation'),
        ('validated', 'Validated by Admin'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]
    
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_applied = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='normal')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def recalculate_total(self):
        from django.db.models import Sum
        items_total = self.items.aggregate(total=Sum('subtotal'))['total'] or 0
        self.total_amount = items_total - self.discount_applied
        self.save(update_fields=['total_amount'])

    class Meta:
        db_table = 'orders'


class OrderItem(models.Model):
    """Individual product in an order"""
    
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items'
    )
    product_name = models.CharField(max_length=200)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, editable=False)
    
    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        self.order.recalculate_total()
    
    def delete(self, *args, **kwargs):
        order = self.order
        super().delete(*args, **kwargs)
        order.recalculate_total()

    class Meta:
        db_table = 'order_items'