from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'leaderboard', views.LeaderboardViewSet, basename='leaderboard')

app_name = 'reputation'

urlpatterns = [
    # API endpoints
    path('api/', include([
        # Voting endpoints
        path('vote/', views.VoteAPIView.as_view(), name='vote'),
        path('vote/<int:message_id>/', views.VoteDetailAPIView.as_view(), name='vote-detail'),
        
        # User reputation endpoints
        path('user/<int:user_id>/', views.UserReputationAPIView.as_view(), name='user-reputation'),
        path('user/me/', views.MyReputationAPIView.as_view(), name='my-reputation'),
        
        # Leaderboard and ranking endpoints
        path('', include(router.urls)),
        path('rankings/', views.ContentRankingsAPIView.as_view(), name='content-rankings'),
        
        # Privilege checking endpoints
        path('privileges/', views.UserPrivilegesAPIView.as_view(), name='user-privileges'),
        path('privileges/check/', views.CheckPrivilegeAPIView.as_view(), name='check-privilege'),
    ])),
]