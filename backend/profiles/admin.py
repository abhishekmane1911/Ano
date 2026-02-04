from django.contrib import admin
from .models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Admin interface for Profile model"""
    list_display = ['anonymous_id', 'age', 'relationship_intent', 'created_at']
    list_filter = ['relationship_intent', 'created_at']
    search_fields = ['anonymous_id']
    readonly_fields = ['id', 'anonymous_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Identifiers', {
            'fields': ('id', 'anonymous_id', 'user')
        }),
        ('Profile Information', {
            'fields': ('age', 'interests', 'hobbies', 'relationship_intent', 'personality_tags', 'bio', 'avatar')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
