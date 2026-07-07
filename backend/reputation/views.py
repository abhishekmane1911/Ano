"""
Views for reputation app.
"""

from rest_framework import status, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.db.models import Q, F
from django.shortcuts import get_object_or_404
from django.core.paginator import Paginator

from .models import UserReputation, Vote, MessageRanking
from .serializers import (
    UserReputationSerializer, VoteSerializer, VoteCreateSerializer,
    MessageRankingSerializer, LeaderboardEntrySerializer, PrivilegeInfoSerializer,
    VoteResultSerializer, ContentRankingSerializer
)
from .services import VotingService, TierPrivilegeManager, ReputationService
from .middleware import ReputationTrackingMixin
from chat.models import Message

User = get_user_model()


class VoteAPIView(ReputationTrackingMixin, APIView):
    """API view for casting votes on messages"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Cast a vote on a message"""
        serializer = VoteCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        message_id = serializer.validated_data['message_id']
        vote_type = serializer.validated_data['vote_type']
        
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Cast vote using VotingService
        result = VotingService.cast_vote(request.user, message, vote_type)
        
        # Serialize result
        result_serializer = VoteResultSerializer(result)
        
        if result['success']:
            return Response(result_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(result_serializer.data, status=status.HTTP_403_FORBIDDEN)


class VoteDetailAPIView(APIView):
    """API view for getting vote details for a specific message"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, message_id):
        """Get vote information for a message"""
        try:
            message = Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get user's vote if exists
        user_vote = None
        try:
            vote = Vote.objects.get(user=request.user, message=message)
            user_vote = VoteSerializer(vote).data
        except Vote.DoesNotExist:
            pass
        
        # Get message ranking
        try:
            ranking = MessageRanking.objects.get(message=message)
            ranking_data = MessageRankingSerializer(ranking).data
        except MessageRanking.DoesNotExist:
            ranking_data = {
                'message_id': message_id,
                'upvotes': 0,
                'downvotes': 0,
                'total_votes': 0,
                'upvote_percentage': 0.0,
                'wilson_score': 0.0,
                'last_calculated': None
            }
        
        return Response({
            'message_id': message_id,
            'user_vote': user_vote,
            'ranking': ranking_data
        })


class UserReputationAPIView(APIView):
    """API view for getting user reputation information"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, user_id):
        """Get reputation information for a specific user"""
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        reputation = ReputationService.get_or_create_reputation(user)
        serializer = UserReputationSerializer(reputation)
        return Response(serializer.data)


class MyReputationAPIView(APIView):
    """API view for getting current user's reputation information"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get current user's reputation information"""
        reputation = ReputationService.get_or_create_reputation(request.user)
        serializer = UserReputationSerializer(reputation)
        return Response(serializer.data)


class LeaderboardViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for reputation leaderboard"""
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LeaderboardEntrySerializer
    
    def get_queryset(self):
        """Get leaderboard data"""
        # Get top users by reputation score
        reputations = UserReputation.objects.select_related('user').order_by('-reputation_score')[:100]
        
        leaderboard_data = []
        for rank, reputation in enumerate(reputations, 1):
            leaderboard_data.append({
                'rank': rank,
                'user_id': reputation.user.id,
                'username': reputation.user.username,
                'reputation_score': reputation.reputation_score,
                'rank_tier': reputation.rank_tier,
                'level': reputation.calculate_level(),
                'total_upvotes_received': reputation.total_upvotes_received
            })
        
        return leaderboard_data
    
    def list(self, request):
        """List leaderboard entries"""
        queryset = self.get_queryset()
        
        # Apply pagination
        page = request.query_params.get('page', 1)
        page_size = min(int(request.query_params.get('page_size', 20)), 100)
        
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        
        serializer = self.get_serializer(page_obj.object_list, many=True)
        
        return Response({
            'count': paginator.count,
            'num_pages': paginator.num_pages,
            'current_page': page_obj.number,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
            'results': serializer.data
        })


class ContentRankingsAPIView(APIView):
    """API view for getting content rankings"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get ranked content based on Wilson Scores"""
        # Get query parameters
        chatroom_id = request.query_params.get('chatroom_id')
        limit = min(int(request.query_params.get('limit', 50)), 100)
        
        # Build query
        rankings_query = MessageRanking.objects.select_related(
            'message', 'message__sender', 'message__chatroom'
        ).order_by('-wilson_score')
        
        if chatroom_id:
            rankings_query = rankings_query.filter(message__chatroom_id=chatroom_id)
        
        # Get top ranked messages
        rankings = rankings_query[:limit]
        
        # Serialize data
        ranked_content = []
        for ranking in rankings:
            message = ranking.message
            ranked_content.append({
                'message_id': message.id,
                'content': message.content,
                'sender_id': message.sender.anonymous_id,
                'chatroom_id': message.chatroom.id,
                'chatroom_name': message.chatroom.name,
                'wilson_score': ranking.wilson_score,
                'upvotes': ranking.upvotes,
                'downvotes': ranking.downvotes,
                'total_votes': ranking.upvotes + ranking.downvotes,
                'created_at': message.created_at
            })
        
        serializer = ContentRankingSerializer(ranked_content, many=True)
        return Response(serializer.data)


class UserPrivilegesAPIView(APIView):
    """API view for getting user privileges"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get current user's privileges"""
        privileges = TierPrivilegeManager.get_user_privileges(request.user)
        reputation = ReputationService.get_or_create_reputation(request.user)
        
        return Response({
            'user_id': request.user.id,
            'current_tier': reputation.rank_tier,
            'current_score': reputation.reputation_score,
            'level': reputation.calculate_level(),
            'privileges': privileges,
            'tier_privileges': TierPrivilegeManager.TIER_PRIVILEGES
        })


class CheckPrivilegeAPIView(APIView):
    """API view for checking specific privileges"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Check if user has specific privilege"""
        action = request.data.get('action')
        if not action:
            return Response({'error': 'Action is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        privilege_info = TierPrivilegeManager.get_privilege_info(request.user, action)
        serializer = PrivilegeInfoSerializer(privilege_info)
        return Response(serializer.data)


# Utility views for integration with existing chat system

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def message_ranking_view(request, message_id):
    """Get ranking information for a specific message"""
    try:
        message = Message.objects.get(id=message_id)
    except Message.DoesNotExist:
        return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        ranking = MessageRanking.objects.get(message=message)
        serializer = MessageRankingSerializer(ranking)
        return Response(serializer.data)
    except MessageRanking.DoesNotExist:
        # Return default ranking data
        return Response({
            'message_id': message_id,
            'upvotes': 0,
            'downvotes': 0,
            'total_votes': 0,
            'upvote_percentage': 0.0,
            'wilson_score': 0.0,
            'last_calculated': None
        })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def update_message_ranking_view(request, message_id):
    """Force update ranking for a specific message"""
    try:
        message = Message.objects.get(id=message_id)
    except Message.DoesNotExist:
        return Response({'error': 'Message not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Update ranking
    from .services import WilsonScoreCalculator
    wilson_score = WilsonScoreCalculator.update_message_ranking(message)
    
    # Get updated ranking
    ranking = MessageRanking.objects.get(message=message)
    serializer = MessageRankingSerializer(ranking)
    
    return Response({
        'message': 'Ranking updated successfully',
        'ranking': serializer.data
    })