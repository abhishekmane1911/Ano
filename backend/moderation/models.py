from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class ModerationResult(models.Model):
    """Store results of AI moderation checks"""
    
    ACTIONS = [
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('shadowban', 'Shadowban Applied'),
        ('warning', 'Warning Issued'),
    ]
    
    message = models.ForeignKey('chat.Message', on_delete=models.CASCADE, related_name='moderation_results')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='moderation_results')
    toxicity_score = models.FloatField()
    flagged_categories = models.JSONField(default=list)
    action_taken = models.CharField(max_length=20, choices=ACTIONS)
    processed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'moderation_results'
        indexes = [
            models.Index(fields=['message']),
            models.Index(fields=['user']),
            models.Index(fields=['toxicity_score']),
            models.Index(fields=['processed_at']),
        ]
    
    def __str__(self):
        return f"Moderation: message {self.message.id} - {self.action_taken}"


class ViolationHistory(models.Model):
    """Track user violations and heat system"""
    
    VIOLATION_TYPES = [
        ('toxicity', 'High Toxicity Content'),
        ('harassment', 'Harassment'),
        ('violence', 'Violence'),
        ('self_harm', 'Self Harm'),
        ('spam', 'Spam'),
        ('inappropriate', 'Inappropriate Content'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='violations')
    violation_type = models.CharField(max_length=50, choices=VIOLATION_TYPES)
    toxicity_score = models.FloatField()
    content_snippet = models.TextField(max_length=200)
    action_taken = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'violation_history'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_active']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.violation_type} ({self.toxicity_score})"
    
    def is_expired(self) -> bool:
        """Check if violation has expired"""
        return self.expires_at and timezone.now() > self.expires_at


class Shadowban(models.Model):
    """Track active shadowbans"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shadowbans')
    reason = models.TextField()
    duration_hours = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'shadowbans'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['is_active']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"Shadowban: {self.user.email} until {self.expires_at}"
    
    def is_expired(self) -> bool:
        """Check if shadowban has expired"""
        return timezone.now() > self.expires_at
    
    def save(self, *args, **kwargs):
        """Set expires_at based on duration_hours"""
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=self.duration_hours)
        super().save(*args, **kwargs)
