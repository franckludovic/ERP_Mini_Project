from django.db import models
from django.conf import settings

# Priority Levels
PRIORITY_CHOICES = [
    ('LOW', 'Low'),
    ('NORMAL', 'Normal'),
    ('HIGH', 'High'),
    ('CRITICAL', 'Critical'),
]

STATUS_CHOICES = [
    ('PENDING', 'Pending'),
    ('SENT', 'Sent'),
    ('FAILED', 'Failed'),
]

CHANNEL_CHOICES = [
    ('IN_APP', 'In App'),
    ('EMAIL', 'Email'),
]

# Template for dynamic messages
class NotificationTemplate(models.Model):
    event_type = models.CharField(max_length=100)
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES)
    subject = models.CharField(max_length=255, blank=True, null=True)
    body = models.TextField()  # supports {{variables}}

    def __str__(self):
        return f"{self.event_type} - {self.channel}"


# User preferences
class NotificationPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    email_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username


# Main notification table
class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=100)
    message = models.TextField()
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.event_type} - {self.priority}"