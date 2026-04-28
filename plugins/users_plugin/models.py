# from django.contrib.auth.models import AbstractUser
# from django.db import models
# class User(AbstractUser):
#     ROLE_CHOICES = (
#         ('admin', 'Admin'),
#         ('production_manager', 'Production Manager'),
#         ('customer', 'Customer')
#     )

#     GRADE_CHOICES = (
#         ('1st', '1st Grade'),
#         ('2nd', '2nd Grade'),
#         ('3rd', '3rd Grade')
#     )

#     role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
#     grade = models.CharField(max_length=10, choices=GRADE_CHOICES, default='3rd')
#     transaction_count = models.IntegerField(default=0)
#     total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
from django.contrib.auth.models import AbstractUser
from django.db import models
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('production_manager', 'Production Manager'),
        ('customer', 'Customer'),
    )
    GRADE_CHOICES = (
        ('1st', '1st Grade'),
        ('2nd', '2nd Grade'),
        ('3rd', '3rd Grade'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    grade = models.CharField(max_length=10, choices=GRADE_CHOICES, default='3rd')
    transaction_count = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def is_premium(self):
        return self.transaction_count >= 7 and self.total_spent >= 3_000_000

    def __str__(self):
        return f"{self.username} ({self.role})" 