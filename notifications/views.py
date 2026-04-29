from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.shortcuts import render

from .models import Notification
from .serializers import NotificationSerializer
from .utils import create_notification


# -------------------------
# Swagger parameter
# -------------------------
event_param = openapi.Parameter(
    'event',
    openapi.IN_QUERY,
    description="Notification event type (ORDER_CREATED, LOW_STOCK, etc.)",
    type=openapi.TYPE_STRING,
    required=True
)


# -------------------------
# SEND NOTIFICATION (FIXED)
# -------------------------
@swagger_auto_schema(
    methods=['post'],   # 🔥 THIS FIXES YOUR ERROR
    manual_parameters=[event_param]
)
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
def user_notifications(request):

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


# -------------------------
# HTML PAGE
# -------------------------
def notifications_page(request):
    return render(request, "notifications/notifications.html", {
        "user_id": request.user.id,
        "username": request.user.username
    })