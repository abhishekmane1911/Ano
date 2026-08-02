"""
Serializers for moderation app.
"""

from rest_framework import serializers
from .models import ViolationHistory, Shadowban, ModerationResult


class ViolationHistorySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ViolationHistory
        fields = [
            'id', 'violation_type', 'toxicity_score', 'content_snippet',
            'action_taken', 'is_active', 'expires_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ShadowbanSerializer(serializers.ModelSerializer):
    
    time_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = Shadowban
        fields = [
            'id', 'reason', 'duration_hours', 'created_at', 
            'expires_at', 'is_active', 'time_remaining'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_time_remaining(self, obj):
        if not obj.is_active or obj.is_expired():
            return None
        
        from django.utils import timezone
        remaining = obj.expires_at - timezone.now()
        return {
            'total_seconds': int(remaining.total_seconds()),
            'hours': int(remaining.total_seconds() // 3600),
            'minutes': int((remaining.total_seconds() % 3600) // 60)
        }


class ModerationResultSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ModerationResult
        fields = [
            'id', 'toxicity_score', 'flagged_categories', 
            'action_taken', 'processed_at'
        ]
        read_only_fields = ['id', 'processed_at']


class HeatInfoSerializer(serializers.Serializer):
    
    heat_level = serializers.IntegerField()
    heat_name = serializers.CharField()
    penalty_multiplier = serializers.FloatField()
    recent_violations = serializers.IntegerField()
    rehabilitation_progress = serializers.FloatField()
    is_shadowbanned = serializers.BooleanField()
    shadowban_expires = serializers.DateTimeField(allow_null=True)
    next_level_violations = serializers.IntegerField(allow_null=True)
    can_rehabilitate = serializers.BooleanField()


class ReportContentSerializer(serializers.Serializer):
    
    content_type = serializers.ChoiceField(choices=['message', 'post', 'comment'])
    content_id = serializers.IntegerField()
    reason = serializers.ChoiceField(
        choices=[
            ('spam', 'Spam'),
            ('harassment', 'Harassment'),
            ('violence', 'Violence'),
            ('inappropriate', 'Inappropriate Content'),
            ('other', 'Other')
        ],
        default='inappropriate'
    )
    description = serializers.CharField(max_length=500, required=False, allow_blank=True)