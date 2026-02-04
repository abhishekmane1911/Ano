from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from authentication.models import User
from profiles.models import Profile
from .models import Report, Block
from .utils import get_blocked_profile_ids, filter_blocked_profiles, is_blocked


class ReportModelTest(TestCase):
    """Test Report model"""
    
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@iiti.ac.in',
            password='testpass123',
            is_verified=True
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@iiti.ac.in',
            password='testpass123',
            is_verified=True
        )
        
        # Create profiles
        self.profile1 = Profile.objects.create(
            user=self.user1,
            age=20,
            interests=['coding', 'music'],
            hobbies=['reading'],
            relationship_intent='friendship',
            personality_tags=['introverted']
        )
        self.profile2 = Profile.objects.create(
            user=self.user2,
            age=21,
            interests=['sports', 'gaming'],
            hobbies=['cooking'],
            relationship_intent='dating',
            personality_tags=['extroverted']
        )
    
    def test_create_report(self):
        """Test creating a report"""
        report = Report.objects.create(
            reporter=self.profile1,
            reported=self.profile2,
            reason='harassment',
            description='Test harassment report'
        )
        
        self.assertEqual(report.reporter, self.profile1)
        self.assertEqual(report.reported, self.profile2)
        self.assertEqual(report.reason, 'harassment')
        self.assertEqual(report.status, 'pending')
    
    def test_report_string_representation(self):
        """Test report string representation uses anonymous ID"""
        report = Report.objects.create(
            reporter=self.profile1,
            reported=self.profile2,
            reason='spam',
            description='Test spam report'
        )
        
        self.assertIn(str(self.profile1.anonymous_id), str(report))


class BlockModelTest(TestCase):
    """Test Block model"""
    
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@iiti.ac.in',
            password='testpass123',
            is_verified=True
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@iiti.ac.in',
            password='testpass123',
            is_verified=True
        )
        
        # Create profiles
        self.profile1 = Profile.objects.create(
            user=self.user1,
            age=20,
            interests=['coding'],
            hobbies=['reading'],
            relationship_intent='friendship',
            personality_tags=['introverted']
        )
        self.profile2 = Profile.objects.create(
            user=self.user2,
            age=21,
            interests=['sports'],
            hobbies=['cooking'],
            relationship_intent='dating',
            personality_tags=['extroverted']
        )
    
    def test_create_block(self):
        """Test creating a block"""
        block = Block.objects.create(
            blocker=self.profile1,
            blocked=self.profile2
        )
        
        self.assertEqual(block.blocker, self.profile1)
        self.assertEqual(block.blocked, self.profile2)
    
    def test_block_unique_constraint(self):
        """Test that duplicate blocks are prevented"""
        Block.objects.create(
            blocker=self.profile1,
            blocked=self.profile2
        )
        
        # Try to create duplicate block
        with self.assertRaises(Exception):
            Block.objects.create(
                blocker=self.profile1,
                blocked=self.profile2
            )


class ReportAPITest(APITestCase):
    """Test Report API endpoints"""
    
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@iiti.ac.in',
            password='testpass123',
            is_verified=True
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@iiti.ac.in',
            password='testpass123',
            is_verified=True
        )
        
        # Create profiles
        self.profile1 = Profile.objects.create(
            user=self.user1,
            age=20,
            interests=['coding'],
            hobbies=['reading'],
            relationship_intent='friendship',
            personality_tags=['introverted']
        )
        self.profile2 = Profile.objects.create(
            user=self.user2,
            age=21,
            interests=['sports'],
            hobbies=['cooking'],
            relationship_intent='dating',
            personality_tags=['extroverted']
        )
        
        self.client = APIClient()
    
    def test_create_report_authenticated(self):
        """Test creating a report when authenticated"""
        self.client.force_authenticate(user=self.user1)
        
        url = reverse('reports:report-create')
        data = {
            'reported_id': str(self.profile2.anonymous_id),
            'reason': 'harassment',
            'description': 'Test harassment report'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Report.objects.count(), 1)
        
        report = Report.objects.first()
        self.assertEqual(report.reporter, self.profile1)
        self.assertEqual(report.reported, self.profile2)
    
    def test_create_report_unauthenticated(self):
        """Test creating a report when not authenticated"""
        url = reverse('reports:report-create')
        data = {
            'reported_id': str(self.profile2.anonymous_id),
            'reason': 'spam',
            'description': 'Test spam report'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_cannot_report_self(self):
        """Test that users cannot report themselves"""
        self.client.force_authenticate(user=self.user1)
        
        url = reverse('reports:report-create')
        data = {
            'reported_id': str(self.profile1.anonymous_id),
            'reason': 'spam',
            'description': 'Self report'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class BlockAPITest(APITestCase):
    """Test Block API endpoints"""
    
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@iiti.ac.in',
            password='testpass123',
            is_verified=True
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@iiti.ac.in',
            password='testpass123',
            is_verified=True
        )
        
        # Create profiles
        self.profile1 = Profile.objects.create(
            user=self.user1,
            age=20,
            interests=['coding'],
            hobbies=['reading'],
            relationship_intent='friendship',
            personality_tags=['introverted']
        )
        self.profile2 = Profile.objects.create(
            user=self.user2,
            age=21,
            interests=['sports'],
            hobbies=['cooking'],
            relationship_intent='dating',
            personality_tags=['extroverted']
        )
        
        self.client = APIClient()
    
    def test_create_block_authenticated(self):
        """Test blocking a user when authenticated"""
        self.client.force_authenticate(user=self.user1)
        
        url = reverse('reports:block-create')
        data = {
            'blocked_id': str(self.profile2.anonymous_id)
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Block.objects.count(), 1)
        
        block = Block.objects.first()
        self.assertEqual(block.blocker, self.profile1)
        self.assertEqual(block.blocked, self.profile2)
    
    def test_list_blocked_users(self):
        """Test listing blocked users"""
        self.client.force_authenticate(user=self.user1)
        
        # Create a block
        Block.objects.create(
            blocker=self.profile1,
            blocked=self.profile2
        )
        
        url = reverse('reports:blocked-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if response is paginated or not
        if isinstance(response.data, dict) and 'results' in response.data:
            # Paginated response
            self.assertEqual(len(response.data['results']), 1)
            self.assertEqual(response.data['results'][0]['anonymous_id'], str(self.profile2.anonymous_id))
        else:
            # Non-paginated response
            self.assertEqual(len(response.data), 1)
            self.assertEqual(response.data[0]['anonymous_id'], str(self.profile2.anonymous_id))
    
    def test_unblock_user(self):
        """Test unblocking a user"""
        self.client.force_authenticate(user=self.user1)
        
        # Create a block
        Block.objects.create(
            blocker=self.profile1,
            blocked=self.profile2
        )
        
        url = reverse('reports:unblock-user', kwargs={'anonymous_id': self.profile2.anonymous_id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Block.objects.count(), 0)
    
    def test_cannot_block_self(self):
        """Test that users cannot block themselves"""
        self.client.force_authenticate(user=self.user1)
        
        url = reverse('reports:block-create')
        data = {
            'blocked_id': str(self.profile1.anonymous_id)
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class BlockUtilsTest(TestCase):
    """Test blocking utility functions"""
    
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@iiti.ac.in',
            password='testpass123',
            is_verified=True
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@iiti.ac.in',
            password='testpass123',
            is_verified=True
        )
        self.user3 = User.objects.create_user(
            username='user3',
            email='user3@iiti.ac.in',
            password='testpass123',
            is_verified=True
        )
        
        # Create profiles
        self.profile1 = Profile.objects.create(
            user=self.user1,
            age=20,
            interests=['coding'],
            hobbies=['reading'],
            relationship_intent='friendship',
            personality_tags=['introverted']
        )
        self.profile2 = Profile.objects.create(
            user=self.user2,
            age=21,
            interests=['sports'],
            hobbies=['cooking'],
            relationship_intent='dating',
            personality_tags=['extroverted']
        )
        self.profile3 = Profile.objects.create(
            user=self.user3,
            age=22,
            interests=['music'],
            hobbies=['gaming'],
            relationship_intent='casual',
            personality_tags=['creative']
        )
    
    def test_get_blocked_profile_ids(self):
        """Test getting blocked profile IDs"""
        # Profile1 blocks Profile2
        Block.objects.create(blocker=self.profile1, blocked=self.profile2)
        
        blocked_ids = get_blocked_profile_ids(self.profile1)
        
        self.assertIn(self.profile2.id, blocked_ids)
        self.assertNotIn(self.profile3.id, blocked_ids)
    
    def test_get_blocked_profile_ids_bidirectional(self):
        """Test that blocks work both ways"""
        # Profile2 blocks Profile1
        Block.objects.create(blocker=self.profile2, blocked=self.profile1)
        
        # Profile1 should see Profile2 as blocked
        blocked_ids = get_blocked_profile_ids(self.profile1)
        
        self.assertIn(self.profile2.id, blocked_ids)
    
    def test_filter_blocked_profiles(self):
        """Test filtering blocked profiles from queryset"""
        # Profile1 blocks Profile2
        Block.objects.create(blocker=self.profile1, blocked=self.profile2)
        
        queryset = Profile.objects.all()
        filtered = filter_blocked_profiles(queryset, self.profile1)
        
        self.assertIn(self.profile1, filtered)
        self.assertNotIn(self.profile2, filtered)
        self.assertIn(self.profile3, filtered)
    
    def test_is_blocked(self):
        """Test checking if two profiles have a block between them"""
        # No block initially
        self.assertFalse(is_blocked(self.profile1, self.profile2))
        
        # Create block
        Block.objects.create(blocker=self.profile1, blocked=self.profile2)
        
        # Should detect block
        self.assertTrue(is_blocked(self.profile1, self.profile2))
        self.assertTrue(is_blocked(self.profile2, self.profile1))  # Works both ways
