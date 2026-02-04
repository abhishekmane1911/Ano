"""
Views for admin dashboard API endpoints
"""
import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from reports.models import Report
from profiles.models import Profile
from authentication.models import User
from chat.models import Message, Chatroom
from matchmaking.models import Match

from .serializers import (
    AdminReportSerializer,
    AdminReportUpdateSerializer,
    AdminUserDetailSerializer,
    AdminUserBanSerializer,
    AdminBroadcastMessageSerializer,
    AdminPlatformMetricsSerializer,
)
from ano_backend.logging_config import get_anonymous_id_from_user

# Get loggers
logger = logging.getLogger('ano_platform')
security_logger = logging.getLogger('ano_platform.security')


class AdminPagination(PageNumberPagination):
    """Custom pagination for admin endpoints"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def list_reports(request):
    """
    List all reports with filtering options
    
    Query parameters:
    - status: Filter by status (pending, reviewed, resolved)
    - ordering: Order by field (created_at, -created_at)
    """
    # Get query parameters
    status_filter = request.query_params.get('status', None)
    ordering = request.query_params.get('ordering', '-created_at')
    
    # Build queryset
    queryset = Report.objects.select_related(
        'reporter',
        'reported',
        'reviewed_by'
    ).all()
    
    # Apply filters
    if status_filter:
        queryset = queryset.filter(status=status_filter)
    
    # Apply ordering
    if ordering:
        queryset = queryset.order_by(ordering)
    
    # Paginate
    paginator = AdminPagination()
    page = paginator.paginate_queryset(queryset, request)
    
    if page is not None:
        serializer = AdminReportSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    serializer = AdminReportSerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated, IsAdminUser])
def update_report(request, report_id):
    """
    Update report status
    
    Body:
    - status: New status (pending, reviewed, resolved)
    """
    try:
        report = Report.objects.select_related('reporter', 'reported', 'reviewed_by').get(id=report_id)
    except Report.DoesNotExist:
        return Response(
            {'error': 'Report not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = AdminReportUpdateSerializer(
        report,
        data=request.data,
        partial=True,
        context={'request': request}
    )
    
    if serializer.is_valid():
        old_status = report.status
        serializer.save()
        
        # Log report status update with anonymous IDs
        admin_id = get_anonymous_id_from_user(request.user)
        security_logger.info(
            f"Report updated by admin {admin_id or f'user_{request.user.id}'} - "
            f"Report ID: {report.id}, "
            f"Reported user: {report.reported.anonymous_id}, "
            f"Status: {old_status} -> {report.status}"
        )
        
        # Return full report data
        response_serializer = AdminReportSerializer(report)
        return Response(response_serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_user_detail(request, anonymous_id):
    """
    Get user details for moderation using anonymous ID
    
    Returns profile information and statistics without exposing email or real name
    """
    try:
        profile = Profile.objects.select_related('user').get(anonymous_id=anonymous_id)
    except Profile.DoesNotExist:
        return Response(
            {'error': 'Profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Annotate with statistics
    profile.reports_received_count = Report.objects.filter(reported=profile).count()
    profile.reports_made_count = Report.objects.filter(reporter=profile).count()
    profile.messages_sent_count = Message.objects.filter(sender=profile).count()
    profile.matches_count = Match.objects.filter(
        Q(profile1=profile) | Q(profile2=profile),
        is_active=True
    ).count()
    
    serializer = AdminUserDetailSerializer(profile)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def ban_user(request, anonymous_id):
    """
    Ban a user by setting their account to inactive
    
    Body:
    - reason: Optional reason for the ban
    """
    try:
        profile = Profile.objects.select_related('user').get(anonymous_id=anonymous_id)
    except Profile.DoesNotExist:
        return Response(
            {'error': 'Profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = AdminUserBanSerializer(data=request.data)
    
    if serializer.is_valid():
        # Deactivate the user account
        user = profile.user
        user.is_active = False
        user.save()
        
        # Log ban action with anonymous IDs
        admin_id = get_anonymous_id_from_user(request.user)
        reason = serializer.validated_data.get('reason', 'No reason provided')
        security_logger.error(
            f"User banned by admin {admin_id or f'user_{request.user.id}'} - "
            f"Banned user: {anonymous_id}, "
            f"Reason: {reason}"
        )
        
        return Response({
            'message': 'User banned successfully',
            'anonymous_id': str(anonymous_id),
            'reason': reason
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def broadcast_message(request):
    """
    Send a broadcast message to a chatroom or all chatrooms
    
    Body:
    - content: Message content (required)
    - chatroom_id: Optional chatroom ID (if not provided, broadcasts to all)
    """
    serializer = AdminBroadcastMessageSerializer(data=request.data)
    
    if serializer.is_valid():
        content = serializer.validated_data['content']
        chatroom_id = serializer.validated_data.get('chatroom_id')
        
        # Get admin profile (create if doesn't exist)
        admin_profile, created = Profile.objects.get_or_create(
            user=request.user,
            defaults={
                'age': 25,
                'relationship_intent': 'friendship',
                'interests': [],
                'hobbies': [],
                'personality_tags': []
            }
        )
        
        # Determine target chatrooms
        if chatroom_id:
            chatrooms = Chatroom.objects.filter(id=chatroom_id, is_active=True)
            if not chatrooms.exists():
                return Response(
                    {'error': 'Chatroom not found or inactive'},
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            chatrooms = Chatroom.objects.filter(is_active=True)
        
        # Create broadcast messages
        messages_created = []
        for chatroom in chatrooms:
            message = Message.objects.create(
                chatroom=chatroom,
                sender=admin_profile,
                content=f"[ADMIN BROADCAST] {content}",
                message_type='system'
            )
            messages_created.append(str(message.id))
        
        return Response({
            'message': 'Broadcast sent successfully',
            'chatrooms_count': len(messages_created),
            'message_ids': messages_created
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def get_platform_metrics(request):
    """
    Get platform health metrics
    
    Returns:
    - Active users (today, this week, total)
    - Message volume (today, this week, total)
    - Total matches
    - Pending reports
    - Total chatrooms
    """
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)
    
    # Calculate metrics
    metrics = {
        # User metrics
        'active_users_today': User.objects.filter(
            last_login__gte=today_start,
            is_active=True
        ).count(),
        'active_users_week': User.objects.filter(
            last_login__gte=week_start,
            is_active=True
        ).count(),
        'total_users': User.objects.filter(is_active=True).count(),
        'total_profiles': Profile.objects.count(),
        
        # Message metrics
        'total_messages_today': Message.objects.filter(
            created_at__gte=today_start,
            is_deleted=False
        ).count(),
        'total_messages_week': Message.objects.filter(
            created_at__gte=week_start,
            is_deleted=False
        ).count(),
        'total_messages': Message.objects.filter(is_deleted=False).count(),
        
        # Match metrics
        'total_matches': Match.objects.filter(is_active=True).count(),
        
        # Report metrics
        'total_reports_pending': Report.objects.filter(status='pending').count(),
        'total_reports': Report.objects.count(),
        
        # Chatroom metrics
        'total_chatrooms': Chatroom.objects.filter(is_active=True).count(),
    }
    
    serializer = AdminPlatformMetricsSerializer(metrics)
    return Response(serializer.data)
