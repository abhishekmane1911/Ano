"""
URL configuration for admin dashboard API
"""
from django.urls import path
from . import views

urlpatterns = [
    # Reports management
    path('reports/', views.list_reports, name='admin-list-reports'),
    path('reports/<uuid:report_id>/', views.update_report, name='admin-update-report'),
    
    # User moderation
    path('users/<uuid:anonymous_id>/', views.get_user_detail, name='admin-user-detail'),
    path('users/<uuid:anonymous_id>/ban/', views.ban_user, name='admin-ban-user'),
    
    # Broadcast messages
    path('broadcast/', views.broadcast_message, name='admin-broadcast'),
    
    # Platform metrics
    path('metrics/', views.get_platform_metrics, name='admin-metrics'),
]
