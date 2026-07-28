from django.urls import path
from .views import (
    ReportCreateView,
    BlockCreateView,
    BlockedUsersListView,
    unblock_user,
)

app_name = 'reports'

urlpatterns = [
    path('', ReportCreateView.as_view(), name='report-create'),
    
    path('block/', BlockCreateView.as_view(), name='block-create'),
    path('blocked/', BlockedUsersListView.as_view(), name='blocked-list'),
    path('block/<uuid:anonymous_id>/', unblock_user, name='unblock-user'),
]
