import uuid
from django.db import models
from django.conf import settings
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from profiles.models import Profile


class Chatroom(models.Model):
    """Public chatroom for anonymous group communication"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, help_text='Chatroom name')
    description = models.TextField(
        blank=True,
        help_text='Chatroom description'
    )
    is_active = models.BooleanField(
        default=True,
        help_text='Whether the chatroom is active'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_chatrooms',
        help_text='User who created the chatroom'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    member_count = models.IntegerField(
        default=0,
        help_text='Number of members in the chatroom'
    )
    
    class Meta:
        db_table = 'chatrooms'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Chatroom: {self.name}"


class Message(models.Model):
    """Message in a chatroom or match chat"""
    
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('voice', 'Voice'),
        ('system', 'System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chatroom = models.ForeignKey(
        Chatroom,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='messages',
        help_text='Chatroom this message belongs to (null for match messages)'
    )
    match = models.ForeignKey(
        'matchmaking.Match',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='messages',
        help_text='Match this message belongs to (null for chatroom messages)'
    )
    sender = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        help_text='Profile that sent this message'
    )
    content = models.TextField(help_text='Message content')
    message_type = models.CharField(
        max_length=10,
        choices=MESSAGE_TYPE_CHOICES,
        default='text',
        help_text='Type of message'
    )
    media_url = models.CharField(
        max_length=500,
        blank=True,
        help_text='URL to media file if applicable'
    )
    is_edited = models.BooleanField(
        default=False,
        help_text='Whether the message has been edited'
    )
    is_deleted = models.BooleanField(
        default=False,
        help_text='Whether the message has been deleted'
    )
    is_pinned = models.BooleanField(
        default=False,
        help_text='Whether the message is pinned'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    search_vector = SearchVectorField(null=True, blank=True)
    
    class Meta:
        db_table = 'messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['chatroom', 'created_at']),
            models.Index(fields=['match', 'created_at']),
            models.Index(fields=['sender']),
            models.Index(fields=['is_pinned']),
            GinIndex(fields=['search_vector']),
        ]
    
    def __str__(self):
        return f"Message {self.id} by {self.sender.anonymous_id}"


class MessageReaction(models.Model):
    """Emoji reaction to a message"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='reactions',
        help_text='Message being reacted to'
    )
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='message_reactions',
        help_text='Profile that reacted'
    )
    emoji = models.CharField(
        max_length=10,
        help_text='Emoji reaction'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'message_reactions'
        unique_together = ['message', 'profile', 'emoji']
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.emoji} on {self.message.id} by {self.profile.anonymous_id}"


class ReadReceipt(models.Model):
    """Read receipt for a message"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='read_receipts',
        help_text='Message that was read'
    )
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='read_receipts',
        help_text='Profile that read the message'
    )
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'read_receipts'
        unique_together = ['message', 'profile']
        ordering = ['read_at']
    
    def __str__(self):
        return f"Read by {self.profile.anonymous_id} at {self.read_at}"
