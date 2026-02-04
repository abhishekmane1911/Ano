"""
WebSocket consumers for real-time chat functionality
"""
import json
import time
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.cache import cache
from asgiref.sync import sync_to_async
from .models import Chatroom, Message, MessageReaction, ReadReceipt
from profiles.models import Profile


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for chatroom real-time communication.
    Handles message sending, editing, deleting, reactions, typing indicators,
    presence updates, and read receipts.
    """
    
    # Rate limiting: max 10 messages per 10 seconds per user
    RATE_LIMIT_MESSAGES = 10
    RATE_LIMIT_WINDOW = 10  # seconds
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.chatroom_id = self.scope['url_route']['kwargs']['chatroom_id']
        self.chatroom_group_name = f'chat_{self.chatroom_id}'
        self.user = self.scope['user']
        
        # Check if user is authenticated
        if self.user.is_anonymous:
            await self.close(code=4001)
            return
        
        # Verify chatroom exists
        chatroom_exists = await self.chatroom_exists(self.chatroom_id)
        if not chatroom_exists:
            await self.close(code=4004)
            return
        
        # Get user's profile
        self.profile = await self.get_user_profile(self.user)
        if not self.profile:
            await self.close(code=4003)
            return
        
        # Join chatroom group
        await self.channel_layer.group_add(
            self.chatroom_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Broadcast user join event
        await self.channel_layer.group_send(
            self.chatroom_group_name,
            {
                'type': 'user_join',
                'profile_id': str(self.profile.anonymous_id),
                'timestamp': time.time()
            }
        )
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        if hasattr(self, 'chatroom_group_name') and hasattr(self, 'profile'):
            # Broadcast user leave event
            await self.channel_layer.group_send(
                self.chatroom_group_name,
                {
                    'type': 'user_leave',
                    'profile_id': str(self.profile.anonymous_id),
                    'timestamp': time.time()
                }
            )
            
            # Leave chatroom group
            await self.channel_layer.group_discard(
                self.chatroom_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            event_type = data.get('type')
            
            # Check rate limiting only for message sends (not for typing, ping, etc.)
            if event_type == 'message.send':
                if not await self.check_rate_limit():
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': 'Rate limit exceeded. Please slow down.'
                    }))
                    return
            
            # Route to appropriate handler
            if event_type == 'message.send':
                await self.handle_message_send(data)
            elif event_type == 'message.edit':
                await self.handle_message_edit(data)
            elif event_type == 'message.delete':
                await self.handle_message_delete(data)
            elif event_type == 'message.react':
                await self.handle_message_react(data)
            elif event_type == 'typing.start':
                await self.handle_typing_start(data)
            elif event_type == 'typing.stop':
                await self.handle_typing_stop(data)
            elif event_type == 'read.receipt':
                await self.handle_read_receipt(data)
            elif event_type == 'ping':
                # Handle ping/pong for connection keep-alive
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': time.time()
                }))
            else:
                # Silently ignore unknown event types to avoid spam
                pass
        
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
        """Handle sending a new message"""
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
            # Broadcast message to chatroom
            await self.channel_layer.group_send(
                self.chatroom_group_name,
                {
                    'type': 'message_receive',
                    'message': await self.serialize_message(message)
                }
            )
    
    async def handle_message_edit(self, data):
        """Handle editing an existing message"""
        message_id = data.get('message_id')
        new_content = data.get('content', '').strip()
        
        if not message_id or not new_content:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Message ID and content are required'
            }))
            return
        
        # Update message in database
        message = await self.update_message(message_id, new_content)
        
        if message:
            # Broadcast update to chatroom
            await self.channel_layer.group_send(
                self.chatroom_group_name,
                {
                    'type': 'message_edit',
                    'message': await self.serialize_message(message)
                }
            )
        else:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Failed to edit message. You can only edit your own messages.'
            }))
    
    async def handle_message_delete(self, data):
        """Handle deleting a message"""
        message_id = data.get('message_id')
        
        if not message_id:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Message ID is required'
            }))
            return
        
        # Delete message in database (soft delete)
        success = await self.delete_message(message_id)
        
        if success:
            # Broadcast deletion to chatroom
            await self.channel_layer.group_send(
                self.chatroom_group_name,
                {
                    'type': 'message_delete',
                    'message_id': message_id,
                    'timestamp': time.time()
                }
            )
        else:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Failed to delete message. You can only delete your own messages.'
            }))
    
    async def handle_message_react(self, data):
        """Handle adding a reaction to a message"""
        message_id = data.get('message_id')
        emoji = data.get('emoji', '').strip()
        
        if not message_id or not emoji:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Message ID and emoji are required'
            }))
            return
        
        # Add reaction in database
        reaction = await self.add_reaction(message_id, emoji)
        
        if reaction:
            # Broadcast reaction to chatroom
            await self.channel_layer.group_send(
                self.chatroom_group_name,
                {
                    'type': 'message_react',
                    'message_id': message_id,
                    'emoji': emoji,
                    'profile_id': str(self.profile.anonymous_id),
                    'reaction_id': str(reaction.id),
                    'timestamp': time.time()
                }
            )
    
    async def handle_typing_start(self, data):
        """Handle typing indicator start"""
        await self.channel_layer.group_send(
            self.chatroom_group_name,
            {
                'type': 'typing_start',
                'profile_id': str(self.profile.anonymous_id),
                'timestamp': time.time()
            }
        )
    
    async def handle_typing_stop(self, data):
        """Handle typing indicator stop"""
        await self.channel_layer.group_send(
            self.chatroom_group_name,
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
            # Send read receipt to chatroom (typically only to sender)
            await self.channel_layer.group_send(
                self.chatroom_group_name,
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
    
    async def message_edit(self, event):
        """Broadcast message edit to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'message.edit',
            'message': event['message']
        }))
    
    async def message_delete(self, event):
        """Broadcast message deletion to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'message.delete',
            'message_id': event['message_id'],
            'timestamp': event['timestamp']
        }))
    
    async def message_react(self, event):
        """Broadcast message reaction to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'message.react',
            'message_id': event['message_id'],
            'emoji': event['emoji'],
            'profile_id': event['profile_id'],
            'reaction_id': event['reaction_id'],
            'timestamp': event['timestamp']
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
    
    async def user_join(self, event):
        """Broadcast user join to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'user.join',
            'profile_id': event['profile_id'],
            'timestamp': event['timestamp']
        }))
    
    async def user_leave(self, event):
        """Broadcast user leave to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'user.leave',
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
    
    # Database operations
    
    @database_sync_to_async
    def chatroom_exists(self, chatroom_id):
        """Check if chatroom exists and is active"""
        return Chatroom.objects.filter(id=chatroom_id, is_active=True).exists()
    
    @database_sync_to_async
    def get_user_profile(self, user):
        """Get user's profile"""
        try:
            return user.profile
        except Profile.DoesNotExist:
            return None
    
    @database_sync_to_async
    def create_message(self, content, message_type, media_url):
        """Create a new message in the database"""
        try:
            chatroom = Chatroom.objects.get(id=self.chatroom_id)
            message = Message.objects.create(
                chatroom=chatroom,
                sender=self.profile,
                content=content,
                message_type=message_type,
                media_url=media_url
            )
            return message
        except Exception:
            return None
    
    @database_sync_to_async
    def update_message(self, message_id, new_content):
        """Update an existing message"""
        try:
            message = Message.objects.get(id=message_id, sender=self.profile)
            if message.is_deleted:
                return None
            message.content = new_content
            message.is_edited = True
            message.save()
            return message
        except Message.DoesNotExist:
            return None
    
    @database_sync_to_async
    def delete_message(self, message_id):
        """Soft delete a message"""
        try:
            message = Message.objects.get(id=message_id, sender=self.profile)
            message.is_deleted = True
            message.content = '[Message deleted]'
            message.media_url = ''
            message.save()
            return True
        except Message.DoesNotExist:
            return False
    
    @database_sync_to_async
    def add_reaction(self, message_id, emoji):
        """Add a reaction to a message"""
        try:
            message = Message.objects.get(id=message_id)
            reaction, created = MessageReaction.objects.get_or_create(
                message=message,
                profile=self.profile,
                emoji=emoji
            )
            return reaction
        except Message.DoesNotExist:
            return None
    
    @database_sync_to_async
    def create_read_receipt(self, message_id):
        """Create a read receipt for a message"""
        try:
            message = Message.objects.get(id=message_id)
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
            'chatroom_id': str(message.chatroom.id) if message.chatroom else None,
            'sender_id': str(message.sender.anonymous_id),
            'content': message.content,
            'message_type': message.message_type,
            'media_url': media_url,
            'is_edited': message.is_edited,
            'is_deleted': message.is_deleted,
            'is_pinned': message.is_pinned,
            'created_at': message.created_at.isoformat(),
            'updated_at': message.updated_at.isoformat()
        }
    
    async def check_rate_limit(self):
        """Check if user has exceeded rate limit"""
        cache_key = f'ws_rate_limit_{self.user.id}_{self.chatroom_id}'
        
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
