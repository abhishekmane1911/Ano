from django.contrib import admin
from .models import UserReputation, MessageRanking, Vote


@admin.register(UserReputation)
class UserReputationAdmin(admin.ModelAdmin):
    list_display = ['user', 'reputation_score', 'rank_tier', 'total_upvotes_received', 'total_downvotes_received', 'updated_at']
    list_filter = ['rank_tier', 'created_at']
    search_fields = ['user__email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-reputation_score']


@admin.register(MessageRanking)
class MessageRankingAdmin(admin.ModelAdmin):
    list_display = ['message', 'upvotes', 'downvotes', 'wilson_score', 'last_calculated']
    list_filter = ['last_calculated']
    search_fields = ['message__content']
    readonly_fields = ['last_calculated']
    ordering = ['-wilson_score']


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'vote_type', 'created_at']
    list_filter = ['vote_type', 'created_at']
    search_fields = ['user__email', 'message__content']
    readonly_fields = ['created_at']
