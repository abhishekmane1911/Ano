import uuid
from django.db import models
from django.conf import settings
from profiles.models import Profile


class Report(models.Model):
    """Report model for users reporting inappropriate behavior"""
    
    REASON_CHOICES = [
        ('harassment', 'Harassment'),
        ('spam', 'Spam'),
        ('inappropriate', 'Inappropriate Content'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporter = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='reports_made',
        help_text='Profile that submitted the report'
    )
    reported = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='reports_received',
        help_text='Profile being reported'
    )
    reason = models.CharField(
        max_length=20,
        choices=REASON_CHOICES,
        help_text='Reason for the report'
    )
    description = models.TextField(
        help_text='Detailed description of the issue'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        help_text='Current status of the report'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_reports',
        help_text='Admin user who reviewed the report'
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='Timestamp when report was reviewed'
    )
    
    class Meta:
        db_table = 'reports'
        indexes = [
            models.Index(fields=['reporter']),
            models.Index(fields=['reported']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Report {self.id} - {self.reason} by {self.reporter.anonymous_id}"


class Block(models.Model):
    """Block model for users blocking other users"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    blocker = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='blocks_made',
        help_text='Profile that initiated the block'
    )
    blocked = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='blocks_received',
        help_text='Profile being blocked'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'blocks'
        unique_together = [['blocker', 'blocked']]
        indexes = [
            models.Index(fields=['blocker', 'blocked']),
            models.Index(fields=['blocker']),
            models.Index(fields=['blocked']),
        ]
    
    def __str__(self):
        return f"Block by {self.blocker.anonymous_id} on {self.blocked.anonymous_id}"
