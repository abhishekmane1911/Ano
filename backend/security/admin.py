from django.contrib import admin
from .models import RateLimitRecord, HashedIdentity, SecurityEvent


@admin.register(RateLimitRecord)
class RateLimitRecordAdmin(admin.ModelAdmin):
    list_display = ['user', 'action_type', 'ip_address', 'timestamp']
    list_filter = ['action_type', 'timestamp']
    search_fields = ['user__email', 'ip_address']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']


@admin.register(HashedIdentity)
class HashedIdentityAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_hash', 'created_at']
    search_fields = ['user__email', 'email_hash']
    readonly_fields = ['created_at', 'email_hash', 'salt']
    ordering = ['-created_at']


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    list_display = ['user', 'event_type', 'severity', 'ip_address', 'timestamp']
    list_filter = ['event_type', 'severity', 'timestamp']
    search_fields = ['user__email', 'ip_address', 'description']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']
