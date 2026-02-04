from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatroomViewSet, MessageViewSet, search_messages

router = DefaultRouter()
router.register(r'chatrooms', ChatroomViewSet, basename='chatroom')
router.register(r'messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
    path('search/', search_messages, name='search-messages'),
]
