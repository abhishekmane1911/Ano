"""
Legal compliance models for Terms of Service, Privacy Policy acceptance
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class LegalDocument(models.Model):
    """
    Stores versions of legal documents (ToS, Privacy Policy, etc.)
    """
    DOCUMENT_TYPES = [
        ('tos', 'Terms of Service'),
        ('privacy', 'Privacy Policy'),
        ('guidelines', 'Community Guidelines'),
        ('cookie', 'Cookie Policy'),
    ]
    
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    version = models.CharField(max_length=20)
    content = models.TextField()
    effective_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'legal_documents'
        ordering = ['-effective_date']
        unique_together = ['document_type', 'version']
    
    def __str__(self):
        return f"{self.get_document_type_display()} v{self.version}"


class UserLegalConsent(models.Model):
    """
    Tracks user acceptance of legal documents
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='legal_consents')
    document = models.ForeignKey(LegalDocument, on_delete=models.CASCADE)
    accepted_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        db_table = 'user_legal_consents'
        ordering = ['-accepted_at']
        unique_together = ['user', 'document']
    
    def __str__(self):
        return f"{self.user.email} - {self.document}"


class DataDeletionRequest(models.Model):
    """
    GDPR/CCPA: Track user data deletion requests
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deletion_requests')
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'data_deletion_requests'
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"Deletion request for {self.user.email} - {self.status}"


class DataExportRequest(models.Model):
    """
    GDPR: Track user data export requests
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('expired', 'Expired'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='export_requests')
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)  # Download link expires after 7 days
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    file_path = models.CharField(max_length=500, blank=True)
    download_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'data_export_requests'
        ordering = ['-requested_at']
    
    def __str__(self):
        return f"Export request for {self.user.email} - {self.status}"
    
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class UserAgeVerification(models.Model):
    """
    Track age verification for compliance
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='age_verification')
    birth_year = models.IntegerField()  # Only year for privacy
    verified_at = models.DateTimeField(auto_now_add=True)
    verification_method = models.CharField(max_length=50, default='self_reported')
    is_verified = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'user_age_verifications'
    
    def __str__(self):
        return f"Age verification for {self.user.email}"
    
    @property
    def age(self):
        from datetime import datetime
        current_year = datetime.now().year
        return current_year - self.birth_year


class ContentAppeal(models.Model):
    """
    Track appeals for moderation decisions
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('under_review', 'Under Review'),
        ('upheld', 'Appeal Upheld - Content Restored'),
        ('denied', 'Appeal Denied'),
        ('modified', 'Partially Upheld'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='content_appeals')
    content_type = models.CharField(max_length=50)  # 'message', 'profile', etc.
    content_id = models.CharField(max_length=100)
    original_action = models.CharField(max_length=50)  # 'removed', 'shadowban', etc.
    appeal_reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_appeals')
    
    decision = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'content_appeals'
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"Appeal by {self.user.email} - {self.status}"
