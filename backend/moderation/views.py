"""
Views for moderation app with heat system integration.
"""

from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.utils import timezone
from .services import ModerationService, HeatSystem
from .models import ViolationHistory, Shadowban, ModerationResult
from .serializers import ViolationHistorySerializer, ShadowbanSerializer, HeatInfoSerializer

User = get_user_model()


class ModerationStatusAPIView(APIView):
    """API view for checking moderation status with heat system info"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get comprehensive moderation status for current user"""
        user = request.user
        
        heat_info = HeatSystem.get_heat_info(user)
        
        recent_violations = ViolationHistory.objects.filter(
            user=user,
            is_active=True
        ).order_by('-created_at')[:5]
        
        active_shadowban = Shadowban.objects.filter(
            user=user,
            is_active=True,
            expires_at__gt=timezone.now()
        ).first()
        
        return Response({
            'user_id': user.id,
            'heat_system': heat_info,
            'recent_violations': ViolationHistorySerializer(recent_violations, many=True).data,
            'shadowban': ShadowbanSerializer(active_shadowban).data if active_shadowban else None,
            'escalation_warning': HeatSystem.get_escalation_warning(user)
        })


class HeatSystemAPIView(APIView):
    """API view for heat system management"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get detailed heat system information"""
        user = request.user
        heat_info = HeatSystem.get_heat_info(user)
        
        return Response({
            'heat_info': heat_info,
            'escalation_warning': HeatSystem.get_escalation_warning(user),
            'rehabilitation_available': heat_info['can_rehabilitate']
        })
    
    def post(self, request):
        """Attempt rehabilitation (if eligible)"""
        user = request.user
        
        if HeatSystem.attempt_rehabilitation(user):
            new_heat_info = HeatSystem.get_heat_info(user)
            return Response({
                'message': 'Rehabilitation successful',
                'new_heat_info': new_heat_info
            })
        else:
            return Response({
                'error': 'Rehabilitation not available',
                'reason': 'Not enough good behavior time or already at minimum heat level'
            }, status=status.HTTP_400_BAD_REQUEST)


class ReportContentAPIView(APIView):
    """API view for reporting content"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Report content for moderation"""
        content_type = request.data.get('content_type') 
        content_id = request.data.get('content_id')
        reason = request.data.get('reason', 'inappropriate')
        description = request.data.get('description', '')
        
        # TODO: Implement actual reporting logic
        # This would create a report record and queue for admin review
        
        return Response({
            'message': 'Content reported successfully',
            'report_id': f'report_{content_type}_{content_id}',
            'status': 'pending_review'
        }, status=status.HTTP_201_CREATED)


class UserViolationsAPIView(APIView):
    """API view for getting user violations"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get user's violation history with pagination"""
        user = request.user
        page_size = int(request.query_params.get('page_size', 10))
        page = int(request.query_params.get('page', 1))
        
        violations = ViolationHistory.objects.filter(user=user).order_by('-created_at')
        total_count = violations.count()
        
        start = (page - 1) * page_size
        end = start + page_size
        page_violations = violations[start:end]
        
        return Response({
            'violations': ViolationHistorySerializer(page_violations, many=True).data,
            'total_count': total_count,
            'page': page,
            'page_size': page_size,
            'has_next': end < total_count
        })


class ShadowbanStatusAPIView(APIView):
    """API view for checking shadowban status"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Get shadowban status for current user"""
        user = request.user
        is_shadowbanned = ModerationService.is_user_shadowbanned(user)
        
        active_shadowban = None
        if is_shadowbanned:
            active_shadowban = Shadowban.objects.filter(
                user=user,
                is_active=True,
                expires_at__gt=timezone.now()
            ).first()
        
        return Response({
            'is_shadowbanned': is_shadowbanned,
            'shadowban': ShadowbanSerializer(active_shadowban).data if active_shadowban else None
        })


class ModerationStatsAPIView(APIView):
    """API view for moderation statistics (admin only)"""
    
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    
    def get(self, request):
        """Get platform-wide moderation statistics"""
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now() - timedelta(days=30)
        
        total_users = User.objects.count()
        users_with_violations = User.objects.filter(
            violations__created_at__gte=cutoff_date
        ).distinct().count()
        
        active_shadowbans = Shadowban.objects.filter(
            is_active=True,
            expires_at__gt=timezone.now()
        ).count()
        
        recent_violations = ViolationHistory.objects.filter(
            created_at__gte=cutoff_date
        ).count()
        
        heat_distribution = {str(i): 0 for i in range(6)}
        for user in User.objects.filter(violations__is_active=True).distinct():
            heat_level = HeatSystem.get_user_heat_level(user)
            heat_distribution[str(heat_level)] += 1
        
        action_stats = {}
        for result in ModerationResult.objects.filter(processed_at__gte=cutoff_date):
            action = result.action_taken
            action_stats[action] = action_stats.get(action, 0) + 1
        
        return Response({
            'period': '30_days',
            'total_users': total_users,
            'users_with_violations': users_with_violations,
            'violation_rate': (users_with_violations / total_users * 100) if total_users > 0 else 0,
            'active_shadowbans': active_shadowbans,
            'recent_violations': recent_violations,
            'heat_distribution': heat_distribution,
            'action_distribution': action_stats
        })