from rest_framework import serializers
from .models import Chatroom, Message, MessageReaction, ReadReceipt
from profiles.models import Profile


class ChatroomSerializer(serializers.ModelSerializer):
    """Serializer for Chatroom model"""
    
    class Meta:
        model = Chatroom
        fields = [
            'id',
            'name',
            'description',
            'is_active',
            'created_at',
            'member_count'
        ]
        read_only_fields = ['id', 'created_at', 'member_count']


class MessageReactionSerializer(serializers.ModelSerializer):
    """Serializer for MessageReaction model"""
    
    profile_id = serializers.UUIDField(source='profile.anonymous_id', read_only=True)
    
    class Meta:
        model = MessageReaction
        fields = ['id', 'emoji', 'profile_id', 'created_at']
        read_only_fields = ['id', 'profile_id', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""
    
    sender_id = serializers.UUIDField(source='sender.anonymous_id', read_only=True)
    reactions = MessageReactionSerializer(many=True, read_only=True)
    reaction_count = serializers.SerializerMethodField()
    media_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id',
            'chatroom',
            'sender_id',
            'content',
            'message_type',
            'media_url',
            'is_edited',
            'is_deleted',
            'is_pinned',
            'created_at',
            'updated_at',
            'reactions',
            'reaction_count'
        ]
        read_only_fields = [
            'id',
            'sender_id',
            'is_edited',
            'is_deleted',
            'created_at',
            'updated_at',
            'reactions',
            'reaction_count'
        ]
    
    def get_reaction_count(self, obj):
        """Get count of reactions grouped by emoji"""
        reactions = {}
        for reaction in obj.reactions.all():
            emoji = reaction.emoji
            reactions[emoji] = reactions.get(emoji, 0) + 1
        return reactions
    
    def get_media_url(self, obj):
        """Convert relative media URL to absolute URL"""
        if not obj.media_url:
            return ''
        
        # If already absolute, return as-is
        if obj.media_url.startswith('http://') or obj.media_url.startswith('https://'):
            return obj.media_url
        
        # Build absolute URL
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.media_url)
        
        return obj.media_url


class MessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating messages"""
    
    class Meta:
        model = Message
        fields = ['content', 'message_type', 'media_url']
    
    def validate_content(self, value):
        """Validate message content is not empty for text messages"""
        if not value or not value.strip():
            raise serializers.ValidationError("Message content cannot be empty")
        
        # Length validation
        if len(value) > 2000:
            raise serializers.ValidationError("Message content too long (max 2000 characters)")
        
        # Basic XSS prevention
        import re
        if re.search(r'<script|javascript:|data:|vbscript:', value, re.IGNORECASE):
            raise serializers.ValidationError("Message contains prohibited content")
        
        return value


class MessageUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating messages"""
    
    class Meta:
        model = Message
        fields = ['content']
    
    def validate_content(self, value):
        """Validate message content is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Message content cannot be empty")
        return value


class ReactionCreateSerializer(serializers.Serializer):
    """Serializer for creating reactions"""
    
    emoji = serializers.CharField(max_length=10)
    
    def validate_emoji(self, value):
        """Validate emoji is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Emoji cannot be empty")
        return value


class ReadReceiptSerializer(serializers.ModelSerializer):
    """Serializer for ReadReceipt model"""
    
    profile_id = serializers.UUIDField(source='profile.anonymous_id', read_only=True)
    
    class Meta:
        model = ReadReceipt
        fields = ['id', 'message', 'profile_id', 'read_at']
        read_only_fields = ['id', 'profile_id', 'read_at']


class MessageSearchResultSerializer(serializers.ModelSerializer):
    """Serializer for message search results with highlighting"""
    
    sender_id = serializers.UUIDField(source='sender.anonymous_id', read_only=True)
    chatroom_name = serializers.CharField(source='chatroom.name', read_only=True, allow_null=True)
    match_id = serializers.UUIDField(source='match.id', read_only=True, allow_null=True)
    highlighted_content = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id',
            'chatroom',
            'chatroom_name',
            'match_id',
            'sender_id',
            'content',
            'highlighted_content',
            'message_type',
            'is_pinned',
            'created_at'
        ]
        read_only_fields = fields
    
    def get_highlighted_content(self, obj):
        """Return content with search term highlighted"""
        query = self.context.get('query', '')
        if not query:
            return obj.content
        
        # Simple highlighting - wrap matching text in <mark> tags
        import re
        pattern = re.compile(re.escape(query), re.IGNORECASE)
        highlighted = pattern.sub(lambda m: f'<mark>{m.group()}</mark>', obj.content)
        return highlighted
