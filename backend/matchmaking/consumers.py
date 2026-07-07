"""
WebSocket consumers for match chat functionality
"""
import json
import time
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.cache import cache
from asgiref.sync import sync_to_async
from .models import Match
from chat.models import Message, ReadReceipt
from profiles.models import Profile
from reports.utils import is_blocked


class MatchConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for match chat real-time communication.
    Handles message sending, receiving, typing indicators, and read receipts
    for one-on-one match conversations.
    """
    
    # Rate limiting: max 20 messages per 10 seconds per user (more lenient for 1-on-1)
    RATE_LIMIT_MESSAGES = 20
    RATE_LIMIT_WINDOW = 10  # seconds
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.match_id = self.scope['url_route']['kwargs']['match_id']
        self.match_group_name = f'match_{self.match_id}'
        self.user = self.scope['user']
        
        # Check if user is authenticated
        if self.user.is_anonymous:
            await self.close(code=4001)
            return
        
        # Get user's profile
        self.profile = await self.get_user_profile(self.user)
        if not self.profile:
            await self.close(code=4003)
            return
        
        # Verify match exists and user is part of it
        match_valid = await self.verify_match_access(self.match_id, self.profile)
        if not match_valid:
            await self.close(code=4004)
            return
        
        # Join match group
        await self.channel_layer.group_add(
            self.match_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'match_group_name'):
            # Leave match group
            await self.channel_layer.group_discard(
                self.match_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            event_type = data.get('type')
            
            # Check rate limiting
            if not await self.check_rate_limit():
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Rate limit exceeded. Please slow down.'
                }))
                return
            
            # Route to appropriate handler
            if event_type == 'message.send':
                await self.handle_message_send(data)
            elif event_type == 'typing.start':
                await self.handle_typing_start(data)
            elif event_type == 'typing.stop':
                await self.handle_typing_stop(data)
            elif event_type == 'read.receipt':
                await self.handle_read_receipt(data)
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Unknown event type: {event_type}'
                }))
        
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Error processing message: {str(e)}'
            }))
    
    async def handle_message_send(self, data):
        """Handle sending a new message in match chat"""
        content = data.get('content', '').strip()
        message_type = data.get('message_type', 'text')
        media_url = data.get('media_url', '')
        
        # Validate content length
        if len(content) > 2000:  # Reasonable message length limit
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Message content too long (max 2000 characters)'
            }))
            return
        
        # Basic HTML/script tag sanitization
        import re
        if re.search(r'<script|javascript:|data:|vbscript:', content, re.IGNORECASE):
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Message contains prohibited content'
            }))
            return
        
        if not content and message_type == 'text':
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Message content cannot be empty'
            }))
            return
        
        # Validate media URL if provided
        if media_url:
            # Basic validation - check if it's a proper media URL
            if not media_url.startswith(('/media/', 'http://', 'https://')):
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': 'Invalid media URL format'
                }))
                return
        
        # Create message in database
        message = await self.create_message(
            content=content,
            message_type=message_type,
            media_url=media_url
        )
        
        if message:
            # Broadcast message to both users in the match
            await self.channel_layer.group_send(
                self.match_group_name,
                {
                    'type': 'message_receive',
                    'message': await self.serialize_message(message)
                }
            )
    
    async def handle_typing_start(self, data):
        """Handle typing indicator start"""
        await self.channel_layer.group_send(
            self.match_group_name,
            {
                'type': 'typing_start',
                'profile_id': str(self.profile.anonymous_id),
                'timestamp': time.time()
            }
        )
    
    async def handle_typing_stop(self, data):
        """Handle typing indicator stop"""
        await self.channel_layer.group_send(
            self.match_group_name,
            {
                'type': 'typing_stop',
                'profile_id': str(self.profile.anonymous_id),
                'timestamp': time.time()
            }
        )
    
    async def handle_read_receipt(self, data):
        """Handle read receipt for a message"""
        message_id = data.get('message_id')
        
        if not message_id:
            return
        
        # Create read receipt in database
        receipt = await self.create_read_receipt(message_id)
        
        if receipt:
            # Send read receipt to both users
            await self.channel_layer.group_send(
                self.match_group_name,
                {
                    'type': 'read_receipt',
                    'message_id': message_id,
                    'profile_id': str(self.profile.anonymous_id),
                    'timestamp': time.time()
                }
            )
    
    # Event handlers for broadcasting
    
    async def message_receive(self, event):
        """Broadcast received message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'message.receive',
            'message': event['message']
        }))
    
    async def typing_start(self, event):
        """Broadcast typing start to WebSocket"""
        # Don't send typing indicator to the user who is typing
        if event['profile_id'] != str(self.profile.anonymous_id):
            await self.send(text_data=json.dumps({
                'type': 'typing.start',
                'profile_id': event['profile_id'],
                'timestamp': event['timestamp']
            }))
    
    async def typing_stop(self, event):
        """Broadcast typing stop to WebSocket"""
        # Don't send typing indicator to the user who stopped typing
        if event['profile_id'] != str(self.profile.anonymous_id):
            await self.send(text_data=json.dumps({
                'type': 'typing.stop',
                'profile_id': event['profile_id'],
                'timestamp': event['timestamp']
            }))
    
    async def read_receipt(self, event):
        """Broadcast read receipt to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'read.receipt',
            'message_id': event['message_id'],
            'profile_id': event['profile_id'],
            'timestamp': event['timestamp']
        }))
    
    async def reputation_update(self, event):
        """Broadcast reputation update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'reputation.update',
            'user_id': event['user_id'],
            'reputation_data': event['reputation_data'],
            'timestamp': event['timestamp']
        }))
    
    async def ranking_update(self, event):
        """Broadcast ranking update to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'ranking.update',
            'message_id': event['message_id'],
            'ranking_data': event['ranking_data'],
            'timestamp': event['timestamp']
        }))
    
    async def moderation_notification(self, event):
        """Broadcast moderation notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'moderation.notification',
            'notification_type': event['notification_type'],
            'message': event['message'],
            'details': event.get('details', {}),
            'timestamp': event['timestamp']
        }))
    
    async def tier_update(self, event):
        """Broadcast tier update notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'tier.update',
            'user_id': event['user_id'],
            'old_tier': event['old_tier'],
            'new_tier': event['new_tier'],
            'new_privileges': event.get('new_privileges', []),
            'timestamp': event['timestamp']
        }))
    
    # Database operations
    
    @database_sync_to_async
    def get_user_profile(self, user):
        """Get user's profile"""
        try:
            return user.profile
        except Profile.DoesNotExist:
            return None
    
    @database_sync_to_async
    def verify_match_access(self, match_id, profile):
        """Verify that the match exists, the user is part of it, and no blocks exist"""
        try:
            match = Match.objects.get(id=match_id, is_active=True)
            if not match.has_profile(profile):
                return False
            
            # Get the other profile in the match
            other_profile = match.profile1 if match.profile2 == profile else match.profile2
            
            # Check if either user has blocked the other
            if is_blocked(profile, other_profile):
                return False
            
            return True
        except Match.DoesNotExist:
            return False
    
    @database_sync_to_async
    def create_message(self, content, message_type, media_url):
        """Create a new message in the match chat"""
        try:
            match = Match.objects.get(id=self.match_id)
            message = Message.objects.create(
                match=match,
                sender=self.profile,
                content=content,
                message_type=message_type,
                media_url=media_url
            )
            return message
        except Exception:
            return None
    
    @database_sync_to_async
    def create_read_receipt(self, message_id):
        """Create a read receipt for a message"""
        try:
            message = Message.objects.get(id=message_id, match_id=self.match_id)
            receipt, created = ReadReceipt.objects.get_or_create(
                message=message,
                profile=self.profile
            )
            return receipt
        except Message.DoesNotExist:
            return None
    
    @database_sync_to_async
    def serialize_message(self, message):
        """Serialize a message for JSON response"""
        # Convert relative media URL to absolute URL
        media_url = message.media_url
        if media_url and not media_url.startswith(('http://', 'https://')):
            # Build absolute URL
            from django.conf import settings
            if media_url.startswith('/media/'):
                # Already has /media/ prefix
                base_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
                media_url = f"{base_url}{media_url}"
            elif media_url.startswith('media/'):
                # Missing leading slash
                base_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
                media_url = f"{base_url}/{media_url}"
            else:
                # Relative path, add full media URL
                base_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
                media_url = f"{base_url}{settings.MEDIA_URL}{media_url}"
        
        return {
            'id': str(message.id),
            'match_id': str(message.match.id) if message.match else None,
            'sender': str(message.sender.id),
            'sender_anonymous_id': str(message.sender.anonymous_id),
            'content': message.content,
            'message_type': message.message_type,
            'media_url': media_url,
            'is_edited': message.is_edited,
            'is_deleted': message.is_deleted,
            'created_at': message.created_at.isoformat(),
            'updated_at': message.updated_at.isoformat(),
            'is_own_message': message.sender == self.profile
        }
    
    async def check_rate_limit(self):
        """Check if user has exceeded rate limit"""
        cache_key = f'ws_match_rate_limit_{self.user.id}_{self.match_id}'
        
        # Use sync_to_async for cache operations
        messages_sent = await sync_to_async(cache.get)(cache_key, 0)
        
        if messages_sent >= self.RATE_LIMIT_MESSAGES:
            return False
        
        # Increment counter
        await sync_to_async(cache.set)(
            cache_key,
            messages_sent + 1,
            self.RATE_LIMIT_WINDOW
        )
        return True
