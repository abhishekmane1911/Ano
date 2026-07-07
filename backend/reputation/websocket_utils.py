"""
WebSocket utilities for broadcasting real-time reputation and ranking updates
"""
import time
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class RealtimeNotifier:
    """Utility class for sending real-time notifications via WebSocket"""
    
    def __init__(self):
        self.channel_layer = get_channel_layer()
    
    def broadcast_reputation_update(self, user_id, reputation_data, chatroom_id=None):
        """Broadcast reputation update to relevant WebSocket groups"""
        if not self.channel_layer:
            return
        
        message = {
            'type': 'reputation_update',
            'user_id': user_id,
            'reputation_data': reputation_data,
            'timestamp': time.time()
        }
        
        # Broadcast to specific chatroom if provided
        if chatroom_id:
            group_name = f'chat_{chatroom_id}'
            async_to_sync(self.channel_layer.group_send)(group_name, message)
        
        # Also broadcast to user's personal channel if they have one
        user_group_name = f'user_{user_id}'
        async_to_sync(self.channel_layer.group_send)(user_group_name, message)
    
    def broadcast_ranking_update(self, message_id, ranking_data, chatroom_id=None, match_id=None):
        """Broadcast ranking update to relevant WebSocket groups"""
        if not self.channel_layer:
            return
        
        message = {
            'type': 'ranking_update',
            'message_id': message_id,
            'ranking_data': ranking_data,
            'timestamp': time.time()
        }
        
        # Broadcast to chatroom or match
        if chatroom_id:
            group_name = f'chat_{chatroom_id}'
            async_to_sync(self.channel_layer.group_send)(group_name, message)
        elif match_id:
            group_name = f'match_{match_id}'
            async_to_sync(self.channel_layer.group_send)(group_name, message)
    
    def broadcast_tier_update(self, user_id, old_tier, new_tier, new_privileges, chatroom_id=None):
        """Broadcast tier update notification"""
        if not self.channel_layer:
            return
        
        message = {
            'type': 'tier_update',
            'user_id': user_id,
            'old_tier': old_tier,
            'new_tier': new_tier,
            'new_privileges': new_privileges,
            'timestamp': time.time()
        }
        
        # Broadcast to specific chatroom if provided
        if chatroom_id:
            group_name = f'chat_{chatroom_id}'
            async_to_sync(self.channel_layer.group_send)(group_name, message)
        
        # Also broadcast to user's personal channel
        user_group_name = f'user_{user_id}'
        async_to_sync(self.channel_layer.group_send)(user_group_name, message)
    
    def broadcast_moderation_notification(self, user_id, notification_type, message, details=None, chatroom_id=None):
        """Broadcast moderation notification"""
        if not self.channel_layer:
            return
        
        notification = {
            'type': 'moderation_notification',
            'notification_type': notification_type,
            'message': message,
            'details': details or {},
            'timestamp': time.time()
        }
        
        # Send to user's personal channel
        user_group_name = f'user_{user_id}'
        async_to_sync(self.channel_layer.group_send)(user_group_name, notification)
        
        # Also broadcast to chatroom if it's a public notification
        if chatroom_id and notification_type in ['content_rejected', 'user_shadowbanned']:
            group_name = f'chat_{chatroom_id}'
            async_to_sync(self.channel_layer.group_send)(group_name, notification)


# Global instance
realtime_notifier = RealtimeNotifier()