from django.urls import path
from .views import (
    ProfileMeView,
    ProfileDetailView,
    upload_avatar,
    optimize_avatar,
)

urlpatterns = [
    path('me/', ProfileMeView.as_view(), name='profile-me'),
    path('avatar/', upload_avatar, name='profile-avatar'),
    path('avatar/optimize/', optimize_avatar, name='profile-avatar-optimize'),
    path('<uuid:anonymous_id>/', ProfileDetailView.as_view(), name='profile-detail'),
]
