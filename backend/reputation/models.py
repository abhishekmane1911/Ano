import math
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class UserReputation(models.Model):
    """Extended user reputation and ranking system"""
    
    RANK_TIERS = [
        ('Fresher', 'Fresher'),
        ('Sophomore', 'Sophomore'),
        ('Senior', 'Senior'),
        ('Campus Legend', 'Campus Legend'),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='reputation'
    )
    reputation_score = models.FloatField(default=0.0)
    rank_tier = models.CharField(
        max_length=20,
        choices=RANK_TIERS,
        default='Fresher'
    )
    total_upvotes_received = models.IntegerField(default=0)
    total_downvotes_received = models.IntegerField(default=0)
    last_tier_update = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_reputation'
        indexes = [
            models.Index(fields=['reputation_score']),
            models.Index(fields=['rank_tier']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.rank_tier} ({self.reputation_score})"
    
    def calculate_level(self) -> int:
        """Calculate user level using logarithmic progression: Level N requires 100 * (1.5 ^ N) XP"""
        if self.reputation_score < 100:
            return 0
        
        # Find the highest level where the user has enough XP
        level = 1
        while True:
            xp_required = 100 * (1.5 ** level)
            if self.reputation_score >= xp_required:
                level += 1
            else:
                break
        
        return level
    
    def xp_for_next_level(self) -> float:
        """Calculate XP needed for next level"""
        current_level = self.calculate_level()
        # Level N means user has passed thresholds 1..(N-1) and is below threshold N
        # The next level's entry threshold is 100 * (1.5 ^ current_level)
        next_level_xp = 100 * (1.5 ** current_level)
        return next_level_xp - self.reputation_score
    
    def update_tier(self):
        """Update user tier based on reputation score"""
        # Tier thresholds based on reputation score to match existing tests
        if self.reputation_score >= 1000:
            new_tier = 'Campus Legend'
        elif self.reputation_score >= 500:
            new_tier = 'Senior'
        elif self.reputation_score >= 100:
            new_tier = 'Sophomore'
        else:
            new_tier = 'Fresher'
        
        if self.rank_tier != new_tier:
            self.rank_tier = new_tier
            self.save()
        
        return new_tier


class ContentRanking(models.Model):
    """Abstract base class for ranking content using Wilson Score"""
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    wilson_score = models.FloatField(default=0.0)
    last_calculated = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
    
    def calculate_wilson_score(self, confidence=0.95) -> float:
        """Calculate Wilson Score Interval lower bound"""
        n = self.upvotes + self.downvotes
        if n == 0:
            return 0.0
        
        p = self.upvotes / n
        z = 1.96  # 95% confidence interval
        
        numerator = p + (z * z) / (2 * n) - z * math.sqrt((p * (1 - p) + (z * z) / (4 * n)) / n)
        denominator = 1 + (z * z) / n
        
        return numerator / denominator
    
    def update_wilson_score(self):
        """Update the Wilson Score and save"""
        self.wilson_score = self.calculate_wilson_score()
        self.save()


class MessageRanking(ContentRanking):
    """Wilson Score ranking for messages"""
    message = models.OneToOneField(
        'chat.Message', 
        on_delete=models.CASCADE, 
        related_name='ranking'
    )
    
    class Meta:
        db_table = 'message_ranking'
        indexes = [
            models.Index(fields=['wilson_score']),
            models.Index(fields=['message']),
        ]


class Vote(models.Model):
    """Track user votes on messages"""
    
    VOTE_TYPES = [
        ('upvote', 'Upvote'),
        ('downvote', 'Downvote'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    message = models.ForeignKey('chat.Message', on_delete=models.CASCADE, related_name='votes')
    vote_type = models.CharField(max_length=10, choices=VOTE_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'votes'
        unique_together = ['user', 'message']
        indexes = [
            models.Index(fields=['message']),
            models.Index(fields=['user']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.vote_type} on message {self.message.id}"
