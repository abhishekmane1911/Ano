"""
URL configuration for moderation app with heat system endpoints.
"""

from django.urls import path
from . import views

app_name = 'moderation'

urlpatterns = [
    # API endpoints
    path('api/', views.ModerationStatusAPIView.as_view(), name='moderation-status'),
    path('api/heat/', views.HeatSystemAPIView.as_view(), name='heat-system'),
    path('api/report/', views.ReportContentAPIView.as_view(), name='report-content'),
    path('api/violations/', views.UserViolationsAPIView.as_view(), name='user-violations'),
    path('api/shadowban/status/', views.ShadowbanStatusAPIView.as_view(), name='shadowban-status'),
    path('api/stats/', views.ModerationStatsAPIView.as_view(), name='moderation-stats'),
]