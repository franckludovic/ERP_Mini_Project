"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView
from django.views.generic import TemplateView
from plugins.orders_plugin import views as order_views
from django.views.generic import TemplateView, RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='/api/users/login/'), name='root-redirect'),
    path('mrp_dashboard/',    TemplateView.as_view(template_name='mrp_dashboard.html'), name='mrp_dashboard'),
    path('order_dashboard/',     order_views.dashboard_view, name='order_dashboard'),
    path('customer_dashboard/',  order_views.customer_dashboard_view, name='customer_dashboard'),
    path('order_history/',       order_views.order_history_view, name='order_history'),
    path('api/token/',        TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('admin/',            admin.site.urls),
    path('api/users/',        include('plugins.users_plugin.urls')),
    path('api/orders/',       include('plugins.orders_plugin.urls')),
    path('api/notifications/',include('plugins.notifications.urls')),
    path('api/mrp/',          include('plugins.mrp_production_plugin.urls')),
    path('api/inventory/',    include('plugins.inventory_plugin.urls')),

    path('inventory_dashboard/', include('plugins.inventory_plugin.urls_dashboard')),
    path('notifications/', include('plugins.notifications.urls')),
]