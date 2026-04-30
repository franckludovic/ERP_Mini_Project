from django.urls import path
from . import views
from plugins.notifications import views as notif_views

urlpatterns = [
    path('production/', views.production_page, name='pm_production'),
    path('ledger/', views.ledger_page, name='pm_ledger'),
    path('history/', views.history_page, name='pm_history'),
    path('notifications/', notif_views.notifications_page, name='pm_notifications'),
]
