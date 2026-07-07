from rest_framework import serializers
from .models import Chatroom, Message, MessageReaction, ReadReceipt, Poll, PollVote, Confession
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


class MessageRankingInfoSerializer(serializers.Serializer):
    """Serializer for message ranking information"""
    
    upvotes = serializers.IntegerField(default=0)
    downvotes = serializers.IntegerField(default=0)
    total_votes = serializers.IntegerField(default=0)
    wilson_score = serializers.FloatField(default=0.0)
    upvote_percentage = serializers.FloatField(default=0.0)
    user_vote = serializers.CharField(allow_null=True, default=None)  # 'upvote', 'downvote', or None


class MessageSerializer(serializers.ModelSerializer):
    """Serializer for Message model"""
    
    sender_id = serializers.UUIDField(source='sender.anonymous_id', read_only=True)
    reactions = MessageReactionSerializer(many=True, read_only=True)
    reaction_count = serializers.SerializerMethodField()
    media_url = serializers.SerializerMethodField()
    ranking = serializers.SerializerMethodField()
    
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
            'reaction_count',
            'ranking'
        ]
        read_only_fields = [
            'id',
            'sender_id',
            'is_edited',
            'is_deleted',
            'created_at',
            'updated_at',
            'reactions',
            'reaction_count',
            'ranking'
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
    
    def get_ranking(self, obj):
        """Get ranking information for the message"""
        try:
            from reputation.models import MessageRanking, Vote
            
            # Get ranking data
            try:
                ranking = MessageRanking.objects.get(message=obj)
                upvotes = ranking.upvotes
                downvotes = ranking.downvotes
                wilson_score = ranking.wilson_score
            except MessageRanking.DoesNotExist:
                upvotes = downvotes = wilson_score = 0
            
            total_votes = upvotes + downvotes
            upvote_percentage = (upvotes / total_votes * 100) if total_votes > 0 else 0.0
            
            # Get user's vote if request context available
            user_vote = None
            request = self.context.get('request')
            if request and hasattr(request, 'user') and request.user.is_authenticated:
                try:
                    vote = Vote.objects.get(user=request.user, message=obj)
                    user_vote = vote.vote_type
                except Vote.DoesNotExist:
                    pass
            
            return {
                'upvotes': upvotes,
                'downvotes': downvotes,
                'total_votes': total_votes,
                'wilson_score': round(wilson_score, 4),
                'upvote_percentage': round(upvote_percentage, 1),
                'user_vote': user_vote
            }
        except ImportError:
            # Reputation app not available, return default values
            return {
                'upvotes': 0,
                'downvotes': 0,
                'total_votes': 0,
                'wilson_score': 0.0,
                'upvote_percentage': 0.0,
                'user_vote': None
            }


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


class PollSerializer(serializers.ModelSerializer):
    """Serializer for Poll model"""
    
    creator_id = serializers.UUIDField(source='creator.anonymous_id', read_only=True)
    vote_counts = serializers.SerializerMethodField()
    total_votes = serializers.SerializerMethodField()
    user_vote = serializers.SerializerMethodField()
    
    class Meta:
        model = Poll
        fields = [
            'id',
            'chatroom',
            'creator_id',
            'question',
            'options',
            'is_active',
            'expires_at',
            'created_at',
            'vote_counts',
            'total_votes',
            'user_vote'
        ]
        read_only_fields = ['id', 'creator_id', 'created_at', 'vote_counts', 'total_votes', 'user_vote']
    
    def get_vote_counts(self, obj):
        """Get vote counts for each option"""
        from .models import PollVote
        votes = PollVote.objects.filter(poll=obj)
        counts = {}
        for i, option in enumerate(obj.options):
            counts[i] = votes.filter(option_index=i).count()
        return counts
    
    def get_total_votes(self, obj):
        """Get total vote count"""
        from .models import PollVote
        return PollVote.objects.filter(poll=obj).count()
    
    def get_user_vote(self, obj):
        """Get current user's vote if available"""
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            try:
                profile = request.user.profile
                from .models import PollVote
                vote = PollVote.objects.get(poll=obj, voter=profile)
                return vote.option_index
            except:
                pass
        return None


class PollCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating polls"""
    
    class Meta:
        model = Poll
        fields = ['question', 'options', 'expires_at']
    
    def validate_options(self, value):
        """Validate poll options"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Options must be a list")
        if len(value) < 2:
            raise serializers.ValidationError("Poll must have at least 2 options")
        if len(value) > 10:
            raise serializers.ValidationError("Poll cannot have more than 10 options")
        for option in value:
            if not isinstance(option, str) or not option.strip():
                raise serializers.ValidationError("All options must be non-empty strings")
        return value


class PollVoteSerializer(serializers.Serializer):
    """Serializer for voting on polls"""
    
    option_index = serializers.IntegerField(min_value=0)
    
    def validate_option_index(self, value):
        """Validate option index is within poll options"""
        poll = self.context.get('poll')
        if poll and value >= len(poll.options):
            raise serializers.ValidationError("Invalid option index")
        return value


class ConfessionSerializer(serializers.ModelSerializer):
    """Serializer for Confession model"""
    
    class Meta:
        model = Confession
        fields = [
            'id',
            'chatroom',
            'content',
            'is_approved',
            'is_active',
            'created_at',
            'approved_at'
        ]
        read_only_fields = ['id', 'is_approved', 'created_at', 'approved_at']


class ConfessionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating confessions"""
    
    class Meta:
        model = Confession
        fields = ['content']
    
    def validate_content(self, value):
        """Validate confession content"""
        if not value or not value.strip():
            raise serializers.ValidationError("Confession content cannot be empty")
        if len(value) > 1000:
            raise serializers.ValidationError("Confession content too long (max 1000 characters)")
        return value
