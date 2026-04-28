from django.db import models

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact = models.EmailField()

    def __str__(self):
        return self.name

class Material(models.Model): # Raw materials like wood/glue
    name = models.CharField(max_length=100)
    quantity_in_stock = models.FloatField()
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.name} - {self.quantity_in_stock}"

class Product(models.Model): # Finished products
    name = models.CharField(max_length=100)
    quantity_in_stock = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.quantity_in_stock}"
