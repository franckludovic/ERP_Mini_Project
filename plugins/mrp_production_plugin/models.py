from django.db import models
from plugins.inventory_plugin.models import Product, Material
from plugins.orders_plugin.models import Order

class BOM(models.Model): # Bill of Materials
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity_required = models.FloatField()

class Production(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='pending')
    start_date = models.DateTimeField(auto_now_add=True)
