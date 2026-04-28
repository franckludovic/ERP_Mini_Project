
from django.urls import path
from .views import (
    RegisterView, LoginView, ProfileView, 
    UserListView, UserDetailView, ChangePasswordView,
    UpgradeToPremiumView, login_template, customer_dashboard_template,
    register_view, login_view, profile_settings_view, logout_view
)

urlpatterns = [
    # Template routes (HTML pages)
    path('login/', login_template, name='login-template'),
    path('login-action/', login_view, name='login-view'),
    path('register/', register_view, name='register-view'),
    path('dashboard/', customer_dashboard_template, name='customer-dashboard'),
    path('settings/', profile_settings_view, name='profile-settings'),
    path('logout/', logout_view, name='logout'),
    
    
    # Auth endpoints
    path('register-api/', RegisterView.as_view(), name='register'),
    path('login-api/', LoginView.as_view(), name='login'),
    
    # User profile
    path('profile/', ProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # Admin endpoints
    path('', UserListView.as_view(), name='user-list'),
    path('<int:pk>/', UserDetailView.as_view(), name='user-detail'),
    path('<int:user_id>/upgrade-premium/', UpgradeToPremiumView.as_view(), name='upgrade-premium'),
]
# orders 
