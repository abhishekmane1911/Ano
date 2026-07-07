from django.contrib import admin
from .models import ModerationResult, ViolationHistory, Shadowban


@admin.register(ModerationResult)
class ModerationResultAdmin(admin.ModelAdmin):
    list_display = ['message', 'user', 'toxicity_score', 'action_taken', 'processed_at']
    list_filter = ['action_taken', 'processed_at']
    search_fields = ['user__email', 'message__content']
    readonly_fields = ['processed_at']
    ordering = ['-processed_at']


@admin.register(ViolationHistory)
class ViolationHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'violation_type', 'toxicity_score', 'action_taken', 'is_active', 'created_at']
    list_filter = ['violation_type', 'is_active', 'created_at']
    search_fields = ['user__email', 'content_snippet']
    readonly_fields = ['created_at']
    ordering = ['-created_at']


@admin.register(Shadowban)
class ShadowbanAdmin(admin.ModelAdmin):
    list_display = ['user', 'duration_hours', 'is_active', 'created_at', 'expires_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__email', 'reason']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
