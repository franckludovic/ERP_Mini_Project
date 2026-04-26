from django.db import models
from django.conf import settings
from plugins.inventory_plugin.models import Product

class Order(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_urgent = models.BooleanField(default=False)
    status = models.CharField(max_length=20, default='pending') # pending, validated, completed
    created_at = models.DateTimeField(auto_now_add=True)
