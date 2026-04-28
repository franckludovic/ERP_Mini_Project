from django.db import models

class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact = models.EmailField()

    def __str__(self):
        return self.name

class Material(models.Model): # Raw materials like wood/glue
    name = models.CharField(max_length=100)
    quantity_in_stock = models.FloatField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.name} - {self.quantity_in_stock}"

class Product(models.Model): # Finished products
    name = models.CharField(max_length=100)
    quantity_in_stock = models.IntegerField(default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    materials = models.ManyToManyField(Material, through='ProductMaterial')

    def __str__(self):
        return f"{self.name} - {self.quantity_in_stock}"

class ProductMaterial(models.Model): # Bill of Materials
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantity_required = models.FloatField(default=1.0) # Quantity of material needed for 1 product

    def __str__(self):
        return f"{self.product.name} requires {self.quantity_required} of {self.material.name}"
