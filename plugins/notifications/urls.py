from django.urls import path
from . import views

urlpatterns = [
    path('send/', views.send_notification),
    path('user/<int:user_id>/', views.user_notifications),
    path('read/<int:notification_id>/', views.mark_as_read),
    path('delete/<int:notification_id>/', views.delete_notification),
    path('mark-all-read/', views.mark_all_read),
    path('unread-count/', views.unread_count),
    path('page/', views.notifications_page, name='notifications_page'),
]