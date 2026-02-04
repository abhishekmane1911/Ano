import logging
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count
from django.core.mail import send_mail
from django.conf import settings
from .models import Report, Block
from .serializers import ReportSerializer, BlockSerializer, BlockedUserSerializer
from profiles.models import Profile
from ano_backend.logging_config import get_anonymous_id_from_user

# Get loggers
logger = logging.getLogger('ano_platform')
security_logger = logging.getLogger('ano_platform.security')


class ReportCreateView(generics.CreateAPIView):
    """Create a new report"""
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        report = serializer.save()
        
        # Log report creation with anonymous IDs
        reporter_id = get_anonymous_id_from_user(self.request.user)
        security_logger.warning(
            f"Report created - Reporter: {reporter_id}, "
            f"Reported: {report.reported.anonymous_id}, "
            f"Reason: {report.reason}"
        )
        
        # Check for report escalation
        reported_profile = report.reported
        report_count = Report.objects.filter(
            reported=reported_profile,
            status='pending'
        ).count()
        
        # Escalate if user has received 3 or more pending reports
        ESCALATION_THRESHOLD = 3
        if report_count >= ESCALATION_THRESHOLD:
            security_logger.error(
                f"Report escalation triggered for {reported_profile.anonymous_id} "
                f"with {report_count} pending reports"
            )
            self._send_escalation_notification(reported_profile, report_count)
    
    def _send_escalation_notification(self, reported_profile, report_count):
        """Send notification to admins about escalated reports"""
        subject = f'Report Escalation: User {reported_profile.anonymous_id}'
        message = f'''
A user has received {report_count} pending reports and requires administrative review.

Anonymous ID: {reported_profile.anonymous_id}
Total Pending Reports: {report_count}

Please review the reports in the admin dashboard.
        '''
        
        # Get admin emails
        from authentication.models import User
        admin_emails = User.objects.filter(is_staff=True).values_list('email', flat=True)
        
        if admin_emails:
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    list(admin_emails),
                    fail_silently=True,
                )
            except Exception as e:
                # Log error but don't fail the request
                print(f"Failed to send escalation email: {e}")


class BlockCreateView(generics.CreateAPIView):
    """Block a user"""
    serializer_class = BlockSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        block = serializer.save()
        
        # Log block creation with anonymous IDs
        blocker_id = get_anonymous_id_from_user(self.request.user)
        security_logger.warning(
            f"User blocked - Blocker: {blocker_id}, "
            f"Blocked: {block.blocked.anonymous_id}"
        )


class BlockedUsersListView(generics.ListAPIView):
    """List all blocked users for the current user"""
    serializer_class = BlockedUserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        try:
            user_profile = self.request.user.profile
            return Block.objects.filter(blocker=user_profile).select_related('blocked')
        except Profile.DoesNotExist:
            # User doesn't have a profile yet, return empty queryset
            return Block.objects.none()


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def unblock_user(request, anonymous_id):
    """Unblock a user by their anonymous ID"""
    try:
        # Check if user has a profile
        try:
            user_profile = request.user.profile
        except Profile.DoesNotExist:
            return Response(
                {'error': 'User profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        blocked_profile = Profile.objects.get(anonymous_id=anonymous_id)
        
        # Find and delete the block
        block = Block.objects.filter(
            blocker=user_profile,
            blocked=blocked_profile
        ).first()
        
        if not block:
            return Response(
                {'error': 'Block not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        block.delete()
        
        # Log unblock with anonymous IDs
        blocker_id = get_anonymous_id_from_user(request.user)
        logger.info(
            f"User unblocked - Blocker: {blocker_id}, "
            f"Unblocked: {blocked_profile.anonymous_id}"
        )
        
        return Response(
            {'message': 'User unblocked successfully'},
            status=status.HTTP_200_OK
        )
    
    except Profile.DoesNotExist:
        return Response(
            {'error': 'Profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )
