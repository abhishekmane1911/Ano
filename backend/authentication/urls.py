from django.urls import path
from . import views

app_name = 'authentication'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('verify-email/', views.verify_email_view, name='verify-email'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('refresh/', views.refresh_token_view, name='refresh'),
    path('me/', views.me_view, name='me'),
    path('password-reset/', views.password_reset_request_view, name='password-reset'),
    path('password-reset-confirm/', views.password_reset_confirm_view, name='password-reset-confirm'),
    path('test-email/', views.test_email_view, name='test-email'),  # Development only
    path('get-reset-url/', views.get_reset_url_view, name='get-reset-url'),  # Development only
]
