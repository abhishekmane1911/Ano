from django.contrib import admin
from .models import Swipe, Match


@admin.register(Swipe)
class SwipeAdmin(admin.ModelAdmin):
    list_display = ['id', 'swiper', 'swiped', 'direction', 'created_at']
    list_filter = ['direction', 'created_at']
    search_fields = ['swiper__anonymous_id', 'swiped__anonymous_id']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['id', 'profile1', 'profile2', 'matched_at', 'is_active']
    list_filter = ['is_active', 'matched_at']
    search_fields = ['profile1__anonymous_id', 'profile2__anonymous_id']
    readonly_fields = ['id', 'matched_at']
    ordering = ['-matched_at']
