# from rest_framework import serializers
# from django.contrib.auth import get_user_model
# from django.contrib.auth.password_validation import validate_password
# from .models import User

# User = get_user_model()


# class UserSerializer(serializers.ModelSerializer):
#     """Serializer for User model - for admin/listing"""
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'email', 'first_name', 'last_name', 
#                   'role', 'grade', 'transaction_count', 'total_spent', 
#                   'date_joined', 'is_active']
#         read_only_fields = ['id', 'transaction_count', 'total_spent', 'date_joined']


# class RegisterSerializer(serializers.ModelSerializer):
#     """Serializer for user registration"""
#     password = serializers.CharField(write_only=True, validators=[validate_password])
#     password_confirm = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = ['username', 'email', 'password', 'password_confirm', 
#                   'first_name', 'last_name', 'grade']

#     def validate(self, attrs):
#         if attrs['password'] != attrs['password_confirm']:
#             raise serializers.ValidationError({"password": "Passwords don't match"})
#         return attrs

#     def create(self, validated_data):
#         validated_data.pop('password_confirm')
#         user = User.objects.create_user(**validated_data)
#         return user


# class LoginSerializer(serializers.Serializer):
#     """Serializer for user login"""
#     Email = serializers.CharField()
#     password = serializers.CharField(write_only=True)


# class ProfileSerializer(serializers.ModelSerializer):
#     """Serializer for user profile - includes computed premium status"""
#     is_premium = serializers.SerializerMethodField()

#     class Meta:
#         model = User
#         fields = ['id', 'username', 'email', 'first_name', 'last_name', 
#                   'role', 'grade', 'transaction_count', 'total_spent', 
#                   'is_premium', 'date_joined']
#         read_only_fields = ['id', 'username', 'email', 'transaction_count', 
#                            'total_spent', 'date_joined']

#     def get_is_premium(self, obj):
#         """Check if user qualifies as premium (7+ orders, 3,000,000+ XAF)"""
#         return obj.transaction_count >= 7 and obj.total_spent >= 3000000


# class UserUpdateSerializer(serializers.ModelSerializer):
#     """Serializer for updating user profile"""
#     class Meta:
#         model = User
#         fields = ['first_name', 'last_name', 'email']

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'grade', 'transaction_count', 'total_spent',
            'date_joined', 'is_active',
        ]
        read_only_fields = ['id', 'transaction_count', 'total_spent', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'grade',
        ]

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value.lower()

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Passwords don't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class ProfileSerializer(serializers.ModelSerializer):
    is_premium = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'grade', 'transaction_count', 'total_spent',
            'is_premium', 'date_joined',
        ]
        read_only_fields = [
            'id', 'username', 'email', 'transaction_count',
            'total_spent', 'date_joined',
        ]

    def get_is_premium(self, obj):
        return obj.is_premium()


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exclude(pk=self.instance.pk).exists():
            raise serializers.ValidationError("This email is already in use.")
        return value.lower()


class AdminUserCreateSerializer(serializers.ModelSerializer):
    """Serializer for Admin to create users with specific roles"""
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'first_name',
            'last_name', 'role', 'grade'
        ]

    def create(self, validated_data):
        role = validated_data.get('role', 'customer')
        if role != 'customer':
            validated_data['grade'] = None
        return User.objects.create_user(**validated_data)