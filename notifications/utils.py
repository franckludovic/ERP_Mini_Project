from .models import NotificationTemplate, NotificationPreference, Notification
from django.contrib.auth.models import User


# Simple template rendering
def render_template(template, data):
    message = template
    for key, value in data.items():
        message = message.replace(f"{{{{{key}}}}}", str(value))
    return message


# Priority logic
def get_priority(event, user):
    if event == "ORDER_MARKED_URGENT":
        return "CRITICAL"
    
    # assuming user.profile.status exists
    if hasattr(user, 'profile') and user.profile.status == "PREMIUM":
        return "HIGH"
    
    return "NORMAL"


# Main function to create notification
def create_notification(event, user_id, data):
    user = User.objects.get(id=user_id)

    templates = NotificationTemplate.objects.filter(event_type=event)
    prefs, _ = NotificationPreference.objects.get_or_create(user=user)

    priority = get_priority(event, user)

    for template in templates:
        if template.channel == "EMAIL" and not prefs.email_enabled:
            continue
        if template.channel == "IN_APP" and not prefs.in_app_enabled:
            continue

        message = render_template(template.body, data)

        Notification.objects.create(
            user=user,
            event_type=event,
            message=message,
            channel=template.channel,
            priority=priority
        )