from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin interface for Profile model"""
    list_display = ['anonymous_id', 'created_at']
    list_filter = ['created_at']
    search_fields = ['anonymous_id']
    readonly_fields = ['id', 'anonymous_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Identifiers', {
            'fields': ('id', 'anonymous_id', 'user')
        }),
        ('Profile Information', {
            'fields': ('bio', 'avatar')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
