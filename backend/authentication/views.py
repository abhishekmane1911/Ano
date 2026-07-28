import logging
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

from .serializers import (
    RegisterSerializer,
    EmailVerificationSerializer,
    LoginSerializer,
    UserSerializer,
    TokenSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer
)
from .tasks import send_verification_email, send_password_reset_email
from ano_backend.logging_config import get_anonymous_id_from_user
# from security.authentication import EnhancedAuthenticationService

User = get_user_model()

logger = logging.getLogger('ano_platform')
security_logger = logging.getLogger('ano_platform.security')


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Register a new user with IIT Indore email.
    Sends verification email asynchronously upon successful registration.
    """
    serializer = RegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        logger.info(f"New user registered: user_{user.id}")
        
        # Send verification email asynchronously using Celery
        send_verification_email.delay(
            user_id=str(user.id),
            user_email=user.email,
            verification_token=str(user.verification_token)
        )
        logger.info(f"Verification email task queued for user_{user.id}")
        
        return Response({
            'message': 'Registration successful. Please check your email to verify your account.',
            'email': user.email
        }, status=status.HTTP_201_CREATED)
    
    logger.warning(f"Registration failed: {serializer.errors}")
    return Response({
        'error': {
            'code': 'VALIDATION_ERROR',
            'message': 'Invalid registration data',
            'details': serializer.errors
        }
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_email_view(request):
    """
    Verify user email with verification token.
    Activates the user account upon successful verification.
    """
    serializer = EmailVerificationSerializer(data=request.data)
    
    if serializer.is_valid():
        token = serializer.validated_data['token']
        
        try:
            user = User.objects.get(verification_token=token)
            
            if user.is_verified:
                logger.info(f"Email verification attempted for already verified user_{user.id}")
                return Response({
                    'message': 'Email already verified'
                }, status=status.HTTP_200_OK)
            
            user.is_verified = True
            user.is_active = True
            user.save()
            
            logger.info(f"Email verified successfully for user_{user.id}")
            
            return Response({
                'message': 'Email verified successfully. You can now log in.'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            security_logger.warning(f"Invalid verification token attempted: {token}")
            return Response({
                'error': {
                    'code': 'INVALID_TOKEN',
                    'message': 'Invalid verification token'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'error': {
            'code': 'VALIDATION_ERROR',
            'message': 'Invalid request data',
            'details': serializer.errors
        }
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Authenticate user and return JWT tokens.
    Simplified version without complex middleware interference.
    """
    try:
        # Get credentials from request
        email = request.data.get('email', '').lower().strip()
        password = request.data.get('password', '')
        
        if not email or not password:
            return Response({
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Email and password are required'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find user by email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({
                'error': {
                    'code': 'INVALID_CREDENTIALS',
                    'message': 'Invalid email or password'
                }
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check password
        if not user.check_password(password):
            return Response({
                'error': {
                    'code': 'INVALID_CREDENTIALS',
                    'message': 'Invalid email or password'
                }
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if user is active
        if not user.is_active:
            return Response({
                'error': {
                    'code': 'ACCOUNT_NOT_VERIFIED',
                    'message': 'Please verify your email before logging in'
                }
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        # Prepare user data
        user_data = {
            'id': str(user.id),
            'email': user.email,
            'username': user.username,
            'is_verified': user.is_verified,
            'date_joined': user.date_joined.isoformat(),
            'isAdmin': user.is_staff or user.is_superuser
        }
        
        response_data = {
            'access': str(refresh.access_token),
            'user': user_data
        }
        
        # Create response with refresh token in HTTP-only cookie
        response = Response(response_data, status=status.HTTP_200_OK)
        response.set_cookie(
            key='refresh_token',
            value=str(refresh),
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Lax',
            max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
        )
        
        logger.info(f"Successful login for user_{user.id}")
        return response
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        logger.error(f"Login error: {str(e)}\n{error_trace}")
        
        return Response({
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': 'An error occurred during login',
                'details': str(e) if settings.DEBUG else 'Internal server error'
            }
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout user by blacklisting refresh token.
    Clears refresh token cookie.
    """
    try:
        # Get refresh token from cookie or request body
        refresh_token = request.COOKIES.get('refresh_token') or request.data.get('refresh')
        
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        # Log logout with anonymous ID
        anonymous_id = get_anonymous_id_from_user(request.user)
        logger.info(f"User logged out: {anonymous_id or f'user_{request.user.id}'}")
        
        response = Response({
            'message': 'Logged out successfully'
        }, status=status.HTTP_200_OK)
        
        # Clear refresh token cookie
        response.delete_cookie('refresh_token')
        
        return response
        
    except (TokenError, InvalidToken) as e:
        security_logger.warning(f"Logout failed with invalid token for user_{request.user.id}")
        return Response({
            'error': {
                'code': 'INVALID_TOKEN',
                'message': 'Invalid or expired token'
            }
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token_view(request):
    """
    Refresh access token using refresh token.
    Returns new access token and rotated refresh token.
    """
    # Get refresh token from cookie or request body
    refresh_token = request.COOKIES.get('refresh_token') or request.data.get('refresh')
    
    if not refresh_token:
        return Response({
            'error': {
                'code': 'NO_REFRESH_TOKEN',
                'message': 'Refresh token not provided'
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        refresh = RefreshToken(refresh_token)
        
        # Get new access token
        access_token = str(refresh.access_token)
        
        # Rotate refresh token (if configured)
        new_refresh_token = str(refresh)
        
        response_data = {
            'access': access_token,
        }
        
        response = Response(response_data, status=status.HTTP_200_OK)
        
        # Update refresh token cookie
        response.set_cookie(
            key='refresh_token',
            value=new_refresh_token,
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Lax',
            max_age=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'].total_seconds()
        )
        
        return response
        
    except (TokenError, InvalidToken) as e:
        return Response({
            'error': {
                'code': 'INVALID_TOKEN',
                'message': 'Invalid or expired refresh token'
            }
        }, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """
    Get current authenticated user details.
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_request_view(request):
    """
    Request password reset by email.
    Sends password reset link to user's email.
    """
    serializer = PasswordResetRequestSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email, is_active=True)
            
            # Generate password reset token
            reset_token = user.generate_password_reset_token()
            
            # Send password reset email asynchronously
            send_password_reset_email.delay(
                user_id=str(user.id),
                user_email=user.email,
                reset_token=str(reset_token)
            )
            
            logger.info(f"Password reset email task queued for user_{user.id}")
            
            # In development, also log the reset URL for easy testing
            if settings.DEBUG:
                reset_url = f"{settings.FRONTEND_URL}/password-reset-confirm?token={reset_token}"
                logger.info(f"Development: Password reset URL for {email}: {reset_url}")
                print(f"\n{'='*60}")
                print(f"PASSWORD RESET LINK FOR DEVELOPMENT")
                print(f"Email: {email}")
                print(f"Reset URL: {reset_url}")
                print(f"{'='*60}\n")
            
        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            logger.warning(f"Password reset requested for non-existent email: {email.split('@')[1]}")
        
        # Always return success to prevent email enumeration
        return Response({
            'message': 'If an account exists with this email, you will receive password reset instructions.'
        }, status=status.HTTP_200_OK)
    
    return Response({
        'error': {
            'code': 'VALIDATION_ERROR',
            'message': 'Invalid request data',
            'details': serializer.errors
        }
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def password_reset_confirm_view(request):
    """
    Confirm password reset with token and new password.
    """
    serializer = PasswordResetConfirmSerializer(data=request.data)
    
    if serializer.is_valid():
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['password']
        
        try:
            user = User.objects.get(password_reset_token=token)
            
            # Check if token is still valid
            if not user.is_password_reset_token_valid():
                security_logger.warning(f"Expired password reset token used for user_{user.id}")
                return Response({
                    'error': {
                        'code': 'TOKEN_EXPIRED',
                        'message': 'Password reset token has expired. Please request a new one.'
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Set new password
            user.set_password(new_password)
            user.clear_password_reset_token()
            
            logger.info(f"Password reset successfully for user_{user.id}")
            
            return Response({
                'message': 'Password reset successful. You can now log in with your new password.'
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            security_logger.warning(f"Invalid password reset token attempted: {token}")
            return Response({
                'error': {
                    'code': 'INVALID_TOKEN',
                    'message': 'Invalid password reset token'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({
        'error': {
            'code': 'VALIDATION_ERROR',
            'message': 'Invalid request data',
            'details': serializer.errors
        }
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def test_email_view(request):
    """
    Test email functionality - Development only
    """
    if not settings.DEBUG:
        return Response({'error': 'Not available in production'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        from django.core.mail import send_mail
        
        send_mail(
            subject='Test Email from Ano',
            message='This is a test email to verify email functionality.',
            from_email=settings.EMAIL_HOST_USER or 'noreply@ano.com',
            recipient_list=['test@iiti.ac.in'],
            fail_silently=False,
        )
        
        return Response({
            'message': 'Test email sent successfully. Check console or email files.'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Failed to send test email: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_reset_url_view(request):
    """
    Get password reset URL for development/testing - Development only
    """
    if not settings.DEBUG:
        return Response({'error': 'Not available in production'}, status=status.HTTP_404_NOT_FOUND)
    
    email = request.GET.get('email')
    if not email:
        return Response({'error': 'Email parameter required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = User.objects.get(email=email, is_active=True)
        
        # Generate a new reset token if none exists or if the current one is expired
        if not user.password_reset_token or not user.is_password_reset_token_valid():
            reset_token = user.generate_password_reset_token()
        else:
            reset_token = user.password_reset_token
            
        reset_url = f"{settings.FRONTEND_URL}/password-reset-confirm?token={reset_token}"
        
        return Response({
            'email': email,
            'reset_url': reset_url,
            'token': str(reset_token),
            'expires_at': user.password_reset_token_created,
            'message': 'Copy this URL and paste it in your browser to reset password'
        }, status=status.HTTP_200_OK)
            
    except User.DoesNotExist:
        return Response({
            'error': 'User not found'
        }, status=status.HTTP_404_NOT_FOUND)
