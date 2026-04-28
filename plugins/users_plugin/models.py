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
from django.core.validators import RegexValidator

class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text="Required. 150 characters or fewer. Letters, digits and spaces only.",
        validators=[RegexValidator(r'^[\w\s.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers, spaces, and @/./+/-/_ characters.')],
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )
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
    grade = models.CharField(max_length=10, choices=GRADE_CHOICES, null=True, blank=True)
    transaction_count = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    is_banned = models.BooleanField(default=False)
    ban_until = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def is_premium(self):
        return self.transaction_count >= 7 and self.total_spent >= 3_000_000

    def __str__(self):
        return f"{self.username} ({self.role})" 