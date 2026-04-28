# from rest_framework import status, generics, permissions
# from rest_framework.response import Response
# from rest_framework.views import APIView
# from rest_framework_simplejwt.tokens import RefreshToken
# from django.contrib.auth import authenticate, get_user_model
# from django.shortcuts import render
# from .serializers import (
#     UserSerializer, RegisterSerializer, LoginSerializer, 
#     ProfileSerializer, UserUpdateSerializer
# )
# # from .models import User

# User = get_user_model()


# # ==================== Role-Based Access Control ====================

# class IsAdminUser(permissions.BasePermission):
#     """Allow only admin users"""
#     def has_permission(self, request, view):
#         return request.user and request.user.is_authenticated and request.user.role == 'admin'


# class IsProductionManager(permissions.BasePermission):
#     """Allow only production manager users"""
#     def has_permission(self, request, view):
#         return request.user and request.user.is_authenticated and request.user.role == 'production_manager'


# class IsAdminOrProductionManager(permissions.BasePermission):
#     """Allow admin or production manager"""
#     def has_permission(self, request, view):
#         return request.user and request.user.is_authenticated and request.user.role in ['admin', 'production_manager']


# class IsCustomer(permissions.BasePermission):
#     """Allow only customer users"""
#     def has_permission(self, request, view):
#         return request.user and request.user.is_authenticated and request.user.role == 'customer'


# # ==================== Views ====================

# class RegisterView(generics.CreateAPIView):
#     """API endpoint for user registration"""
#     queryset = User.objects.all()
#     permission_classes = [permissions.AllowAny]
#     serializer_class = RegisterSerializer

#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()

#         # Generate JWT tokens
#         refresh = RefreshToken.for_user(user)

#         return Response({
#             'user': UserSerializer(user).data,
#             'tokens': {
#                 'refresh': str(refresh),
#                 'access': str(refresh.access_token),
#             }
#         }, status=status.HTTP_201_CREATED)


# class LoginView(APIView):
#     """API endpoint for user login"""
#     permission_classes = [permissions.AllowAny]

#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         # Get email from the validated data
#         email = serializer.validated_data.get('Email')
        
#         # Find user by email
#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             return Response(
#                 {'error': 'Invalid credentials'},
#                 status=status.HTTP_401_UNAUTHORIZED
#             )

#         # Check password
#         if not user.check_password(serializer.validated_data['password']):
#             return Response(
#                 {'error': 'Invalid credentials'},
#                 status=status.HTTP_401_UNAUTHORIZED
#             )

#         if not user.is_active:
#             return Response(
#                 {'error': 'User account is disabled'},
#                 status=status.HTTP_401_UNAUTHORIZED
#             )

#         refresh = RefreshToken.for_user(user)

#         return Response({
#             'user': ProfileSerializer(user).data,
#             'tokens': {
#                 'refresh': str(refresh),
#                 'access': str(refresh.access_token),
#             }
#         })


# class ProfileView(generics.RetrieveUpdateAPIView):
#     """API endpoint for user profile - get and update"""
#     serializer_class = ProfileSerializer

#     def get_object(self):
#         return self.request.user

#     def get_serializer_class(self):
#         if self.request.method in ['PUT', 'PATCH']:
#             return UserUpdateSerializer
#         return ProfileSerializer


# class UserListView(generics.ListAPIView):
#     """API endpoint to list all users - admin only"""
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [IsAdminUser]


# class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
#     """API endpoint for single user - admin only"""
#     queryset = User.objects.all()
#     serializer_class = UserSerializer
#     permission_classes = [IsAdminUser]
#     lookup_field = 'pk'


# class ChangePasswordView(APIView):
#     """API endpoint for changing password - authenticated users"""
#     permission_classes = [permissions.IsAuthenticated]
#     def post(self, request):
#         user = request.user
#         old_password = request.data.get('old_password')
#         new_password = request.data.get('new_password')

#         if not old_password or not new_password:
#             return Response(
#                 {'error': 'Both old_password and new_password are required'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         if not user.check_password(old_password):
#             return Response(
#                 {'error': 'Incorrect old password'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         user.set_password(new_password)
#         user.save()

#         return Response({'message': 'Password changed successfully'})


# class UpgradeToPremiumView(APIView):
#     permission_classes = [IsAdminUser]

#     def post(self, request, user_id):
#         try:
#             user = User.objects.get(pk=user_id)
#         except User.DoesNotExist:
#             return Response({'error': 'User not found'}, status=404)

#         user.transaction_count = 7
#         user.total_spent = 3000000
#         user.save()

#         return Response({
#             'message': f'{user.username} now qualifies as premium',
#             'user': ProfileSerializer(user).data
#         })


# # ==================== Template Views ====================

# def login_template(request):
#     """Render login page with registration form"""
#     return render(request, 'login.html')


# def login_view(request):
#     """Handle user login from form"""
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         password = request.POST.get('password')

#         # Try to find user by email
#         try:
#             user = User.objects.get(email=email)
#         except User.DoesNotExist:
#             return render(request, 'login.html', {
#                 'error': 'Invalid email or password',
#                 'active_tab': 'signin'
#             })

#         # Check password
#         if not user.check_password(password):
#             return render(request, 'login.html', {
#                 'error': 'Invalid email or password',
#                 'active_tab': 'signin'
#             })

#         if not user.is_active:
#             return render(request, 'login.html', {
#                 'error': 'User account is disabled',
#                 'active_tab': 'signin'
#             })

#         # Login successful - set session and redirect to dashboard
#         from django.shortcuts import redirect
#         request.session['user_id'] = user.id
#         request.session['username'] = user.username
#         return redirect('/api/users/dashboard/')

#     return render(request, 'login.html')


# def customer_dashboard_template(request):
#     """Render customer dashboard page with user data"""
#     # Get user from session (set during login)
#     user = None
#     user_id = request.session.get('user_id')
    
#     if user_id:
#         try:
#             user = User.objects.get(pk=user_id)
#         except User.DoesNotExist:
#             pass
    
#     # If no user in session, try to get from query params (for demo)
#     if not user:
#         user_id = request.GET.get('user_id')
#         if user_id:
#             try:
#                 user = User.objects.get(pk=user_id)
#             except User.DoesNotExist:
#                 pass
    
#     # If still no user, show demo data
#     if not user:
#         context = {
#             'user': {
#                 'username': 'Demo User',
#                 'email': 'demo@nexus.com',
#                 'role': 'customer',
#                 'transaction_count': 4,
#                 'total_spent': 2100000,
#                 'is_premium': False,
#                 'grade': '1st Grade',
#             },
#             'order_progress': 57,
#             'spend_progress': 70,
#             'orders': [
#                 {'id': 'ORD-001', 'date': '2026-04-25', 'status': 'Delivered', 'total': 450000},
#                 {'id': 'ORD-002', 'date': '2026-04-20', 'status': 'Shipped', 'total': 320000},
#                 {'id': 'ORD-003', 'date': '2026-04-15', 'status': 'Pending', 'total': 280000},
#             ]
#         }
#     else:
#         # Calculate premium status
#         is_premium = user.transaction_count >= 7 and user.total_spent >= 3000000
        
#         # Calculate progress percentage
#         order_progress = min(int((user.transaction_count or 0) / 7 * 100), 100)
#         spend_progress = min(int((user.total_spent or 0) / 3000000 * 100), 100)
        
#         # Determine grade based on role
#         grade_map = {
#             'customer': '1st Grade',
#             'production_manager': '2nd Grade',
#             'admin': 'Admin',
#         }
#         grade = grade_map.get(user.role, '1st Grade')
        
#         context = {
#             'user': {
#                 'username': user.username,
#                 'email': user.email,
#                 'role': user.role,
#                 'transaction_count': user.transaction_count or 0,
#                 'total_spent': user.total_spent or 0,
#                 'is_premium': is_premium,
#                 'grade': grade,
#             },
#             'order_progress': order_progress,
#             'spend_progress': spend_progress,
#             'orders': [
#                 {'id': 'ORD-001', 'date': '2026-04-25', 'status': 'Delivered', 'total': 450000},
#                 {'id': 'ORD-002', 'date': '2026-04-20', 'status': 'Shipped', 'total': 320000},
#                 {'id': 'ORD-003', 'date': '2026-04-15', 'status': 'Pending', 'total': 280000},
#             ]
#         }
    
#     return render(request, 'customer-dashboard.html', context)


# def profile_settings_view(request):
#     """Render profile settings page"""
#     # Get user from session (set during login)
#     user = None
#     user_id = request.session.get('user_id')
    
#     if user_id:
#         try:
#             user = User.objects.get(pk=user_id)
#         except User.DoesNotExist:
#             pass
    
#     # If no user in session, try query params
#     if not user:
#         user_id = request.GET.get('user_id')
#         if user_id:
#             try:
#                 user = User.objects.get(pk=user_id)
#             except User.DoesNotExist:
#                 pass
    
#     # If still no user, show demo data
#     if not user:
#         user_data = {
#             'username': 'Demo User',
#             'email': 'demo@nexus.com',
#             'role': 'customer',
#             'transaction_count': 4,
#             'total_spent': 2100000,
#             'is_premium': False,
#             'grade': '1st Grade',
#         }
#     else:
#         is_premium = user.transaction_count >= 7 and user.total_spent >= 3000000
#         grade_map = {'customer': '1st Grade', 'production_manager': '2nd Grade', 'admin': 'Admin'}
        
#         user_data = {
#             'id': user.id,
#             'username': user.username,
#             'email': user.email,
#             'role': user.role,
#             'transaction_count': user.transaction_count or 0,
#             'total_spent': user.total_spent or 0,
#             'is_premium': is_premium,
#             'grade': grade_map.get(user.role, '1st Grade'),
#         }
    
#     return render(request, 'profile-settings.html', {'user': user_data})


# def logout_view(request):
#     """Handle user logout"""
#     from django.shortcuts import redirect
#     return redirect('/api/users/login/')


# def register_view(request):
#     """Handle user registration from form"""
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         password2 = request.POST.get('password2')
#         role = request.POST.get('role', 'customer')

#         # Validate passwords match
#         if password != password2:
#             return render(request, 'login.html', {
#                 'error': 'Passwords do not match',
#                 'active_tab': 'register'
#             })

#         # Check if user already exists
#         if User.objects.filter(username=username).exists():
#             return render(request, 'login.html', {
#                 'error': 'Username already exists',
#                 'active_tab': 'register'
#             })

#         if User.objects.filter(email=email).exists():
#             return render(request, 'login.html', {
#                 'error': 'Email already exists',
#                 'active_tab': 'register'
#             })

#         # Create user
#         user = User.objects.create_user(
#             username=username,
#             email=email,
#             password=password,
#             role=role
#         )

#         # Redirect to login with success message
#         return render(request, 'login.html', {
#             'success': 'Account created successfully! Please sign in.',
#             'active_tab': 'signin'
#         })

#     return render(request, 'login.html')

from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    ProfileSerializer, UserUpdateSerializer, AdminUserCreateSerializer
)

User = get_user_model()


# ==================== Permissions ====================

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated
                and request.user.role == 'admin')


class IsProductionManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated
                and request.user.role == 'production_manager')


class IsAdminOrProductionManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated
                and request.user.role in ['admin', 'production_manager'])


class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user and request.user.is_authenticated
                and request.user.role == 'customer')


# ==================== API Views ====================

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.check_password(serializer.validated_data['password']):
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {'error': 'User account is disabled'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            'user': ProfileSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        })


class ProfileView(generics.RetrieveUpdateAPIView):
    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserUpdateSerializer
        return ProfileSerializer


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'pk'


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response(
                {'error': 'Both old_password and new_password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.check_password(old_password):
            return Response(
                {'error': 'Incorrect old password'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            validate_password(new_password, user)
        except ValidationError as e:
            return Response(
                {'error': list(e.messages)},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()
        return Response({'message': 'Password changed successfully'})


class UpgradeToPremiumView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if user.is_premium():
            return Response({
                'message': f'{user.username} is already premium',
                'user': ProfileSerializer(user).data
            })

        return Response({
            'message': (
                f'{user.username} does not yet qualify for premium. '
                f'Needs {max(0, 7 - user.transaction_count)} more orders and '
                f'{max(0, 3_000_000 - int(user.total_spent))} XAF more in spending.'
            ),
            'user': ProfileSerializer(user).data
        }, status=status.HTTP_400_BAD_REQUEST)


class AdminUserCreateView(generics.CreateAPIView):
    """API view for Admins to create users with specific roles"""
    queryset = User.objects.all()
    permission_classes = [IsAdminUser]
    serializer_class = AdminUserCreateSerializer


# ==================== Template Views ====================

def _get_user_context(user):
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'grade': user.get_grade_display(),
        'transaction_count': user.transaction_count,
        'total_spent': user.total_spent,
        'is_premium': user.is_premium(),
        'is_banned': user.is_banned,
        'ban_until': user.ban_until.isoformat() if user.ban_until else None,
    }


def _require_session_user(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    try:
        return User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return None


def login_template(request):
    return render(request, 'login.html')


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return render(request, 'login.html', {
                'error': 'Invalid email or password',
                'active_tab': 'signin'
            })

        if not user.check_password(password):
            return render(request, 'login.html', {
                'error': 'Invalid email or password',
                'active_tab': 'signin'
            })

        if not user.is_active:
            return render(request, 'login.html', {
                'error': 'User account is disabled',
                'active_tab': 'signin'
            })

        from django.contrib.auth import login
        login(request, user)
        request.session['user_id'] = user.id
        request.session['username'] = user.username
        
        # Role-based redirection
        if user.role == 'admin':
            return redirect('order_dashboard')
        elif user.role == 'production_manager':
            return redirect('mrp_dashboard')
        else:
            return redirect('customer_dashboard')

    return render(request, 'login.html')


def logout_view(request):
    from django.contrib.auth import logout
    logout(request)
    request.session.flush()
    return redirect('login-template')


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email', '').lower()
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        # Strict default to 'customer' for public registration
        role = 'customer'

        if password != password2:
            return render(request, 'login.html', {
                'error': 'Passwords do not match',
                'active_tab': 'register'
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'login.html', {
                'error': 'Username already exists',
                'active_tab': 'register'
            })

        if User.objects.filter(email__iexact=email).exists():
            return render(request, 'login.html', {
                'error': 'Email already exists',
                'active_tab': 'register'
            })

        User.objects.create_user(
            username=username, email=email,
            password=password, role=role
        )
        return render(request, 'login.html', {
            'success': 'Account created successfully! Please sign in.',
            'active_tab': 'signin'
        })

    return render(request, 'login.html')


def customer_dashboard_template(request):
    user = _require_session_user(request)

    if not user:
        context = {
            'user': {
                'username': 'Demo User', 'email': 'demo@nexus.com',
                'role': 'customer', 'grade': '1st Grade',
                'transaction_count': 4, 'total_spent': 2100000,
                'is_premium': False,
            },
            'order_progress': 57,
            'spend_progress': 70,
            'orders': [],
        }
    else:
        context = {
            'user': _get_user_context(user),
            'order_progress': min(int(user.transaction_count / 7 * 100), 100),
            'spend_progress': min(int(user.total_spent / 3_000_000 * 100), 100),
            'orders': [],  # wire to: user.orders.order_by('-created_at')[:10]
        }

    return render(request, 'customer-dashboard.html', context)


def profile_settings_view(request):
    user = _require_session_user(request)

    if not user:
        return redirect('login-template')

    return render(request, 'profile-settings.html', {'user': _get_user_context(user)})


def user_management_template(request):
    """Render the User Management HTML page for Admins"""
    admin_user = _require_session_user(request)
    if not admin_user or admin_user.role != 'admin':
        return redirect('login-template')

    users = User.objects.all().order_by('-date_joined')
    user_data = [_get_user_context(u) for u in users]

    return render(request, 'user-management.html', {
        'admin': _get_user_context(admin_user),
        'users': user_data,
        'role_choices': User.ROLE_CHOICES,
        'grade_choices': User.GRADE_CHOICES,
    })

from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import api_view

@api_view(['POST'])
def ban_user(request, user_id):
    user = User.objects.get(pk=user_id)
    duration_days = int(request.data.get('duration', 0))
    user.is_banned = True
    user.ban_until = timezone.now() + timedelta(days=duration_days)
    user.save()
    return Response({'success': True, 'message': f'User banned until {user.ban_until}'})

@api_view(['POST'])
def unban_user(request, user_id):
    user = User.objects.get(pk=user_id)
    user.is_banned = False
    user.ban_until = None
    user.save()
    return Response({'success': True, 'message': 'User unbanned'})

@api_view(['DELETE', 'POST'])
def delete_user(request, user_id):
    user = User.objects.get(pk=user_id)
    user.delete()
    return Response({'success': True, 'message': 'User deleted'})
