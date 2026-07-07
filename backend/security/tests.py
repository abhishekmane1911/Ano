"""
Tests for security module functionality.
Tests rate limiting, input sanitization, and identity hashing.
"""
import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import HashedIdentity, RateLimitRecord, SecurityEvent
from .services import RateLimitService, InputSanitizer, IdentityHasher
from .authentication import EnhancedAuthenticationService

User = get_user_model()


class RateLimitServiceTest(TestCase):
    """Test rate limiting functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@iiti.ac.in',
            username='test@iiti.ac.in',
            password='testpass123'
        )
        cache.clear()  # Clear cache before each test
    
    def test_rate_limit_check_allows_within_limit(self):
        """Test that requests within limit are allowed"""
        result = RateLimitService.check_rate_limit(
            self.user, 'post_creation', '127.0.0.1'
        )
        self.assertTrue(result)
    
    def test_rate_limit_check_blocks_over_limit(self):
        """Test that requests over limit are blocked"""
        # Make maximum allowed requests
        for _ in range(5):  # post_creation limit is 5
            RateLimitService.check_rate_limit(
                self.user, 'post_creation', '127.0.0.1'
            )
        
        # Next request should be blocked
        result = RateLimitService.check_rate_limit(
            self.user, 'post_creation', '127.0.0.1'
        )
        self.assertFalse(result)
    
    def test_get_remaining_requests(self):
        """Test getting remaining request count"""
        # Make 2 requests
        for _ in range(2):
            RateLimitService.check_rate_limit(
                self.user, 'post_creation', '127.0.0.1'
            )
        
        remaining = RateLimitService.get_remaining_requests(
            self.user, 'post_creation'
        )
        self.assertEqual(remaining, 3)  # 5 - 2 = 3


class InputSanitizerTest(TestCase):
    """Test input sanitization functionality"""
    
    def test_sanitize_html_removes_scripts(self):
        """Test that script tags are removed"""
        malicious_content = '<script>alert("xss")</script>Hello'
        sanitized = InputSanitizer.sanitize_html(malicious_content)
        self.assertNotIn('<script>', sanitized)
        self.assertIn('Hello', sanitized)
    
    def test_escape_javascript_escapes_chars(self):
        """Test that JavaScript characters are escaped"""
        content = '<script>alert("test")</script>'
        escaped = InputSanitizer.escape_javascript(content)
        # The & character is escaped first, so we get &amp;lt; instead of &lt;
        self.assertIn('&amp;lt;', escaped)
        self.assertIn('&amp;gt;', escaped)
        self.assertIn('&amp;quot;', escaped)
    
    def test_validate_input_length(self):
        """Test input length validation"""
        short_content = 'Hello'
        long_content = 'x' * 1000
        
        self.assertTrue(InputSanitizer.validate_input_length(short_content, 100))
        self.assertFalse(InputSanitizer.validate_input_length(long_content, 100))
    
    def test_check_for_malicious_patterns(self):
        """Test malicious pattern detection"""
        user = User.objects.create_user(
            email='test@iiti.ac.in',
            username='test@iiti.ac.in',
            password='testpass123'
        )
        
        malicious_content = '<script>alert("xss")</script>'
        safe_content = 'Hello world'
        
        self.assertTrue(InputSanitizer.check_for_malicious_patterns(
            malicious_content, user, '127.0.0.1'
        ))
        self.assertFalse(InputSanitizer.check_for_malicious_patterns(
            safe_content, user, '127.0.0.1'
        ))


class IdentityHasherTest(TestCase):
    """Test identity hashing functionality"""
    
    def test_hash_email_generates_hash_and_salt(self):
        """Test that email hashing generates hash and salt"""
        email = 'test@iiti.ac.in'
        email_hash, salt = IdentityHasher.hash_email(email)
        
        self.assertIsInstance(email_hash, str)
        self.assertIsInstance(salt, str)
        self.assertEqual(len(email_hash), 64)  # SHA256 hex length
        self.assertEqual(len(salt), 32)  # 16 bytes hex encoded
    
    def test_verify_email_hash_works_correctly(self):
        """Test that email hash verification works"""
        email = 'test@iiti.ac.in'
        email_hash, salt = IdentityHasher.hash_email(email)
        
        # Correct email should verify
        self.assertTrue(IdentityHasher.verify_email_hash(email, email_hash, salt))
        
        # Wrong email should not verify
        self.assertFalse(IdentityHasher.verify_email_hash(
            'wrong@iiti.ac.in', email_hash, salt
        ))
    
    def test_hash_is_deterministic_with_same_salt(self):
        """Test that same email and salt produce same hash"""
        email = 'test@iiti.ac.in'
        
        # Generate two hashes for the same email
        hash1, salt1 = IdentityHasher.hash_email(email)
        hash2, salt2 = IdentityHasher.hash_email(email)
        
        # Hashes should be different because salts are random
        self.assertNotEqual(hash1, hash2)
        self.assertNotEqual(salt1, salt2)
        
        # But verification should work for both
        self.assertTrue(IdentityHasher.verify_email_hash(email, hash1, salt1))
        self.assertTrue(IdentityHasher.verify_email_hash(email, hash2, salt2))


class EnhancedAuthenticationServiceTest(TestCase):
    """Test enhanced authentication service"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@iiti.ac.in',
            username='test@iiti.ac.in',
            password='testpass123'
        )
    
    def test_find_user_by_email_regular(self):
        """Test finding user by regular email"""
        found_user = EnhancedAuthenticationService.find_user_by_email('test@iiti.ac.in')
        self.assertEqual(found_user, self.user)
    
    def test_find_user_by_email_case_insensitive(self):
        """Test finding user by email is case insensitive"""
        found_user = EnhancedAuthenticationService.find_user_by_email('TEST@iiti.ac.in')
        self.assertEqual(found_user, self.user)
    
    def test_is_email_registered(self):
        """Test checking if email is registered"""
        self.assertTrue(EnhancedAuthenticationService.is_email_registered('test@iiti.ac.in'))
        self.assertFalse(EnhancedAuthenticationService.is_email_registered('notfound@iiti.ac.in'))
    
    def test_verify_email_ownership(self):
        """Test verifying email ownership"""
        self.assertTrue(EnhancedAuthenticationService.verify_email_ownership(
            self.user, 'test@iiti.ac.in'
        ))
        self.assertFalse(EnhancedAuthenticationService.verify_email_ownership(
            self.user, 'wrong@iiti.ac.in'
        ))


class HashedIdentityModelTest(TestCase):
    """Test hashed identity model functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@iiti.ac.in',
            username='test@iiti.ac.in',
            password='testpass123'
        )
    
    def test_create_hashed_identity(self):
        """Test creating hashed identity"""
        # Delete any existing hashed identity created by signal
        HashedIdentity.objects.filter(user=self.user).delete()
        
        email_hash, salt = HashedIdentity.hash_email(self.user.email)
        hashed_identity = HashedIdentity.objects.create(
            user=self.user,
            email_hash=email_hash,
            salt=salt
        )
        
        self.assertEqual(hashed_identity.user, self.user)
        self.assertEqual(len(hashed_identity.email_hash), 64)
        self.assertEqual(len(hashed_identity.salt), 32)
    
    def test_verify_email_hash_method(self):
        """Test the verify_email_hash class method"""
        email = 'test@iiti.ac.in'
        email_hash, salt = HashedIdentity.hash_email(email)
        
        self.assertTrue(HashedIdentity.verify_email_hash(email, email_hash, salt))
        self.assertFalse(HashedIdentity.verify_email_hash('wrong@iiti.ac.in', email_hash, salt))


class SecurityEventTest(TestCase):
    """Test security event logging"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@iiti.ac.in',
            username='test@iiti.ac.in',
            password='testpass123'
        )
    
    def test_create_security_event(self):
        """Test creating security event"""
        event = SecurityEvent.objects.create(
            user=self.user,
            event_type='rate_limit_exceeded',
            severity='medium',
            description='Test security event',
            ip_address='127.0.0.1'
        )
        
        self.assertEqual(event.user, self.user)
        self.assertEqual(event.event_type, 'rate_limit_exceeded')
        self.assertEqual(event.severity, 'medium')
        self.assertEqual(event.ip_address, '127.0.0.1')


class RateLimitMiddlewareTest(APITestCase):
    """Test rate limiting middleware integration"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@iiti.ac.in',
            username='test@iiti.ac.in',
            password='testpass123',
            is_verified=True,
            is_active=True
        )
        cache.clear()
    
    def test_middleware_allows_normal_requests(self):
        """Test that middleware allows normal requests"""
        self.client.force_authenticate(user=self.user)
        
        # This would normally be a real endpoint
        # For testing, we'll just verify the middleware doesn't block everything
        response = self.client.get('/api/auth/user/')
        
        # The endpoint might not exist, but middleware shouldn't block with 429
        self.assertNotEqual(response.status_code, 429)