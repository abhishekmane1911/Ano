from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APITestCase
from rest_framework import status
import uuid

User = get_user_model()


class UserModelTest(TestCase):
    """Test custom User model"""
    
    def setUp(self):
        self.valid_email = 'test@iiti.ac.in'
        self.invalid_email = 'test@gmail.com'
    
    def test_create_user_with_valid_email(self):
        """Test creating user with valid IIT Indore email"""
        user = User.objects.create_user(
            email=self.valid_email,
            username='testuser',
            password='testpass123'
        )
        self.assertEqual(user.email, self.valid_email)
        self.assertFalse(user.is_verified)
        self.assertIsInstance(user.id, uuid.UUID)
        self.assertIsInstance(user.verification_token, uuid.UUID)
    
    def test_password_is_hashed(self):
        """Test that password is hashed using Argon2"""
        user = User.objects.create_user(
            email=self.valid_email,
            username='testuser',
            password='testpass123'
        )
        self.assertNotEqual(user.password, 'testpass123')
        self.assertTrue(user.password.startswith('argon2'))


class RegistrationAPITest(APITestCase):
    """Test user registration endpoint"""
    
    def setUp(self):
        self.url = '/api/auth/register/'
        self.valid_data = {
            'email': 'newuser@iiti.ac.in',
            'username': 'newuser',
            'password': 'SecurePass123!',
            'password_confirm': 'SecurePass123!'
        }
    
    def test_register_with_valid_data(self):
        """Test registration with valid IIT Indore email"""
        response = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertEqual(User.objects.count(), 1)
        
        user = User.objects.first()
        self.assertEqual(user.email, self.valid_data['email'])
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_verified)
    
    def test_register_with_invalid_email_domain(self):
        """Test registration with non-IIT Indore email"""
        invalid_data = self.valid_data.copy()
        invalid_data['email'] = 'test@gmail.com'
        
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
    
    def test_register_with_mismatched_passwords(self):
        """Test registration with mismatched passwords"""
        invalid_data = self.valid_data.copy()
        invalid_data['password_confirm'] = 'DifferentPass123!'
        
        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
    
    def test_register_with_duplicate_email(self):
        """Test registration with already registered email"""
        User.objects.create_user(
            email=self.valid_data['email'],
            username='existinguser',
            password='pass123'
        )
        
        response = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class EmailVerificationAPITest(APITestCase):
    """Test email verification endpoint"""
    
    def setUp(self):
        self.url = '/api/auth/verify-email/'
        self.user = User.objects.create_user(
            email='test@iiti.ac.in',
            username='testuser',
            password='testpass123'
        )
        self.user.is_active = False
        self.user.save()
    
    def test_verify_email_with_valid_token(self):
        """Test email verification with valid token"""
        response = self.client.post(
            self.url,
            {'token': str(self.user.verification_token)},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_verified)
        self.assertTrue(self.user.is_active)
    
    def test_verify_email_with_invalid_token(self):
        """Test email verification with invalid token"""
        response = self.client.post(
            self.url,
            {'token': str(uuid.uuid4())},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_verified)
        self.assertFalse(self.user.is_active)


class LoginAPITest(APITestCase):
    """Test login endpoint"""
    
    def setUp(self):
        self.url = '/api/auth/login/'
        self.user = User.objects.create_user(
            email='test@iiti.ac.in',
            username='testuser',
            password='testpass123'
        )
        self.user.is_verified = True
        self.user.is_active = True
        self.user.save()
    
    def test_login_with_valid_credentials(self):
        """Test login with valid credentials"""
        response = self.client.post(
            self.url,
            {'email': 'test@iiti.ac.in', 'password': 'testpass123'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertIn('refresh_token', response.cookies)
    
    def test_login_with_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post(
            self.url,
            {'email': 'test@iiti.ac.in', 'password': 'wrongpass'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_with_unverified_account(self):
        """Test login with unverified account"""
        self.user.is_active = False
        self.user.save()
        
        response = self.client.post(
            self.url,
            {'email': 'test@iiti.ac.in', 'password': 'testpass123'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenRefreshAPITest(APITestCase):
    """Test token refresh endpoint"""
    
    def setUp(self):
        self.url = '/api/auth/refresh/'
        self.user = User.objects.create_user(
            email='test@iiti.ac.in',
            username='testuser',
            password='testpass123'
        )
        self.user.is_verified = True
        self.user.is_active = True
        self.user.save()
        
        # Login to get tokens
        login_response = self.client.post(
            '/api/auth/login/',
            {'email': 'test@iiti.ac.in', 'password': 'testpass123'},
            format='json'
        )
        self.refresh_token = login_response.data['refresh']
    
    def test_refresh_token_with_valid_token(self):
        """Test refreshing access token with valid refresh token"""
        response = self.client.post(
            self.url,
            {'refresh': self.refresh_token},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_refresh_token_without_token(self):
        """Test refresh without providing token (no cookie, no body)"""
        # Create a new client without cookies
        new_client = self.client_class()
        response = new_client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RateLimitTest(APITestCase):
    """Test rate limiting middleware"""
    
    def setUp(self):
        self.url = '/api/auth/login/'
        cache.clear()
    
    def tearDown(self):
        cache.clear()
    
    def test_rate_limiting_on_failed_logins(self):
        """Test that rate limiting blocks after multiple failed attempts"""
        # Make 5 failed login attempts
        for i in range(5):
            response = self.client.post(
                self.url,
                {'email': 'test@iiti.ac.in', 'password': 'wrongpass'},
                format='json'
            )
            self.assertIn(response.status_code, [400, 401])
        
        # 6th attempt should be rate limited
        response = self.client.post(
            self.url,
            {'email': 'test@iiti.ac.in', 'password': 'wrongpass'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)


class LogoutAPITest(APITestCase):
    """Test logout endpoint"""
    
    def setUp(self):
        self.url = '/api/auth/logout/'
        self.user = User.objects.create_user(
            email='test@iiti.ac.in',
            username='testuser',
            password='testpass123'
        )
        self.user.is_verified = True
        self.user.is_active = True
        self.user.save()
        
        # Login to get tokens
        login_response = self.client.post(
            '/api/auth/login/',
            {'email': 'test@iiti.ac.in', 'password': 'testpass123'},
            format='json'
        )
        self.access_token = login_response.data['access']
        self.refresh_token = login_response.data['refresh']
    
    def test_logout_with_valid_token(self):
        """Test logout with valid refresh token"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(
            self.url,
            {'refresh': self.refresh_token},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)



class PasswordResetTokenTest(TestCase):
    """Test password reset token functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@iiti.ac.in',
            username='testuser',
            password='testpass123'
        )
        self.user.is_verified = True
        self.user.is_active = True
        self.user.save()
    
    def test_generate_password_reset_token(self):
        """Test generating password reset token"""
        token = self.user.generate_password_reset_token()
        
        self.assertIsNotNone(token)
        self.assertIsInstance(token, uuid.UUID)
        self.assertIsNotNone(self.user.password_reset_token)
        self.assertIsNotNone(self.user.password_reset_token_created)
    
    def test_password_reset_token_is_valid(self):
        """Test that newly generated token is valid"""
        self.user.generate_password_reset_token()
        self.assertTrue(self.user.is_password_reset_token_valid())
    
    def test_clear_password_reset_token(self):
        """Test clearing password reset token"""
        self.user.generate_password_reset_token()
        self.user.clear_password_reset_token()
        
        self.assertIsNone(self.user.password_reset_token)
        self.assertIsNone(self.user.password_reset_token_created)


class PasswordResetRequestAPITest(APITestCase):
    """Test password reset request endpoint"""
    
    def setUp(self):
        self.url = '/api/auth/password-reset/'
        self.user = User.objects.create_user(
            email='test@iiti.ac.in',
            username='testuser',
            password='testpass123'
        )
        self.user.is_verified = True
        self.user.is_active = True
        self.user.save()
    
    def test_password_reset_request_with_valid_email(self):
        """Test password reset request with valid email"""
        response = self.client.post(
            self.url,
            {'email': 'test@iiti.ac.in'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Check that token was generated
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.password_reset_token)
    
    def test_password_reset_request_with_nonexistent_email(self):
        """Test password reset request with non-existent email (should still return success)"""
        response = self.client.post(
            self.url,
            {'email': 'nonexistent@iiti.ac.in'},
            format='json'
        )
        # Should return success to prevent email enumeration
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_password_reset_request_with_invalid_domain(self):
        """Test password reset request with invalid email domain"""
        response = self.client.post(
            self.url,
            {'email': 'test@gmail.com'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmAPITest(APITestCase):
    """Test password reset confirmation endpoint"""
    
    def setUp(self):
        self.url = '/api/auth/password-reset-confirm/'
        self.user = User.objects.create_user(
            email='test@iiti.ac.in',
            username='testuser',
            password='oldpass123'
        )
        self.user.is_verified = True
        self.user.is_active = True
        self.user.save()
        
        self.reset_token = self.user.generate_password_reset_token()
    
    def test_password_reset_confirm_with_valid_token(self):
        """Test password reset confirmation with valid token"""
        response = self.client.post(
            self.url,
            {
                'token': str(self.reset_token),
                'password': 'NewSecurePass123!',
                'password_confirm': 'NewSecurePass123!'
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewSecurePass123!'))
        
        # Verify token was cleared
        self.assertIsNone(self.user.password_reset_token)
    
    def test_password_reset_confirm_with_invalid_token(self):
        """Test password reset confirmation with invalid token"""
        response = self.client.post(
            self.url,
            {
                'token': str(uuid.uuid4()),
                'password': 'NewSecurePass123!',
                'password_confirm': 'NewSecurePass123!'
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_password_reset_confirm_with_mismatched_passwords(self):
        """Test password reset confirmation with mismatched passwords"""
        response = self.client.post(
            self.url,
            {
                'token': str(self.reset_token),
                'password': 'NewSecurePass123!',
                'password_confirm': 'DifferentPass123!'
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class EmailServiceTest(TestCase):
    """Test email service functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@iiti.ac.in',
            username='testuser',
            password='testpass123'
        )
    
    def test_verification_email_task_exists(self):
        """Test that verification email task is importable"""
        from authentication.tasks import send_verification_email
        self.assertIsNotNone(send_verification_email)
    
    def test_password_reset_email_task_exists(self):
        """Test that password reset email task is importable"""
        from authentication.tasks import send_password_reset_email
        self.assertIsNotNone(send_password_reset_email)
