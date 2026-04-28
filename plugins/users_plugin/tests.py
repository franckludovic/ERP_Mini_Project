from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import User


class UserModelTest(TestCase):
    """Tests for User model"""
    
    def test_create_user(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            role='customer',
            grade='3rd'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.role, 'customer')
        self.assertEqual(user.grade, '3rd')
        self.assertEqual(user.transaction_count, 0)
        self.assertEqual(user.total_spent, 0)
    
    def test_default_role(self):
        user = User.objects.create_user(
            username='defaultuser',
            email='default@example.com',
            password='pass123'
        )
        self.assertEqual(user.role, 'customer')
        self.assertEqual(user.grade, '3rd')


class RegisterAPITest(APITestCase):
    """Tests for user registration API"""
    
    def test_register_success(self):
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'StrongPass123!',
            'password_confirm': 'StrongPass123!',
            'first_name': 'John',
            'last_name': 'Doe',
            'grade': '2nd'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('tokens', response.data)
        self.assertIn('user', response.data)
    
    def test_register_password_mismatch(self):
        url = reverse('register')
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'Pass123!',
            'password_confirm': 'DifferentPass!',
            'grade': '2nd'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_duplicate_username(self):
        User.objects.create_user(
            username='existing',
            email='existing@example.com',
            password='Pass123!'
        )
        url = reverse('register')
        data = {
            'username': 'existing',
            'email': 'another@example.com',
            'password': 'Pass123!',
            'password_confirm': 'Pass123!',
            'grade': '2nd'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class LoginAPITest(APITestCase):
    """Tests for user login API"""
    
    def setUp(self):
        self.user = User.objects.create_user(
    
            email='login@example.com',
            password='LoginPass123!'
        )
    
    def test_login_success(self):
        url = reverse('login')
        data = {
            'Email': 'login@example.com',
            'password': 'LoginPass123!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('user', response.data)
    
    def test_login_invalid_credentials(self):
        url = reverse('login')
        data = {
            'Email': 'login@example.com',
            'password': 'WrongPassword!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_nonexistent_user(self):
        url = reverse('login')
        data = {
            'Email': 'nonexistent@example.com',
            'password': 'Pass123!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ProfileAPITest(APITestCase):
    """Tests for user profile API"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='profileuser',
            email='profile@example.com',
            password='ProfilePass123!',
            role='customer',
            grade='1st'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_get_profile(self):
        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'profileuser')
    
    def test_update_profile(self):
        url = reverse('profile')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
    
    def test_unauthenticated_profile_access(self):
        self.client.force_authenticate(user=None)
        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class ChangePasswordAPITest(APITestCase):
    """Tests for change password API"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='passworduser',
            email='password@example.com',
            password='OldPass123!'
        )
        self.client.force_authenticate(user=self.user)
    
    def test_change_password_success(self):
        url = reverse('change-password')
        data = {
            'old_password': 'OldPass123!',
            'new_password': 'NewPass123!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPass123!'))
    
    def test_change_password_wrong_old(self):
        url = reverse('change-password')
        data = {
            'old_password': 'WrongPass!',
            'new_password': 'NewPass123!'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PremiumStatusTest(APITestCase):
    """Tests for premium status calculation"""
    
    def test_non_premium_user(self):
        user = User.objects.create_user(
            username='regular',
            email='regular@example.com',
            password='Pass123!',
            transaction_count=3,
            total_spent=500000
        )
        self.client.force_authenticate(user=user)
        url = reverse('profile')
        response = self.client.get(url)
        self.assertFalse(response.data['is_premium'])
    
    def test_premium_user(self):
        user = User.objects.create_user(
            username='premium',
            email='premium@example.com',
            password='Pass123!',
            transaction_count=7,
            total_spent=3000000
        )
        self.client.force_authenticate(user=user)
        url = reverse('profile')
        response = self.client.get(url)
        self.assertTrue(response.data['is_premium'])
