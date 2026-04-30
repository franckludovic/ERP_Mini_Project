from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.shortcuts import render

from .models import Notification
from .serializers import NotificationSerializer
from .utils import create_notification


# -------------------------
# Swagger parameter
# -------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_notification(request):

    event = request.GET.get('event')
    user = request.user

    create_notification(event, user.id, {})

    return Response({
        "message": "Notification created successfully",
        "user": user.username
    })


# -------------------------
# GET NOTIFICATIONS
# -------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_notifications(request, user_id=None):

    # Use the authenticated user's ID
    # The user_id from URL is allowed to prevent the TypeError, 
    # but we filter by request.user for security.
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)


# -------------------------
# MARK AS READ
# -------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_as_read(request, notification_id):

    try:
        notif = Notification.objects.get(
            id=notification_id,
            user=request.user
        )
    except Notification.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    notif.is_read = True
    notif.save()

    return Response({"message": "Marked as read"})


# -------------------------
# MARK ALL READ
# -------------------------
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_read(request):

    Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True)

    return Response({"message": "All marked as read"})


# -------------------------
# DELETE NOTIFICATION
# -------------------------
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_notification(request, notification_id):

    try:
        notif = Notification.objects.get(
            id=notification_id,
            user=request.user
        )
    except Notification.DoesNotExist:
        return Response({"error": "Not found"}, status=404)

    notif.delete()

    return Response({"message": "Deleted"})


from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.contrib.auth.decorators import login_required

# -------------------------
# HTML PAGE
# -------------------------
@login_required
@xframe_options_sameorigin
def notifications_page(request):
    base_template = 'admin_dashboard/partial.html' if request.headers.get('HX-Request') else 'admin_dashboard/base.html'
    return render(request, "notifications/notifications.html", {
        "user_id": request.user.id,
        "username": request.user.username,
        "base_template": base_template,
    })