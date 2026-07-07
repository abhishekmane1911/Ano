from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from profiles.models import Profile
from .models import Chatroom, Message, MessageReaction, ReadReceipt
import uuid

User = get_user_model()


class ChatroomAPITestCase(TestCase):
    """Test cases for Chatroom API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@iiti.ac.in',
            password='testpass123',
            is_verified=True
        )
        
        # Create profile for user
        self.profile = Profile.objects.create(
            user=self.user,
            age=20,
            interests=['coding', 'music'],
            hobbies=['reading'],
            relationship_intent='friendship',
            personality_tags=['introverted']
        )
        
        # Create test chatroom
        self.chatroom = Chatroom.objects.create(
            name='Test Chatroom',
            description='A test chatroom',
            created_by=self.user
        )
        
        # Create reputation records for users to have voting privileges
        from reputation.models import UserReputation
        reputation, created = UserReputation.objects.get_or_create(
            user=self.user,
            defaults={
                'reputation_score': 200.0,  # Enough for Sophomore tier (voting privileges)
                'rank_tier': 'Sophomore'
            }
        )
        if not created:
            # Update existing record
            reputation.reputation_score = 200.0
            reputation.rank_tier = 'Sophomore'
            reputation.save()
        
        # Authenticate client
        self.client.force_authenticate(user=self.user)
    
    def test_list_chatrooms(self):
        """Test listing all chatrooms"""
        response = self.client.get('/api/chat/chatrooms/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Chatroom')
    
    def test_get_chatroom_detail(self):
        """Test getting chatroom details"""
        response = self.client.get(f'/api/chat/chatrooms/{self.chatroom.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Chatroom')
        self.assertEqual(response.data['description'], 'A test chatroom')
    
    def test_send_message_to_chatroom(self):
        """Test sending a message to a chatroom"""
        data = {
            'content': 'Hello, world!',
            'message_type': 'text'
        }
        response = self.client.post(
            f'/api/chat/chatrooms/{self.chatroom.id}/send_message/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'Hello, world!')
        self.assertEqual(response.data['message_type'], 'text')
        
        # Verify message was created
        self.assertEqual(Message.objects.count(), 1)
        message = Message.objects.first()
        self.assertEqual(message.content, 'Hello, world!')
        self.assertEqual(message.sender, self.profile)
        self.assertEqual(message.chatroom, self.chatroom)
    
    def test_get_chatroom_messages(self):
        """Test getting paginated messages for a chatroom"""
        # Create some messages
        for i in range(5):
            Message.objects.create(
                chatroom=self.chatroom,
                sender=self.profile,
                content=f'Message {i}',
                message_type='text'
            )
        
        response = self.client.get(f'/api/chat/chatrooms/{self.chatroom.id}/messages/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 5)
    
    def test_send_empty_message_fails(self):
        """Test that sending an empty message fails"""
        data = {
            'content': '',
            'message_type': 'text'
        }
        response = self.client.post(
            f'/api/chat/chatrooms/{self.chatroom.id}/send_message/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class MessageAPITestCase(TestCase):
    """Test cases for Message API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
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
            interests=['music'],
            hobbies=['gaming'],
            relationship_intent='dating',
            personality_tags=['extroverted']
        )
        
        # Create chatroom
        self.chatroom = Chatroom.objects.create(
            name='Test Chatroom',
            description='A test chatroom'
        )
        
        # Create reputation records for users to have voting privileges
        from reputation.models import UserReputation
        reputation1, created = UserReputation.objects.get_or_create(
            user=self.user1,
            defaults={
                'reputation_score': 200.0,  # Enough for Sophomore tier (voting privileges)
                'rank_tier': 'Sophomore'
            }
        )
        if not created:
            # Update existing record
            reputation1.reputation_score = 200.0
            reputation1.rank_tier = 'Sophomore'
            reputation1.save()
            
        reputation2, created = UserReputation.objects.get_or_create(
            user=self.user2,
            defaults={
                'reputation_score': 200.0,  # Enough for Sophomore tier (voting privileges)
                'rank_tier': 'Sophomore'
            }
        )
        if not created:
            # Update existing record
            reputation2.reputation_score = 200.0
            reputation2.rank_tier = 'Sophomore'
            reputation2.save()
        
        # Create message
        self.message = Message.objects.create(
            chatroom=self.chatroom,
            sender=self.profile1,
            content='Original message',
            message_type='text'
        )
        
        # Authenticate as user1
        self.client.force_authenticate(user=self.user1)
    
    def test_edit_message(self):
        """Test editing a message"""
        data = {'content': 'Edited message'}
        response = self.client.put(
            f'/api/chat/messages/{self.message.id}/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['content'], 'Edited message')
        self.assertTrue(response.data['is_edited'])
        
        # Verify in database
        self.message.refresh_from_db()
        self.assertEqual(self.message.content, 'Edited message')
        self.assertTrue(self.message.is_edited)
    
    def test_edit_other_user_message_fails(self):
        """Test that editing another user's message fails"""
        # Authenticate as user2
        self.client.force_authenticate(user=self.user2)
        
        data = {'content': 'Hacked message'}
        response = self.client.put(
            f'/api/chat/messages/{self.message.id}/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_delete_message(self):
        """Test deleting a message (soft delete)"""
        response = self.client.delete(f'/api/chat/messages/{self.message.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # Verify soft delete
        self.message.refresh_from_db()
        self.assertTrue(self.message.is_deleted)
        self.assertEqual(self.message.content, '[Message deleted]')
    
    def test_delete_other_user_message_fails(self):
        """Test that deleting another user's message fails"""
        # Authenticate as user2
        self.client.force_authenticate(user=self.user2)
        
        response = self.client.delete(f'/api/chat/messages/{self.message.id}/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_react_to_message(self):
        """Test adding a reaction to a message"""
        data = {'emoji': '👍'}
        response = self.client.post(
            f'/api/chat/messages/{self.message.id}/react/',
            data
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['emoji'], '👍')
        
        # Verify reaction was created
        self.assertEqual(MessageReaction.objects.count(), 1)
        reaction = MessageReaction.objects.first()
        self.assertEqual(reaction.emoji, '👍')
        self.assertEqual(reaction.profile, self.profile1)
        self.assertEqual(reaction.message, self.message)
    
    def test_duplicate_reaction_returns_existing(self):
        """Test that adding the same reaction twice returns existing"""
        data = {'emoji': '👍'}
        
        # First reaction
        response1 = self.client.post(
            f'/api/chat/messages/{self.message.id}/react/',
            data
        )
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Second reaction (duplicate)
        response2 = self.client.post(
            f'/api/chat/messages/{self.message.id}/react/',
            data
        )
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        # Verify only one reaction exists
        self.assertEqual(MessageReaction.objects.count(), 1)
    
    def test_pin_message(self):
        """Test pinning a message"""
        response = self.client.post(f'/api/chat/messages/{self.message.id}/pin/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_pinned'])
        
        # Verify in database
        self.message.refresh_from_db()
        self.assertTrue(self.message.is_pinned)
    
    def test_unpin_message(self):
        """Test unpinning a message"""
        # First pin it
        self.message.is_pinned = True
        self.message.save()
        
        # Then unpin
        response = self.client.post(f'/api/chat/messages/{self.message.id}/pin/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_pinned'])
        
        # Verify in database
        self.message.refresh_from_db()
        self.assertFalse(self.message.is_pinned)


class MessageModelTestCase(TestCase):
    """Test cases for Message model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@iiti.ac.in',
            password='testpass123',
            is_verified=True
        )
        self.profile = Profile.objects.create(
            user=self.user,
            age=20,
            interests=['coding'],
            hobbies=['reading'],
            relationship_intent='friendship',
            personality_tags=['introverted']
        )
        self.chatroom = Chatroom.objects.create(
            name='Test Chatroom',
            description='A test chatroom'
        )
    
    def test_message_creation(self):
        """Test creating a message"""
        message = Message.objects.create(
            chatroom=self.chatroom,
            sender=self.profile,
            content='Test message',
            message_type='text'
        )
        self.assertIsNotNone(message.id)
        self.assertIsInstance(message.id, uuid.UUID)
        self.assertEqual(message.content, 'Test message')
        self.assertEqual(message.sender, self.profile)
        self.assertFalse(message.is_edited)
        self.assertFalse(message.is_deleted)
        self.assertFalse(message.is_pinned)
    
    def test_message_reaction_creation(self):
        """Test creating a message reaction"""
        message = Message.objects.create(
            chatroom=self.chatroom,
            sender=self.profile,
            content='Test message',
            message_type='text'
        )
        reaction = MessageReaction.objects.create(
            message=message,
            profile=self.profile,
            emoji='👍'
        )
        self.assertIsNotNone(reaction.id)
        self.assertEqual(reaction.emoji, '👍')
        self.assertEqual(reaction.message, message)
        self.assertEqual(reaction.profile, self.profile)
    
    def test_read_receipt_creation(self):
        """Test creating a read receipt"""
        message = Message.objects.create(
            chatroom=self.chatroom,
            sender=self.profile,
            content='Test message',
            message_type='text'
        )
        receipt = ReadReceipt.objects.create(
            message=message,
            profile=self.profile
        )
        self.assertIsNotNone(receipt.id)
        self.assertEqual(receipt.message, message)
        self.assertEqual(receipt.profile, self.profile)
        self.assertIsNotNone(receipt.read_at)
