from django.urls import path
from plugins.orders_plugin import views as order_views
from plugins.notifications import views as notif_views

urlpatterns = [
    path('overview/', order_views.customer_dashboard_view, name='customer_overview'),
    path('history/', order_views.order_history_view, name='customer_history'),
    path('notifications/', notif_views.notifications_page, name='customer_notifications'),
]
