from django.urls import path
from .views import MatchmakingViewSet

urlpatterns = [
    # Profiles for swiping
    path('profiles/', MatchmakingViewSet.as_view({'get': 'get_profiles_for_swiping'}), name='matchmaking-profiles'),
    
    # Swipe endpoint
    path('swipe/', MatchmakingViewSet.as_view({'post': 'record_swipe'}), name='matchmaking-swipe'),
    
    # Matches list
    path('matches/', MatchmakingViewSet.as_view({'get': 'list_matches'}), name='matchmaking-matches'),
    
    # Match detail
    path('matches/<uuid:pk>/', MatchmakingViewSet.as_view({'get': 'match_detail'}), name='matchmaking-match-detail'),
    
    # Match messages
    path('matches/<uuid:pk>/messages/', MatchmakingViewSet.as_view({'get': 'match_messages'}), name='matchmaking-match-messages'),
    
    # Send match message
    path('matches/<uuid:pk>/messages/send/', MatchmakingViewSet.as_view({'post': 'send_match_message'}), name='matchmaking-send-message'),
    
    # Upload match media
    path('matches/<uuid:pk>/messages/upload/', MatchmakingViewSet.as_view({'post': 'upload_match_media'}), name='matchmaking-upload-media'),
]
