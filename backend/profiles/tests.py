from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from io import BytesIO
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
import uuid
from .models import Profile

User = get_user_model()


class ProfileModelTest(TestCase):
    """Test the Profile model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@iiti.ac.in',
            password='testpass123'
        )
    
    def test_profile_creation(self):
        """Test creating a profile with valid data"""
        profile = Profile.objects.create(
            user=self.user,
            age=22,
            interests=['coding', 'music'],
            hobbies=['guitar', 'reading'],
            relationship_intent='friendship',
            personality_tags=['introverted', 'creative']
        )
        
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.age, 22)
        self.assertIsInstance(profile.anonymous_id, uuid.UUID)
        self.assertIsInstance(profile.id, uuid.UUID)
    
    def test_profile_anonymous_id_unique(self):
        """Test that anonymous_id is unique"""
        profile1 = Profile.objects.create(
            user=self.user,
            age=22,
            interests=['coding'],
            hobbies=['guitar'],
            relationship_intent='friendship',
            personality_tags=['introverted']
        )
        
        user2 = User.objects.create_user(
            username='testuser2',
            email='test2@iiti.ac.in',
            password='testpass123'
        )
        
        profile2 = Profile.objects.create(
            user=user2,
            age=23,
            interests=['sports'],
            hobbies=['football'],
            relationship_intent='dating',
            personality_tags=['extroverted']
        )
        
        self.assertNotEqual(profile1.anonymous_id, profile2.anonymous_id)


class ProfileAPITest(APITestCase):
    """Test the Profile API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@iiti.ac.in',
            password='testpass123'
        )
        self.user.is_verified = True
        self.user.save()
        
        # Authenticate the client
        self.client.force_authenticate(user=self.user)
    
    def test_create_profile(self):
        """Test creating a profile via API"""
        data = {
            'age': 22,
            'interests': ['coding', 'music'],
            'hobbies': ['guitar', 'reading'],
            'relationship_intent': 'friendship',
            'personality_tags': ['introverted', 'creative'],
            'bio': 'Test bio'
        }
        
        response = self.client.post('/api/profiles/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('anonymous_id', response.data)
        self.assertEqual(response.data['age'], 22)
        self.assertEqual(response.data['interests'], ['coding', 'music'])
        
        # Verify no personal information is exposed
        self.assertNotIn('user', response.data)
        self.assertNotIn('email', response.data)
    
    def test_create_profile_duplicate(self):
        """Test that creating a duplicate profile fails"""
        Profile.objects.create(
            user=self.user,
            age=22,
            interests=['coding'],
            hobbies=['guitar'],
            relationship_intent='friendship',
            personality_tags=['introverted']
        )
        
        data = {
            'age': 23,
            'interests': ['sports'],
            'hobbies': ['football'],
            'relationship_intent': 'dating',
            'personality_tags': ['extroverted']
        }
        
        response = self.client.post('/api/profiles/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_profile_invalid_age(self):
        """Test creating a profile with invalid age"""
        data = {
            'age': 15,  # Too young
            'interests': ['coding'],
            'hobbies': ['guitar'],
            'relationship_intent': 'friendship',
            'personality_tags': ['introverted']
        }
        
        response = self.client.post('/api/profiles/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_profile_invalid_relationship_intent(self):
        """Test creating a profile with invalid relationship intent"""
        data = {
            'age': 22,
            'interests': ['coding'],
            'hobbies': ['guitar'],
            'relationship_intent': 'invalid_choice',
            'personality_tags': ['introverted']
        }
        
        response = self.client.post('/api/profiles/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_get_own_profile(self):
        """Test retrieving own profile"""
        profile = Profile.objects.create(
            user=self.user,
            age=22,
            interests=['coding', 'music'],
            hobbies=['guitar', 'reading'],
            relationship_intent='friendship',
            personality_tags=['introverted', 'creative']
        )
        
        response = self.client.get('/api/profiles/me/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data['anonymous_id']), str(profile.anonymous_id))
        self.assertEqual(response.data['age'], 22)
        
        # Verify no personal information is exposed
        self.assertNotIn('user', response.data)
        self.assertNotIn('email', response.data)
    
    def test_update_profile(self):
        """Test updating own profile"""
        Profile.objects.create(
            user=self.user,
            age=22,
            interests=['coding'],
            hobbies=['guitar'],
            relationship_intent='friendship',
            personality_tags=['introverted']
        )
        
        update_data = {
            'age': 23,
            'interests': ['coding', 'music', 'sports'],
            'bio': 'Updated bio'
        }
        
        response = self.client.patch('/api/profiles/me/', update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['age'], 23)
        self.assertEqual(response.data['bio'], 'Updated bio')
    
    def test_get_profile_by_anonymous_id(self):
        """Test retrieving a profile by anonymous_id"""
        profile = Profile.objects.create(
            user=self.user,
            age=22,
            interests=['coding', 'music'],
            hobbies=['guitar', 'reading'],
            relationship_intent='friendship',
            personality_tags=['introverted', 'creative']
        )
        
        response = self.client.get(f'/api/profiles/{profile.anonymous_id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.data['anonymous_id']), str(profile.anonymous_id))
        
        # Verify no personal information is exposed
        self.assertNotIn('user', response.data)
        self.assertNotIn('email', response.data)
    
    def test_upload_avatar(self):
        """Test uploading an avatar"""
        Profile.objects.create(
            user=self.user,
            age=22,
            interests=['coding'],
            hobbies=['guitar'],
            relationship_intent='friendship',
            personality_tags=['introverted']
        )
        
        # Create a test image
        image = Image.new('RGB', (100, 100), color='red')
        image_io = BytesIO()
        image.save(image_io, format='JPEG')
        image_io.seek(0)
        
        avatar_file = SimpleUploadedFile(
            "test_avatar.jpg",
            image_io.read(),
            content_type="image/jpeg"
        )
        
        response = self.client.post(
            '/api/profiles/avatar/',
            {'avatar': avatar_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('avatar', response.data)
    
    def test_upload_avatar_invalid_type(self):
        """Test uploading an avatar with invalid file type"""
        Profile.objects.create(
            user=self.user,
            age=22,
            interests=['coding'],
            hobbies=['guitar'],
            relationship_intent='friendship',
            personality_tags=['introverted']
        )
        
        # Create a text file instead of an image
        text_file = SimpleUploadedFile(
            "test.txt",
            b"This is not an image",
            content_type="text/plain"
        )
        
        response = self.client.post(
            '/api/profiles/avatar/',
            {'avatar': text_file},
            format='multipart'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access profile endpoints"""
        self.client.force_authenticate(user=None)
        
        response = self.client.get('/api/profiles/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response = self.client.post('/api/profiles/', {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
