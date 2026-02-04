from rest_framework import serializers
from .models import Swipe, Match
from profiles.models import Profile
from profiles.serializers import ProfileSerializer
from chat.models import Message


class SwipeSerializer(serializers.ModelSerializer):
    """Serializer for swipe records"""
    
    swiped = serializers.UUIDField()
    
    class Meta:
        model = Swipe
        fields = ['id', 'swiper', 'swiped', 'direction', 'created_at']
        read_only_fields = ['id', 'swiper', 'created_at']
    
    def validate_swiped(self, value):
        """Validate and convert anonymous_id to Profile"""
        try:
            # Try to find profile by anonymous_id
            profile = Profile.objects.get(anonymous_id=value)
            return profile
        except Profile.DoesNotExist:
            raise serializers.ValidationError("Profile not found")
    
    def validate(self, data):
        """Validate swipe data"""
        swiper = self.context['request'].user.profile
        swiped = data.get('swiped')
        
        # Can't swipe on yourself
        if swiper == swiped:
            raise serializers.ValidationError("Cannot swipe on your own profile")
        
        # Check if already swiped
        if Swipe.objects.filter(swiper=swiper, swiped=swiped).exists():
            raise serializers.ValidationError("Already swiped on this profile")
        
        return data


class MatchSerializer(serializers.ModelSerializer):
    """Serializer for match records"""
    
    profile1 = serializers.SerializerMethodField()
    profile2 = serializers.SerializerMethodField()
    other_profile = serializers.SerializerMethodField()
    
    class Meta:
        model = Match
        fields = ['id', 'profile1', 'profile2', 'other_profile', 'matched_at', 'is_active']
        read_only_fields = ['id', 'profile1', 'profile2', 'matched_at']
    
    def get_profile1(self, obj):
        """Get profile1 with context"""
        return ProfileSerializer(obj.profile1, context=self.context).data
    
    def get_profile2(self, obj):
        """Get profile2 with context"""
        return ProfileSerializer(obj.profile2, context=self.context).data
    
    def get_other_profile(self, obj):
        """Get the other profile in the match relative to the requesting user"""
        request = self.context.get('request')
        if request and hasattr(request.user, 'profile'):
            other = obj.get_other_profile(request.user.profile)
            if other:
                return ProfileSerializer(other, context=self.context).data
        return None


class MatchMessageSerializer(serializers.ModelSerializer):
    """Serializer for messages in match chats"""
    
    sender_anonymous_id = serializers.CharField(source='sender.anonymous_id', read_only=True)
    is_own_message = serializers.SerializerMethodField()
    media_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'match', 'sender', 'sender_anonymous_id', 'content',
            'message_type', 'media_url', 'is_edited', 'is_deleted',
            'created_at', 'updated_at', 'is_own_message'
        ]
        read_only_fields = ['id', 'sender', 'sender_anonymous_id', 'created_at', 'updated_at']
    
    def get_is_own_message(self, obj):
        """Check if the message was sent by the requesting user"""
        request = self.context.get('request')
        if request and hasattr(request.user, 'profile'):
            return obj.sender == request.user.profile
        return False
    
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
    
    def validate(self, data):
        """Validate message data"""
        match = data.get('match')
        request = self.context.get('request')
        
        if not match:
            raise serializers.ValidationError("Match is required")
        
        # Verify user is part of the match
        if request and hasattr(request.user, 'profile'):
            if not match.has_profile(request.user.profile):
                raise serializers.ValidationError("You are not part of this match")
        
        return data
