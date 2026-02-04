from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from profiles.models import Profile
from .models import Swipe, Match

User = get_user_model()


class MatchmakingTestCase(TestCase):
    """Test cases for matchmaking functionality"""
    
    def setUp(self):
        """Set up test data"""
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
            age=22,
            interests=['coding', 'music'],
            hobbies=['reading'],
            relationship_intent='friendship',
            personality_tags=['introverted']
        )
        self.profile2 = Profile.objects.create(
            user=self.user2,
            age=23,
            interests=['sports', 'movies'],
            hobbies=['gaming'],
            relationship_intent='dating',
            personality_tags=['extroverted']
        )
        self.profile3 = Profile.objects.create(
            user=self.user3,
            age=21,
            interests=['art', 'music'],
            hobbies=['painting'],
            relationship_intent='casual',
            personality_tags=['creative']
        )
        
        self.client = APIClient()
    
    def test_get_profiles_for_swiping(self):
        """Test getting profiles for swiping"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/matchmaking/profiles/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return 2 profiles (user2 and user3, excluding own profile)
        self.assertEqual(len(response.data), 2)
    
    def test_swipe_left(self):
        """Test swiping left on a profile"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post('/api/matchmaking/swipe/', {
            'swiped': str(self.profile2.id),
            'direction': 'left'
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['is_match'], False)
        
        # Verify swipe was recorded
        swipe = Swipe.objects.get(swiper=self.profile1, swiped=self.profile2)
        self.assertEqual(swipe.direction, 'left')
    
    def test_swipe_right_no_match(self):
        """Test swiping right without mutual match"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post('/api/matchmaking/swipe/', {
            'swiped': str(self.profile2.id),
            'direction': 'right'
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['is_match'], False)
        
        # Verify swipe was recorded
        swipe = Swipe.objects.get(swiper=self.profile1, swiped=self.profile2)
        self.assertEqual(swipe.direction, 'right')
    
    def test_mutual_match_creation(self):
        """Test that mutual right swipes create a match"""
        # User1 swipes right on User2
        self.client.force_authenticate(user=self.user1)
        response1 = self.client.post('/api/matchmaking/swipe/', {
            'swiped': str(self.profile2.id),
            'direction': 'right'
        })
        self.assertEqual(response1.data['is_match'], False)
        
        # User2 swipes right on User1 - should create match
        self.client.force_authenticate(user=self.user2)
        response2 = self.client.post('/api/matchmaking/swipe/', {
            'swiped': str(self.profile1.id),
            'direction': 'right'
        })
        
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response2.data['is_match'], True)
        self.assertIn('match', response2.data)
        
        # Verify match was created
        match = Match.objects.filter(
            profile1=self.profile2,
            profile2=self.profile1
        ).first()
        self.assertIsNotNone(match)
        self.assertTrue(match.is_active)
    
    def test_profile_exclusion_after_swipe(self):
        """Test that swiped profiles don't appear again"""
        self.client.force_authenticate(user=self.user1)
        
        # Get initial profiles
        response1 = self.client.get('/api/matchmaking/profiles/')
        initial_count = len(response1.data)
        
        # Swipe on profile2
        self.client.post('/api/matchmaking/swipe/', {
            'swiped': str(self.profile2.id),
            'direction': 'left'
        })
        
        # Get profiles again
        response2 = self.client.get('/api/matchmaking/profiles/')
        
        # Should have one less profile
        self.assertEqual(len(response2.data), initial_count - 1)
        
        # Profile2 should not be in the list
        profile_anonymous_ids = [p['anonymous_id'] for p in response2.data]
        self.assertNotIn(str(self.profile2.anonymous_id), profile_anonymous_ids)
    
    def test_list_matches(self):
        """Test listing user's matches"""
        # Create a match
        match = Match.objects.create(
            profile1=self.profile1,
            profile2=self.profile2
        )
        
        self.client.force_authenticate(user=self.user1)
        response = self.client.get('/api/matchmaking/matches/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], str(match.id))
    
    def test_match_detail(self):
        """Test getting match details"""
        match = Match.objects.create(
            profile1=self.profile1,
            profile2=self.profile2
        )
        
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/matchmaking/matches/{match.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(match.id))
        self.assertIn('other_profile', response.data)
    
    def test_match_detail_unauthorized(self):
        """Test that users can't access matches they're not part of"""
        match = Match.objects.create(
            profile1=self.profile1,
            profile2=self.profile2
        )
        
        # User3 tries to access match between user1 and user2
        self.client.force_authenticate(user=self.user3)
        response = self.client.get(f'/api/matchmaking/matches/{match.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_send_match_message(self):
        """Test sending a message in a match chat"""
        match = Match.objects.create(
            profile1=self.profile1,
            profile2=self.profile2
        )
        
        self.client.force_authenticate(user=self.user1)
        response = self.client.post(
            f'/api/matchmaking/matches/{match.id}/messages/send/',
            {
                'content': 'Hello!',
                'message_type': 'text'
            }
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'Hello!')
        self.assertEqual(response.data['sender_anonymous_id'], str(self.profile1.anonymous_id))
    
    def test_get_match_messages(self):
        """Test retrieving messages from a match chat"""
        from chat.models import Message
        
        match = Match.objects.create(
            profile1=self.profile1,
            profile2=self.profile2
        )
        
        # Create some messages
        Message.objects.create(
            match=match,
            sender=self.profile1,
            content='Hello!',
            message_type='text'
        )
        Message.objects.create(
            match=match,
            sender=self.profile2,
            content='Hi there!',
            message_type='text'
        )
        
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f'/api/matchmaking/matches/{match.id}/messages/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Response should be paginated
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_cannot_swipe_on_self(self):
        """Test that users cannot swipe on their own profile"""
        self.client.force_authenticate(user=self.user1)
        response = self.client.post('/api/matchmaking/swipe/', {
            'swiped': str(self.profile1.id),
            'direction': 'right'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_cannot_swipe_twice(self):
        """Test that users cannot swipe on the same profile twice"""
        self.client.force_authenticate(user=self.user1)
        
        # First swipe
        response1 = self.client.post('/api/matchmaking/swipe/', {
            'swiped': str(self.profile2.id),
            'direction': 'left'
        })
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Second swipe on same profile
        response2 = self.client.post('/api/matchmaking/swipe/', {
            'swiped': str(self.profile2.id),
            'direction': 'right'
        })
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
