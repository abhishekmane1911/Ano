from django.contrib import admin
from .models import Report, Block


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'reporter_anonymous_id',
        'reported_anonymous_id',
        'reason',
        'status',
        'created_at',
        'reviewed_at',
    ]
    list_filter = ['status', 'reason', 'created_at']
    search_fields = [
        'reporter__anonymous_id',
        'reported__anonymous_id',
        'description',
    ]
    readonly_fields = ['id', 'created_at']
    
    def reporter_anonymous_id(self, obj):
        return obj.reporter.anonymous_id
    reporter_anonymous_id.short_description = 'Reporter ID'
    
    def reported_anonymous_id(self, obj):
        return obj.reported.anonymous_id
    reported_anonymous_id.short_description = 'Reported ID'


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'blocker_anonymous_id',
        'blocked_anonymous_id',
        'created_at',
    ]
    list_filter = ['created_at']
    search_fields = [
        'blocker__anonymous_id',
        'blocked__anonymous_id',
    ]
    readonly_fields = ['id', 'created_at']
    
    def blocker_anonymous_id(self, obj):
        return obj.blocker.anonymous_id
    blocker_anonymous_id.short_description = 'Blocker ID'
    
    def blocked_anonymous_id(self, obj):
        return obj.blocked.anonymous_id
    blocked_anonymous_id.short_description = 'Blocked ID'
