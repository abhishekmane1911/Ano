"""
Celery tasks for authentication app.
Handles async email sending for verification and password reset.
"""
import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

# Import monitoring and circuit breaker functionality
from ano_backend.monitoring import (
    email_circuit_breaker,
    monitor_async_operation,
    CircuitBreakerOpenException
)

logger = logging.getLogger('ano_platform')


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
@monitor_async_operation("email_verification")
def send_verification_email(self, user_id, user_email, verification_token):
    """
    Send email verification link to user with circuit breaker protection.
    
    Args:
        user_id: User ID for logging
        user_email: User's email address
        verification_token: UUID token for verification
    """
    try:
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
        
        # Render HTML email template
        html_message = render_to_string('authentication/verification_email.html', {
            'verification_url': verification_url,
            'frontend_url': settings.FRONTEND_URL,
        })
        
        # Create plain text version
        plain_message = strip_tags(html_message)
        
        # Use circuit breaker for email sending
        try:
            email_circuit_breaker.call(
                send_mail,
                subject='Verify your Ano account',
                message=plain_message,
                from_email=settings.EMAIL_HOST_USER or 'noreply@ano.com',
                recipient_list=[user_email],
                html_message=html_message,
                fail_silently=False,
            )
        except CircuitBreakerOpenException:
            logger.warning(f"Email circuit breaker is open, queuing verification email for user_{user_id}")
            # Re-queue the task for later when circuit breaker might be closed
            raise self.retry(countdown=300)  # Retry in 5 minutes
        
        logger.info(f"Verification email sent successfully to user_{user_id}")
        return f"Verification email sent to {user_email}"
        
    except Exception as exc:
        logger.error(f"Failed to send verification email to user_{user_id}: {str(exc)}")
        # Retry the task
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
@monitor_async_operation("password_reset_email")
def send_password_reset_email(self, user_id, user_email, reset_token):
    """
    Send password reset link to user with circuit breaker protection.
    
    Args:
        user_id: User ID for logging
        user_email: User's email address
        reset_token: UUID token for password reset
    """
    try:
        reset_url = f"{settings.FRONTEND_URL}/password-reset-confirm?token={reset_token}"
        
        # Render HTML email template
        html_message = render_to_string('authentication/password_reset_email.html', {
            'reset_url': reset_url,
            'frontend_url': settings.FRONTEND_URL,
        })
        
        # Create plain text version
        plain_message = strip_tags(html_message)
        
        # Use circuit breaker for email sending
        try:
            email_circuit_breaker.call(
                send_mail,
                subject='Reset your Ano password',
                message=plain_message,
                from_email=settings.EMAIL_HOST_USER or 'noreply@ano.com',
                recipient_list=[user_email],
                html_message=html_message,
                fail_silently=False,
            )
        except CircuitBreakerOpenException:
            logger.warning(f"Email circuit breaker is open, queuing password reset email for user_{user_id}")
            # Re-queue the task for later when circuit breaker might be closed
            raise self.retry(countdown=300)  # Retry in 5 minutes
        
        logger.info(f"Password reset email sent successfully to user_{user_id}")
        return f"Password reset email sent to {user_email}"
        
    except Exception as exc:
        logger.error(f"Failed to send password reset email to user_{user_id}: {str(exc)}")
        # Retry the task
        raise self.retry(exc=exc)
