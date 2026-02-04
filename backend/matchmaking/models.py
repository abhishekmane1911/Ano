import uuid
from django.db import models
from profiles.models import Profile


class Swipe(models.Model):
    """Record of a user swiping on another profile"""
    
    DIRECTION_CHOICES = [
        ('left', 'Left'),
        ('right', 'Right'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    swiper = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='swipes_made',
        help_text='Profile that performed the swipe'
    )
    swiped = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='swipes_received',
        help_text='Profile that was swiped on'
    )
    direction = models.CharField(
        max_length=5,
        choices=DIRECTION_CHOICES,
        help_text='Direction of swipe: left (reject) or right (accept)'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'swipes'
        unique_together = ['swiper', 'swiped']
        indexes = [
            models.Index(fields=['swiper', 'created_at']),
            models.Index(fields=['swiped', 'created_at']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.swiper.anonymous_id} swiped {self.direction} on {self.swiped.anonymous_id}"


class Match(models.Model):
    """Mutual match between two profiles"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile1 = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='matches_as_profile1',
        help_text='First profile in the match'
    )
    profile2 = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='matches_as_profile2',
        help_text='Second profile in the match'
    )
    matched_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(
        default=True,
        help_text='Whether the match is still active'
    )
    
    class Meta:
        db_table = 'matches'
        indexes = [
            models.Index(fields=['profile1', 'is_active']),
            models.Index(fields=['profile2', 'is_active']),
            models.Index(fields=['matched_at']),
        ]
        ordering = ['-matched_at']
    
    def __str__(self):
        return f"Match between {self.profile1.anonymous_id} and {self.profile2.anonymous_id}"
    
    def get_other_profile(self, profile):
        """Get the other profile in this match"""
        if self.profile1 == profile:
            return self.profile2
        elif self.profile2 == profile:
            return self.profile1
        return None
    
    def has_profile(self, profile):
        """Check if a profile is part of this match"""
        return self.profile1 == profile or self.profile2 == profile
