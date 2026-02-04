"""
WebSocket URL routing for matchmaking application
"""
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/match/(?P<match_id>[0-9a-f-]+)/$', consumers.MatchConsumer.as_asgi()),
]