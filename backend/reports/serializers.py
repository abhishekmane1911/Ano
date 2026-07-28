from rest_framework import serializers
from .models import Report, Block
from profiles.models import Profile


class ReportSerializer(serializers.ModelSerializer):
    """Serializer for Report model with anonymous identifiers"""
    
    reporter_id = serializers.UUIDField(source='reporter.anonymous_id', read_only=True)
    reported_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Report
        fields = [
            'id',
            'reporter_id',
            'reported_id',
            'reason',
            'description',
            'status',
            'created_at',
            'reviewed_at',
        ]
        read_only_fields = ['id', 'reporter_id', 'status', 'created_at', 'reviewed_at']
    
    def validate_reported_id(self, value):
        """Validate that the reported profile exists"""
        try:
            Profile.objects.get(anonymous_id=value)
        except Profile.DoesNotExist:
            raise serializers.ValidationError("Profile not found")
        return value
    
    def create(self, validated_data):
        """Create report with reporter from context"""
        reported_id = validated_data.pop('reported_id')
        reported_profile = Profile.objects.get(anonymous_id=reported_id)
        
        try:
            reporter_profile = self.context['request'].user.profile
        except Profile.DoesNotExist:
            raise serializers.ValidationError("User profile not found")
        

        if reporter_profile == reported_profile:
            raise serializers.ValidationError("Cannot report yourself")
        
        report = Report.objects.create(
            reporter=reporter_profile,
            reported=reported_profile,
            **validated_data
        )
        return report


class BlockSerializer(serializers.ModelSerializer):
    """Serializer for Block model with anonymous identifiers"""
    
    blocker_id = serializers.UUIDField(source='blocker.anonymous_id', read_only=True)
    blocked_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Block
        fields = [
            'id',
            'blocker_id',
            'blocked_id',
            'created_at',
        ]
        read_only_fields = ['id', 'blocker_id', 'created_at']
    
    def validate_blocked_id(self, value):
        """Validate that the blocked profile exists"""
        try:
            Profile.objects.get(anonymous_id=value)
        except Profile.DoesNotExist:
            raise serializers.ValidationError("Profile not found")
        return value
    
    def create(self, validated_data):
        """Create block with blocker from context"""
        blocked_id = validated_data.pop('blocked_id')
        blocked_profile = Profile.objects.get(anonymous_id=blocked_id)
        
        try:
            blocker_profile = self.context['request'].user.profile
        except Profile.DoesNotExist:
            raise serializers.ValidationError("User profile not found")

        if blocker_profile == blocked_profile:
            raise serializers.ValidationError("Cannot block yourself")
        
        if Block.objects.filter(blocker=blocker_profile, blocked=blocked_profile).exists():
            raise serializers.ValidationError("User already blocked")
        
        block = Block.objects.create(
            blocker=blocker_profile,
            blocked=blocked_profile,
        )
        return block


class BlockedUserSerializer(serializers.ModelSerializer):
    """Serializer for listing blocked users"""
    
    anonymous_id = serializers.UUIDField(source='blocked.anonymous_id', read_only=True)
    blocked_at = serializers.DateTimeField(source='created_at', read_only=True)
    
    class Meta:
        model = Block
        fields = ['id', 'anonymous_id', 'blocked_at']
        read_only_fields = ['id', 'anonymous_id', 'blocked_at']
