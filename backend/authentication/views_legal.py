"""
Legal compliance views for GDPR/CCPA data rights
"""
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import json
import os

from .models_legal import (
    LegalDocument, UserLegalConsent, DataDeletionRequest,
    DataExportRequest, UserAgeVerification, ContentAppeal
)

User = get_user_model()


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def accept_legal_document(request):
    """
    User accepts a legal document (ToS, Privacy Policy, etc.)
    """
    document_type = request.data.get('document_type')
    version = request.data.get('version')
    
    if not document_type or not version:
        return Response(
            {'error': 'document_type and version are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        document = LegalDocument.objects.get(
            document_type=document_type,
            version=version,
            is_active=True
        )
    except LegalDocument.DoesNotExist:
        return Response(
            {'error': 'Document not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get IP and user agent
    ip_address = request.META.get('REMOTE_ADDR')
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # Create or update consent
    consent, created = UserLegalConsent.objects.update_or_create(
        user=request.user,
        document=document,
        defaults={
            'ip_address': ip_address,
            'user_agent': user_agent
        }
    )
    
    return Response({
        'message': 'Legal document accepted',
        'document_type': document.get_document_type_display(),
        'version': document.version,
        'accepted_at': consent.accepted_at
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_legal_documents(request):
    """
    Get current active legal documents
    """
    documents = LegalDocument.objects.filter(is_active=True)
    
    result = []
    for doc in documents:
        # Check if user has accepted this version
        has_accepted = UserLegalConsent.objects.filter(
            user=request.user,
            document=doc
        ).exists()
        
        result.append({
            'type': doc.document_type,
            'type_display': doc.get_document_type_display(),
            'version': doc.version,
            'effective_date': doc.effective_date,
            'has_accepted': has_accepted,
            'content': doc.content
        })
    
    return Response(result)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def request_data_export(request):
    """
    GDPR: User requests export of their data
    """
    # Check if there's a pending request
    pending = DataExportRequest.objects.filter(
        user=request.user,
        status__in=['pending', 'processing']
    ).exists()
    
    if pending:
        return Response(
            {'error': 'You already have a pending export request'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create export request
    export_request = DataExportRequest.objects.create(
        user=request.user,
        status='pending'
    )
    
    # TODO: Trigger async task to generate export
    # from .tasks import generate_data_export
    # generate_data_export.delay(export_request.id)
    
    return Response({
        'message': 'Data export request submitted',
        'request_id': export_request.id,
        'status': export_request.status,
        'note': 'You will receive an email when your data is ready to download (within 48 hours)'
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_data_export_status(request):
    """
    Check status of data export requests
    """
    exports = DataExportRequest.objects.filter(user=request.user).order_by('-requested_at')[:5]
    
    result = []
    for export in exports:
        result.append({
            'id': export.id,
            'requested_at': export.requested_at,
            'status': export.status,
            'is_expired': export.is_expired(),
            'download_count': export.download_count,
            'expires_at': export.expires_at
        })
    
    return Response(result)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def request_data_deletion(request):
    """
    GDPR/CCPA: User requests deletion of their data
    """
    reason = request.data.get('reason', '')
    
    # Check if there's a pending request
    pending = DataDeletionRequest.objects.filter(
        user=request.user,
        status__in=['pending', 'processing']
    ).exists()
    
    if pending:
        return Response(
            {'error': 'You already have a pending deletion request'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create deletion request
    deletion_request = DataDeletionRequest.objects.create(
        user=request.user,
        reason=reason,
        status='pending'
    )
    
    return Response({
        'message': 'Data deletion request submitted',
        'request_id': deletion_request.id,
        'status': deletion_request.status,
        'note': 'Your account and data will be deleted within 30 days. You can cancel this request within 7 days.',
        'warning': 'This action cannot be undone after the grace period'
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_data_deletion(request):
    """
    Cancel a pending data deletion request (within grace period)
    """
    request_id = request.data.get('request_id')
    
    try:
        deletion_request = DataDeletionRequest.objects.get(
            id=request_id,
            user=request.user,
            status='pending'
        )
    except DataDeletionRequest.DoesNotExist:
        return Response(
            {'error': 'Deletion request not found or already processed'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Check if within grace period (7 days)
    grace_period = deletion_request.requested_at + timedelta(days=7)
    if timezone.now() > grace_period:
        return Response(
            {'error': 'Grace period has expired. Cannot cancel deletion.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    deletion_request.delete()
    
    return Response({
        'message': 'Data deletion request cancelled successfully'
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def verify_age(request):
    """
    User verifies their age
    """
    birth_year = request.data.get('birth_year')
    
    if not birth_year:
        return Response(
            {'error': 'birth_year is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        birth_year = int(birth_year)
    except ValueError:
        return Response(
            {'error': 'birth_year must be a valid year'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Calculate age
    from datetime import datetime
    current_year = datetime.now().year
    age = current_year - birth_year
    
    # Check minimum age (13)
    if age < 13:
        return Response(
            {'error': 'You must be at least 13 years old to use this service'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create or update age verification
    verification, created = UserAgeVerification.objects.update_or_create(
        user=request.user,
        defaults={
            'birth_year': birth_year,
            'verification_method': 'self_reported',
            'is_verified': True
        }
    )
    
    return Response({
        'message': 'Age verified successfully',
        'age': age,
        'verified_at': verification.verified_at
    })


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def submit_content_appeal(request):
    """
    User appeals a moderation decision
    """
    content_type = request.data.get('content_type')
    content_id = request.data.get('content_id')
    original_action = request.data.get('original_action')
    appeal_reason = request.data.get('appeal_reason')
    
    if not all([content_type, content_id, original_action, appeal_reason]):
        return Response(
            {'error': 'All fields are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if already appealed
    existing = ContentAppeal.objects.filter(
        user=request.user,
        content_type=content_type,
        content_id=content_id,
        status__in=['pending', 'under_review']
    ).exists()
    
    if existing:
        return Response(
            {'error': 'You already have a pending appeal for this content'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create appeal
    appeal = ContentAppeal.objects.create(
        user=request.user,
        content_type=content_type,
        content_id=content_id,
        original_action=original_action,
        appeal_reason=appeal_reason,
        status='pending'
    )
    
    return Response({
        'message': 'Appeal submitted successfully',
        'appeal_id': appeal.id,
        'status': appeal.status,
        'note': 'Your appeal will be reviewed within 48 hours'
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_my_appeals(request):
    """
    Get user's content appeals
    """
    appeals = ContentAppeal.objects.filter(user=request.user).order_by('-submitted_at')
    
    result = []
    for appeal in appeals:
        result.append({
            'id': appeal.id,
            'content_type': appeal.content_type,
            'original_action': appeal.original_action,
            'status': appeal.status,
            'status_display': appeal.get_status_display(),
            'submitted_at': appeal.submitted_at,
            'reviewed_at': appeal.reviewed_at,
            'decision': appeal.decision
        })
    
    return Response(result)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_my_data_summary(request):
    """
    GDPR: Get summary of user's data
    """
    user = request.user
    
    # Count various data points
    from chat.models import Message
    from profiles.models import Profile
    from moderation.models import ViolationHistory
    
    try:
        profile = user.profile
        profile_data = {
            'anonymous_id': str(profile.anonymous_id),
            'bio': profile.bio,
            'interests': profile.interests,
            'created_at': profile.created_at
        }
    except:
        profile_data = None
    
    message_count = Message.objects.filter(sender__user=user).count()
    violation_count = ViolationHistory.objects.filter(user=user).count()
    
    summary = {
        'account': {
            'email': user.email,
            'created_at': user.created_at,
            'is_verified': user.is_verified
        },
        'profile': profile_data,
        'activity': {
            'messages_sent': message_count,
            'violations': violation_count
        },
        'legal': {
            'consents': UserLegalConsent.objects.filter(user=user).count(),
            'export_requests': DataExportRequest.objects.filter(user=user).count(),
            'deletion_requests': DataDeletionRequest.objects.filter(user=user).count()
        }
    }
    
    return Response(summary)
