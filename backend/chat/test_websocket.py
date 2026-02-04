"""
Tests for WebSocket chat functionality
"""
import pytest
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from chat.routing import websocket_urlpatterns
from chat.middleware import JWTAuthMiddleware
from chat.models import Chatroom, Message
from profiles.models import Profile

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.asyncio
class TestChatConsumer:
    """Test cases for ChatConsumer WebSocket functionality"""
    
    async def test_websocket_connection_without_token(self):
        """Test that connection is rejected without authentication token"""
        application = JWTAuthMiddleware(URLRouter(websocket_urlpatterns))
        
        # Create a chatroom
        chatroom = await self.create_chatroom()
        
        # Try to connect without token
        communicator = WebsocketCommunicator(
            application,
            f"/ws/chat/{chatroom.id}/"
        )
        
        connected, subprotocol = await communicator.connect()
        assert not connected
        
        await communicator.disconnect()
    
    async def test_websocket_connection_with_valid_token(self):
        """Test that connection succeeds with valid JWT token"""
        application = JWTAuthMiddleware(URLRouter(websocket_urlpatterns))
        
        # Create user, profile, and chatroom
        user = await self.create_user()
        profile = await self.create_profile(user)
        chatroom = await self.create_chatroom()
        
        # Generate JWT token
        token = str(AccessToken.for_user(user))
        
        # Connect with token
        communicator = WebsocketCommunicator(
            application,
            f"/ws/chat/{chatroom.id}/?token={token}"
        )
        
        connected, subprotocol = await communicator.connect()
        assert connected
        
        # Should receive user.join event
        response = await communicator.receive_json_from()
        assert response['type'] == 'user.join'
        assert response['profile_id'] == str(profile.anonymous_id)
        
        await communicator.disconnect()
    
    async def test_send_message(self):
        """Test sending a message through WebSocket"""
        application = JWTAuthMiddleware(URLRouter(websocket_urlpatterns))
        
        # Setup
        user = await self.create_user()
        profile = await self.create_profile(user)
        chatroom = await self.create_chatroom()
        token = str(AccessToken.for_user(user))
        
        # Connect
        communicator = WebsocketCommunicator(
            application,
            f"/ws/chat/{chatroom.id}/?token={token}"
        )
        await communicator.connect()
        await communicator.receive_json_from()  # user.join event
        
        # Send message
        await communicator.send_json_to({
            'type': 'message.send',
            'content': 'Hello, World!',
            'message_type': 'text'
        })
        
        # Receive message
        response = await communicator.receive_json_from()
        assert response['type'] == 'message.receive'
        assert response['message']['content'] == 'Hello, World!'
        assert response['message']['sender_id'] == str(profile.anonymous_id)
        
        await communicator.disconnect()
    
    async def test_edit_message(self):
        """Test editing a message through WebSocket"""
        application = JWTAuthMiddleware(URLRouter(websocket_urlpatterns))
        
        # Setup
        user = await self.create_user()
        profile = await self.create_profile(user)
        chatroom = await self.create_chatroom()
        message = await self.create_message(chatroom, profile, "Original content")
        token = str(AccessToken.for_user(user))
        
        # Connect
        communicator = WebsocketCommunicator(
            application,
            f"/ws/chat/{chatroom.id}/?token={token}"
        )
        await communicator.connect()
        await communicator.receive_json_from()  # user.join event
        
        # Edit message
        await communicator.send_json_to({
            'type': 'message.edit',
            'message_id': str(message.id),
            'content': 'Edited content'
        })
        
        # Receive edit confirmation
        response = await communicator.receive_json_from()
        assert response['type'] == 'message.edit'
        assert response['message']['content'] == 'Edited content'
        assert response['message']['is_edited'] is True
        
        await communicator.disconnect()
    
    async def test_delete_message(self):
        """Test deleting a message through WebSocket"""
        application = JWTAuthMiddleware(URLRouter(websocket_urlpatterns))
        
        # Setup
        user = await self.create_user()
        profile = await self.create_profile(user)
        chatroom = await self.create_chatroom()
        message = await self.create_message(chatroom, profile, "To be deleted")
        token = str(AccessToken.for_user(user))
        
        # Connect
        communicator = WebsocketCommunicator(
            application,
            f"/ws/chat/{chatroom.id}/?token={token}"
        )
        await communicator.connect()
        await communicator.receive_json_from()  # user.join event
        
        # Delete message
        await communicator.send_json_to({
            'type': 'message.delete',
            'message_id': str(message.id)
        })
        
        # Receive delete confirmation
        response = await communicator.receive_json_from()
        assert response['type'] == 'message.delete'
        assert response['message_id'] == str(message.id)
        
        await communicator.disconnect()
    
    async def test_message_reaction(self):
        """Test adding a reaction to a message"""
        application = JWTAuthMiddleware(URLRouter(websocket_urlpatterns))
        
        # Setup
        user = await self.create_user()
        profile = await self.create_profile(user)
        chatroom = await self.create_chatroom()
        message = await self.create_message(chatroom, profile, "React to this")
        token = str(AccessToken.for_user(user))
        
        # Connect
        communicator = WebsocketCommunicator(
            application,
            f"/ws/chat/{chatroom.id}/?token={token}"
        )
        await communicator.connect()
        await communicator.receive_json_from()  # user.join event
        
        # Add reaction
        await communicator.send_json_to({
            'type': 'message.react',
            'message_id': str(message.id),
            'emoji': '👍'
        })
        
        # Receive reaction confirmation
        response = await communicator.receive_json_from()
        assert response['type'] == 'message.react'
        assert response['emoji'] == '👍'
        assert response['message_id'] == str(message.id)
        
        await communicator.disconnect()
    
    async def test_typing_indicators(self):
        """Test typing start and stop indicators"""
        application = JWTAuthMiddleware(URLRouter(websocket_urlpatterns))
        
        # Setup two users
        user1 = await self.create_user(email='user1@iiti.ac.in')
        profile1 = await self.create_profile(user1)
        user2 = await self.create_user(email='user2@iiti.ac.in')
        profile2 = await self.create_profile(user2)
        chatroom = await self.create_chatroom()
        
        token1 = str(AccessToken.for_user(user1))
        token2 = str(AccessToken.for_user(user2))
        
        # Connect both users
        comm1 = WebsocketCommunicator(
            application,
            f"/ws/chat/{chatroom.id}/?token={token1}"
        )
        comm2 = WebsocketCommunicator(
            application,
            f"/ws/chat/{chatroom.id}/?token={token2}"
        )
        
        await comm1.connect()
        await comm2.connect()
        
        # Clear join events
        await comm1.receive_json_from()  # user1 join
        await comm2.receive_json_from()  # user1 join (broadcast)
        await comm2.receive_json_from()  # user2 join
        await comm1.receive_json_from()  # user2 join (broadcast)
        
        # User1 starts typing
        await comm1.send_json_to({'type': 'typing.start'})
        
        # User2 should receive typing indicator
        response = await comm2.receive_json_from()
        assert response['type'] == 'typing.start'
        assert response['profile_id'] == str(profile1.anonymous_id)
        
        # User1 stops typing
        await comm1.send_json_to({'type': 'typing.stop'})
        
        # User2 should receive stop indicator
        response = await comm2.receive_json_from()
        assert response['type'] == 'typing.stop'
        assert response['profile_id'] == str(profile1.anonymous_id)
        
        await comm1.disconnect()
        await comm2.disconnect()
    
    async def test_read_receipt(self):
        """Test read receipt functionality"""
        application = JWTAuthMiddleware(URLRouter(websocket_urlpatterns))
        
        # Setup
        user = await self.create_user()
        profile = await self.create_profile(user)
        chatroom = await self.create_chatroom()
        message = await self.create_message(chatroom, profile, "Read this")
        token = str(AccessToken.for_user(user))
        
        # Connect
        communicator = WebsocketCommunicator(
            application,
            f"/ws/chat/{chatroom.id}/?token={token}"
        )
        await communicator.connect()
        await communicator.receive_json_from()  # user.join event
        
        # Send read receipt
        await communicator.send_json_to({
            'type': 'read.receipt',
            'message_id': str(message.id)
        })
        
        # Receive read receipt confirmation
        response = await communicator.receive_json_from()
        assert response['type'] == 'read.receipt'
        assert response['message_id'] == str(message.id)
        assert response['profile_id'] == str(profile.anonymous_id)
        
        await communicator.disconnect()
    
    async def test_rate_limiting(self):
        """Test that rate limiting prevents message spam"""
        application = JWTAuthMiddleware(URLRouter(websocket_urlpatterns))
        
        # Setup
        user = await self.create_user()
        await self.create_profile(user)
        chatroom = await self.create_chatroom()
        token = str(AccessToken.for_user(user))
        
        # Connect
        communicator = WebsocketCommunicator(
            application,
            f"/ws/chat/{chatroom.id}/?token={token}"
        )
        await communicator.connect()
        await communicator.receive_json_from()  # user.join event
        
        # Send messages rapidly (more than rate limit)
        for i in range(12):  # Rate limit is 10 messages per 10 seconds
            await communicator.send_json_to({
                'type': 'message.send',
                'content': f'Message {i}',
                'message_type': 'text'
            })
        
        # Should receive 10 successful messages and then error
        error_received = False
        for i in range(12):
            response = await communicator.receive_json_from()
            if response['type'] == 'error' and 'rate limit' in response['message'].lower():
                error_received = True
                break
        
        assert error_received, "Rate limit error should be received"
        
        await communicator.disconnect()
    
    # Helper methods
    
    @staticmethod
    async def create_user(email=None):
        """Create a test user"""
        from channels.db import database_sync_to_async
        import uuid
        
        @database_sync_to_async
        def _create():
            # Generate unique email and username to avoid conflicts
            unique_id = uuid.uuid4().hex[:8]
            if email is None:
                test_email = f"test_{unique_id}@iiti.ac.in"
            else:
                # If email is provided, make it unique
                email_parts = email.split('@')
                test_email = f"{email_parts[0]}_{unique_id}@{email_parts[1]}"
            
            username = f"{test_email.split('@')[0]}"
            return User.objects.create_user(
                username=username,
                email=test_email,
                password='testpass123',
                is_verified=True
            )
        
        return await _create()
    
    @staticmethod
    async def create_profile(user):
        """Create a test profile"""
        from channels.db import database_sync_to_async
        
        @database_sync_to_async
        def _create():
            return Profile.objects.create(
                user=user,
                age=20,
                interests=['coding', 'music'],
                hobbies=['reading'],
                relationship_intent='friendship',
                personality_tags=['introverted']
            )
        
        return await _create()
    
    @staticmethod
    async def create_chatroom():
        """Create a test chatroom"""
        from channels.db import database_sync_to_async
        
        @database_sync_to_async
        def _create():
            return Chatroom.objects.create(
                name='Test Chatroom',
                description='A test chatroom',
                is_active=True
            )
        
        return await _create()
    
    @staticmethod
    async def create_message(chatroom, profile, content):
        """Create a test message"""
        from channels.db import database_sync_to_async
        
        @database_sync_to_async
        def _create():
            return Message.objects.create(
                chatroom=chatroom,
                sender=profile,
                content=content,
                message_type='text'
            )
        
        return await _create()
