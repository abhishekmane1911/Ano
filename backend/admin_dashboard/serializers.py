"""
Serializers for admin dashboard API endpoints
"""
from rest_framework import serializers
from reports.models import Report
from profiles.models import Profile
from authentication.models import User
from chat.models import Message, Chatroom
from matchmaking.models import Match
from django.db.models import Count, Q
from django.utils import timezone


class AdminReportSerializer(serializers.ModelSerializer):
    """Serializer for reports in admin dashboard - uses anonymous IDs only"""
    reporter_anonymous_id = serializers.UUIDField(source='reporter.anonymous_id', read_only=True)
    reported_anonymous_id = serializers.UUIDField(source='reported.anonymous_id', read_only=True)
    reviewed_by_email = serializers.EmailField(source='reviewed_by.email', read_only=True, allow_null=True)
    
    class Meta:
        model = Report
        fields = [
            'id',
            'reporter_anonymous_id',
            'reported_anonymous_id',
            'reason',
            'description',
            'status',
            'created_at',
            'reviewed_by_email',
            'reviewed_at',
        ]
        read_only_fields = ['id', 'created_at', 'reporter_anonymous_id', 'reported_anonymous_id']


class AdminReportUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating report status"""
    
    class Meta:
        model = Report
        fields = ['status']
    
    def validate_status(self, value):
        """Validate status is one of the allowed choices"""
        if value not in ['pending', 'reviewed', 'resolved']:
            raise serializers.ValidationError("Invalid status. Must be 'pending', 'reviewed', or 'resolved'.")
        return value
    
    def update(self, instance, validated_data):
        """Update report status and set reviewed_by and reviewed_at"""
        instance.status = validated_data.get('status', instance.status)
        
        # Set reviewed_by and reviewed_at if status is being changed from pending
        if instance.status != 'pending' and not instance.reviewed_by:
            instance.reviewed_by = self.context['request'].user
            instance.reviewed_at = timezone.now()
        
        instance.save()
        return instance


class AdminUserDetailSerializer(serializers.ModelSerializer):
    """Serializer for user details in admin dashboard - anonymous IDs only"""
    anonymous_id = serializers.UUIDField(read_only=True)
    age = serializers.IntegerField(read_only=True)
    interests = serializers.JSONField(read_only=True)
    hobbies = serializers.JSONField(read_only=True)
    relationship_intent = serializers.CharField(read_only=True)
    personality_tags = serializers.JSONField(read_only=True)
    bio = serializers.CharField(read_only=True)
    
    # Statistics
    reports_received_count = serializers.IntegerField(read_only=True)
    reports_made_count = serializers.IntegerField(read_only=True)
    messages_sent_count = serializers.IntegerField(read_only=True)
    matches_count = serializers.IntegerField(read_only=True)
    
    # User account info (no email exposed)
    is_active = serializers.BooleanField(source='user.is_active', read_only=True)
    date_joined = serializers.DateTimeField(source='user.date_joined', read_only=True)
    last_login = serializers.DateTimeField(source='user.last_login', read_only=True)
    
    class Meta:
        model = Profile
        fields = [
            'anonymous_id',
            'age',
            'interests',
            'hobbies',
            'relationship_intent',
            'personality_tags',
            'bio',
            'reports_received_count',
            'reports_made_count',
            'messages_sent_count',
            'matches_count',
            'is_active',
            'date_joined',
            'last_login',
        ]


class AdminUserBanSerializer(serializers.Serializer):
    """Serializer for banning a user"""
    reason = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        """Validate ban request"""
        return data


class AdminBroadcastMessageSerializer(serializers.Serializer):
    """Serializer for broadcasting messages to all chatrooms"""
    content = serializers.CharField(required=True, max_length=1000)
    chatroom_id = serializers.UUIDField(required=False, allow_null=True)
    
    def validate_content(self, value):
        """Validate message content is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Message content cannot be empty.")
        return value.strip()
    
    def validate_chatroom_id(self, value):
        """Validate chatroom exists if provided"""
        if value:
            try:
                Chatroom.objects.get(id=value)
            except Chatroom.DoesNotExist:
                raise serializers.ValidationError("Chatroom does not exist.")
        return value


class AdminPlatformMetricsSerializer(serializers.Serializer):
    """Serializer for platform health metrics"""
    active_users_today = serializers.IntegerField(read_only=True)
    active_users_week = serializers.IntegerField(read_only=True)
    total_users = serializers.IntegerField(read_only=True)
    total_profiles = serializers.IntegerField(read_only=True)
    total_messages_today = serializers.IntegerField(read_only=True)
    total_messages_week = serializers.IntegerField(read_only=True)
    total_messages = serializers.IntegerField(read_only=True)
    total_matches = serializers.IntegerField(read_only=True)
    total_reports_pending = serializers.IntegerField(read_only=True)
    total_reports = serializers.IntegerField(read_only=True)
    total_chatrooms = serializers.IntegerField(read_only=True)
