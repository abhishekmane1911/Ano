from django.urls import path
from . import views

app_name = 'security'

urlpatterns = [
    path('api/rate-limits/', views.RateLimitStatusAPIView.as_view(), name='rate-limit-status'),
    path('api/security-events/', views.SecurityEventsAPIView.as_view(), name='security-events'),
    path('api/identity/hash/', views.IdentityHashAPIView.as_view(), name='identity-hash'),
]