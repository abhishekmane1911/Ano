"""
Serializers for reputation app.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserReputation, Vote, MessageRanking
from .services import TierPrivilegeManager
from chat.models import Message

User = get_user_model()


class UserReputationSerializer(serializers.ModelSerializer):
    """Serializer for UserReputation model"""
    
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    level = serializers.SerializerMethodField()
    xp_for_next_level = serializers.SerializerMethodField()
    privileges = serializers.SerializerMethodField()
    
    class Meta:
        model = UserReputation
        fields = [
            'user_id',
            'username',
            'reputation_score',
            'rank_tier',
            'level',
            'xp_for_next_level',
            'total_upvotes_received',
            'total_downvotes_received',
            'privileges',
            'last_tier_update',
            'created_at',
            'updated_at'
        ]
        read_only_fields = fields
    
    def get_level(self, obj):
        """Get user's current level"""
        return obj.calculate_level()
    
    def get_xp_for_next_level(self, obj):
        """Get XP needed for next level"""
        return obj.xp_for_next_level()
    
    def get_privileges(self, obj):
        """Get user's current privileges"""
        return TierPrivilegeManager.get_user_privileges(obj.user)


class VoteSerializer(serializers.ModelSerializer):
    """Serializer for Vote model"""
    
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    message_id = serializers.IntegerField(source='message.id', read_only=True)
    
    class Meta:
        model = Vote
        fields = [
            'id',
            'user_id',
            'message_id',
            'vote_type',
            'created_at'
        ]
        read_only_fields = ['id', 'user_id', 'message_id', 'created_at']


class VoteCreateSerializer(serializers.Serializer):
    """Serializer for creating votes"""

    message_id = serializers.UUIDField()
    vote_type = serializers.ChoiceField(choices=[('upvote', 'Upvote'), ('downvote', 'Downvote')])

    def validate_message_id(self, value):
        """Validate message exists"""
        try:
            Message.objects.get(id=value)
        except Message.DoesNotExist:
            raise serializers.ValidationError("Message does not exist")
        return value



class MessageRankingSerializer(serializers.ModelSerializer):
    """Serializer for MessageRanking model"""
    
    message_id = serializers.IntegerField(source='message.id', read_only=True)
    total_votes = serializers.SerializerMethodField()
    upvote_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = MessageRanking
        fields = [
            'message_id',
            'upvotes',
            'downvotes',
            'total_votes',
            'upvote_percentage',
            'wilson_score',
            'last_calculated'
        ]
        read_only_fields = fields
    
    def get_total_votes(self, obj):
        """Get total vote count"""
        return obj.upvotes + obj.downvotes
    
    def get_upvote_percentage(self, obj):
        """Get upvote percentage"""
        total = obj.upvotes + obj.downvotes
        if total == 0:
            return 0.0
        return round((obj.upvotes / total) * 100, 1)


class LeaderboardEntrySerializer(serializers.Serializer):
    """Serializer for leaderboard entries"""
    
    rank = serializers.IntegerField()
    user_id = serializers.IntegerField()
    username = serializers.CharField()
    reputation_score = serializers.FloatField()
    rank_tier = serializers.CharField()
    level = serializers.IntegerField()
    total_upvotes_received = serializers.IntegerField()


class PrivilegeInfoSerializer(serializers.Serializer):
    """Serializer for privilege information"""
    
    action = serializers.CharField()
    has_privilege = serializers.BooleanField()
    current_tier = serializers.CharField()
    required_tier = serializers.CharField()
    current_score = serializers.FloatField()
    all_privileges = serializers.ListField(child=serializers.CharField())


class TierUpdateSerializer(serializers.Serializer):
    """Serializer for tier update information"""
    
    tier_changed = serializers.BooleanField()
    old_tier = serializers.CharField()
    new_tier = serializers.CharField()
    tier_upgrade = serializers.BooleanField()
    new_privileges = serializers.ListField(child=serializers.CharField(), required=False)
    message = serializers.CharField()


class VoteResultSerializer(serializers.Serializer):
    """Serializer for vote operation results"""
    
    success = serializers.BooleanField()
    vote_type = serializers.CharField(required=False)
    error = serializers.CharField(required=False)
    ranking_data = serializers.DictField(required=False)

    reputation_update = serializers.DictField(required=False)
    tier_update = TierUpdateSerializer(required=False)
    privilege_info = PrivilegeInfoSerializer(required=False)


class ContentRankingSerializer(serializers.Serializer):
    """Serializer for content ranking results"""
    
    message_id = serializers.IntegerField()
    content = serializers.CharField()
    sender_id = serializers.UUIDField()
    chatroom_id = serializers.IntegerField()
    chatroom_name = serializers.CharField()
    wilson_score = serializers.FloatField()
    upvotes = serializers.IntegerField()
    downvotes = serializers.IntegerField()
    total_votes = serializers.IntegerField()
    created_at = serializers.DateTimeField()