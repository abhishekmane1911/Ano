"""
Tests for admin dashboard API endpoints
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

from authentication.models import User
from profiles.models import Profile
from reports.models import Report
from chat.models import Chatroom, Message
from matchmaking.models import Match


class AdminDashboardTestCase(TestCase):
    """Test cases for admin dashboard endpoints"""
    
    def setUp(self):
        """Set up test data"""
        # Create admin user
        self.admin_user = User.objects.create_user(
            email='admin@iiti.ac.in',
            username='admin',
            password='adminpass123',
            is_staff=True,
            is_superuser=True,
            is_verified=True
        )
        
        # Create regular users
        self.user1 = User.objects.create_user(
            email='user1@iiti.ac.in',
            username='user1',
            password='pass123',
            is_verified=True
        )
        self.user2 = User.objects.create_user(
            email='user2@iiti.ac.in',
            username='user2',
            password='pass123',
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
        
        # Create reports
        self.report1 = Report.objects.create(
            reporter=self.profile1,
            reported=self.profile2,
            reason='harassment',
            description='Test harassment report',
            status='pending'
        )
        self.report2 = Report.objects.create(
            reporter=self.profile2,
            reported=self.profile1,
            reason='spam',
            description='Test spam report',
            status='reviewed'
        )
        
        # Create chatroom
        self.chatroom = Chatroom.objects.create(
            name='Test Chatroom',
            description='Test chatroom for testing',
            is_active=True
        )
        
        # Create messages
        self.message1 = Message.objects.create(
            chatroom=self.chatroom,
            sender=self.profile1,
            content='Test message 1',
            message_type='text'
        )
        
        # Create match
        self.match = Match.objects.create(
            profile1=self.profile1,
            profile2=self.profile2,
            is_active=True
        )
        
        # Set up API client
        self.client = APIClient()
    
    def test_list_reports_requires_admin(self):
        """Test that listing reports requires admin authentication"""
        url = reverse('admin-list-reports')
        
        # Unauthenticated request
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Regular user request
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Admin request
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_list_reports_returns_anonymous_ids(self):
        """Test that reports list uses anonymous IDs only"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin-list-reports')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that response contains anonymous IDs
        results = response.data['results']
        self.assertGreater(len(results), 0)
        
        for report in results:
            self.assertIn('reporter_anonymous_id', report)
            self.assertIn('reported_anonymous_id', report)
            # Ensure no user email addresses are exposed (field names are OK)
            # Check that actual email values are not present
            self.assertNotIn('@iiti.ac.in', str(report))
            # Ensure username field is not in the response
            self.assertNotIn('reporter_username', report)
            self.assertNotIn('reported_username', report)
    
    def test_list_reports_filtering(self):
        """Test filtering reports by status"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin-list-reports')
        
        # Filter by pending status
        response = self.client.get(url, {'status': 'pending'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        
        # All results should have pending status
        for report in results:
            self.assertEqual(report['status'], 'pending')
    
    def test_update_report_status(self):
        """Test updating report status"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin-update-report', kwargs={'report_id': self.report1.id})
        
        data = {'status': 'reviewed'}
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'reviewed')
        
        # Verify database was updated
        self.report1.refresh_from_db()
        self.assertEqual(self.report1.status, 'reviewed')
        self.assertIsNotNone(self.report1.reviewed_by)
        self.assertIsNotNone(self.report1.reviewed_at)
    
    def test_get_user_detail_uses_anonymous_id(self):
        """Test getting user details using anonymous ID"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin-user-detail', kwargs={'anonymous_id': self.profile1.anonymous_id})
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that response contains anonymous ID but not email
        self.assertEqual(str(response.data['anonymous_id']), str(self.profile1.anonymous_id))
        self.assertNotIn('email', response.data)
        self.assertNotIn('username', response.data)
        
        # Check that statistics are included
        self.assertIn('reports_received_count', response.data)
        self.assertIn('messages_sent_count', response.data)
        self.assertIn('matches_count', response.data)
    
    def test_ban_user(self):
        """Test banning a user"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin-ban-user', kwargs={'anonymous_id': self.profile1.anonymous_id})
        
        data = {'reason': 'Violation of terms'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Verify user is deactivated
        self.user1.refresh_from_db()
        self.assertFalse(self.user1.is_active)
    
    def test_broadcast_message_to_all_chatrooms(self):
        """Test broadcasting message to all chatrooms"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin-broadcast')
        
        data = {'content': 'Important announcement'}
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('chatrooms_count', response.data)
        self.assertGreater(response.data['chatrooms_count'], 0)
        
        # Verify message was created
        broadcast_messages = Message.objects.filter(
            message_type='system',
            content__contains='ADMIN BROADCAST'
        )
        self.assertGreater(broadcast_messages.count(), 0)
    
    def test_broadcast_message_to_specific_chatroom(self):
        """Test broadcasting message to specific chatroom"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin-broadcast')
        
        data = {
            'content': 'Chatroom announcement',
            'chatroom_id': str(self.chatroom.id)
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['chatrooms_count'], 1)
    
    def test_get_platform_metrics(self):
        """Test getting platform metrics"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin-metrics')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that all expected metrics are present
        expected_metrics = [
            'active_users_today',
            'active_users_week',
            'total_users',
            'total_profiles',
            'total_messages_today',
            'total_messages_week',
            'total_messages',
            'total_matches',
            'total_reports_pending',
            'total_reports',
            'total_chatrooms',
        ]
        
        for metric in expected_metrics:
            self.assertIn(metric, response.data)
            self.assertIsInstance(response.data[metric], int)
    
    def test_platform_metrics_accuracy(self):
        """Test that platform metrics return accurate counts"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('admin-metrics')
        
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify some counts
        self.assertEqual(response.data['total_profiles'], 2)
        self.assertEqual(response.data['total_matches'], 1)
        self.assertEqual(response.data['total_reports'], 2)
        self.assertEqual(response.data['total_reports_pending'], 1)
        self.assertEqual(response.data['total_chatrooms'], 1)
