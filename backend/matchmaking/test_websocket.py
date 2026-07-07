"""
WebSocket tests for match chat functionality
"""
import pytest
import json
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from asgiref.sync import sync_to_async
from profiles.models import Profile
from matchmaking.models import Match, Swipe
from chat.models import Message, ReadReceipt
from matchmaking.routing import websocket_urlpatterns
from chat.middleware import JWTAuthMiddleware
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


class MatchWebSocketTest(TransactionTestCase):
    """Test WebSocket functionality for match chat"""
    
    def setUp(self):
        """Set up test data"""
        # Create two users
        self.user1 = User.objects.create_user(
            email='user1@iiti.ac.in',
            username='user1',
            password='testpass123',
            is_verified=True
        )
        self.user2 = User.objects.create_user(
            email='user2@iiti.ac.in',
            username='user2',
            password='testpass123',
            is_verified=True
        )
        
        # Create profiles
        self.profile1 = Profile.objects.create(
            user=self.user1,
            age=22,
            interests=['coding', 'music'],
            hobbies=['reading'],
            relationship_intent='friendship'
        )
        self.profile2 = Profile.objects.create(
            user=self.user2,
            age=23,
            interests=['sports', 'movies'],
            hobbies=['gaming'],
            relationship_intent='dating'
        )
        
        # Create mutual swipes
        Swipe.objects.create(
            swiper=self.profile1,
            swiped=self.profile2,
            direction='right'
        )
        Swipe.objects.create(
            swiper=self.profile2,
            swiped=self.profile1,
            direction='right'
        )
        
        # Create match
        self.match = Match.objects.create(
            profile1=self.profile1,
            profile2=self.profile2
        )
        
        # Generate JWT tokens
        self.token1 = str(AccessToken.for_user(self.user1))
        self.token2 = str(AccessToken.for_user(self.user2))
    
    @pytest.mark.asyncio
    async def test_match_connection_success(self):
        """Test successful WebSocket connection to match chat"""
        application = JWTAuthMiddleware(URLRouter(websocket_urlpatterns))
        communicator = WebsocketCommunicator(
            application,
            f'/ws/match/{self.match.id}/?token={self.token1}'
        )
        
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        
        await communicator.disconnect()
    
    @pytest.mark.asyncio
    async def test_match_connection_unauthorized(self):
        """Test WebSocket connection fails without authentication"""
        application = JWTAuthMiddleware(URLRouter(websocket_urlpatterns))
        communicator = WebsocketCommunicator(
            application,
            f'/ws/match/{self.match.id}/'
        )
        
        connected, _ = await communicator.connect()
        self.assertFalse(connected)
    
    @pytest.mark.asyncio
    async def test_match_connection_not_participant(self):
        """Test WebSocket connection fails if user is not part of match"""
        # Create a third user who is not part of the match
        user3 = await sync_to_async(User.objects.create_user)(
            email='user3@iiti.ac.in',
            username='user3',
            password='testpass123',
            is_verified=True
        )
        await sync_to_async(Profile.objects.create)(
            user=user3,
            age=24,
            interests=['art'],
            hobbies=['painting'],
            relationship_intent='casual'
        )
        token3 = str(AccessToken.for_user(user3))
        
        application = JWTAuthMiddleware(URLRouter(websocket_urlpatterns))
        communicator = WebsocketCommunicator(
            application,
            f'/ws/match/{self.match.id}/?token={token3}'
        )
        
        connected, _ = await communicator.connect()
        self.assertFalse(connected)
    
    @pytest.mark.asyncio
    async def test_send_message_in_match(self):
        """Test sending a message in match chat"""
        application = JWTAuthMiddleware(URLRouter(websocket_urlpatterns))
        communicator = WebsocketCommunicator(
            application,
            f'/ws/match/{self.match.id}/?token={self.token1}'
        )
        
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        
        # Send a message
        await communicator.send_json_to({
            'type': 'message.send',
            'content': 'Hello from match chat!',
            'message_type': 'text'
        })
        
        # Receive the broadcasted message
        response = await communicator.receive_json_from(timeout=5)
        
        self.assertEqual(response['type'], 'message.receive')
        self.assertEqual(response['message']['content'], 'Hello from match chat!')
        self.assertEqual(response['message']['sender_anonymous_id'], str(self.profile1.anonymous_id))
        self.assertEqual(response['message']['match_id'], str(self.match.id))
        
        # Verify message was saved to database
        message = await sync_to_async(Message.objects.filter(match=self.match).select_related('sender').first)()
        self.assertIsNotNone(message)
        self.assertEqual(message.content, 'Hello from match chat!')
        self.assertEqual(message.sender, self.profile1)
        
        await communicator.disconnect()
    
    @pytest.mark.asyncio
    async def test_typing_indicator_in_match(self):
        """Test typing indicators in match chat"""
        application = JWTAuthMiddleware(URLRouter(websocket_urlpatterns))
        
        # Connect both users
        communicator1 = WebsocketCommunicator(
            application,
            f'/ws/match/{self.match.id}/?token={self.token1}'
        )
        communicator2 = WebsocketCommunicator(
            application,
            f'/ws/match/{self.match.id}/?token={self.token2}'
        )
        
        await communicator1.connect()
        await communicator2.connect()
        
        # User 1 starts typing
        await communicator1.send_json_to({
            'type': 'typing.start'
        })
        
        # User 2 should receive typing indicator
        response = await communicator2.receive_json_from(timeout=5)
        self.assertEqual(response['type'], 'typing.start')
        self.assertEqual(response['profile_id'], str(self.profile1.anonymous_id))
        
        # User 1 stops typing
        await communicator1.send_json_to({
            'type': 'typing.stop'
        })
        
        # User 2 should receive stop indicator
        response = await communicator2.receive_json_from(timeout=5)
        self.assertEqual(response['type'], 'typing.stop')
        self.assertEqual(response['profile_id'], str(self.profile1.anonymous_id))
        
        await communicator1.disconnect()
        await communicator2.disconnect()
    
    @pytest.mark.asyncio
    async def test_read_receipt_in_match(self):
        """Test read receipts in match chat"""
        application = JWTAuthMiddleware(URLRouter(websocket_urlpatterns))
        
        # Connect both users
        communicator1 = WebsocketCommunicator(
            application,
            f'/ws/match/{self.match.id}/?token={self.token1}'
        )
        communicator2 = WebsocketCommunicator(
            application,
            f'/ws/match/{self.match.id}/?token={self.token2}'
        )
        
        await communicator1.connect()
        await communicator2.connect()
        
        # User 1 sends a message
        await communicator1.send_json_to({
            'type': 'message.send',
            'content': 'Test message for read receipt',
            'message_type': 'text'
        })
        
        # Both users receive the message
        msg1 = await communicator1.receive_json_from(timeout=5)
        msg2 = await communicator2.receive_json_from(timeout=5)
        message_id = msg1['message']['id']
        
        # User 2 sends read receipt
        await communicator2.send_json_to({
            'type': 'read.receipt',
            'message_id': message_id
        })
        
        # Both users should receive read receipt
        receipt1 = await communicator1.receive_json_from(timeout=5)
        receipt2 = await communicator2.receive_json_from(timeout=5)
        
        self.assertEqual(receipt1['type'], 'read.receipt')
        self.assertEqual(receipt1['message_id'], message_id)
        self.assertEqual(receipt1['profile_id'], str(self.profile2.anonymous_id))
        
        # Verify read receipt was saved to database
        read_receipt = await sync_to_async(
            ReadReceipt.objects.filter(
                message_id=message_id,
                profile=self.profile2
            ).first
        )()
        self.assertIsNotNone(read_receipt)
        
        await communicator1.disconnect()
        await communicator2.disconnect()
    
    @pytest.mark.asyncio
    async def test_message_delivery_to_both_users(self):
        """Test that messages are delivered to both users in the match"""
        application = JWTAuthMiddleware(URLRouter(websocket_urlpatterns))
        
        # Connect both users
        communicator1 = WebsocketCommunicator(
            application,
            f'/ws/match/{self.match.id}/?token={self.token1}'
        )
        communicator2 = WebsocketCommunicator(
            application,
            f'/ws/match/{self.match.id}/?token={self.token2}'
        )
        
        await communicator1.connect()
        await communicator2.connect()
        
        # User 1 sends a message
        await communicator1.send_json_to({
            'type': 'message.send',
            'content': 'Message from user 1',
            'message_type': 'text'
        })
        
        # Both users should receive the message
        response1 = await communicator1.receive_json_from(timeout=5)
        response2 = await communicator2.receive_json_from(timeout=5)
        
        self.assertEqual(response1['type'], 'message.receive')
        self.assertEqual(response2['type'], 'message.receive')
        self.assertEqual(response1['message']['content'], 'Message from user 1')
        self.assertEqual(response2['message']['content'], 'Message from user 1')
        
        await communicator1.disconnect()
        await communicator2.disconnect()
    
    @pytest.mark.asyncio
    async def test_empty_message_rejected(self):
        """Test that empty messages are rejected"""
        application = JWTAuthMiddleware(URLRouter(websocket_urlpatterns))
        communicator = WebsocketCommunicator(
            application,
            f'/ws/match/{self.match.id}/?token={self.token1}'
        )
        
        await communicator.connect()
        
        # Try to send empty message
        await communicator.send_json_to({
            'type': 'message.send',
            'content': '',
            'message_type': 'text'
        })
        
        # Should receive error
        response = await communicator.receive_json_from(timeout=5)
        self.assertEqual(response['type'], 'error')
        self.assertIn('empty', response['message'].lower())
        
        await communicator.disconnect()
