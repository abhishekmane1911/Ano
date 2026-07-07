"""
Enhanced authentication service that works with hashed identities.
Part of the Advanced Gamification Modules - Security hardening.
"""
import logging
from typing import Optional
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.core.exceptions import ValidationError
from .models import HashedIdentity
from .services import IdentityHasher

User = get_user_model()
logger = logging.getLogger('ano_platform.security')


class HashedIdentityBackend(ModelBackend):
    """
    Authentication backend that works with hashed email identities.
    Falls back to regular email authentication for backward compatibility.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user using hashed identity or regular email.
        Maintains backward compatibility with existing authentication.
        """
        if username is None or password is None:
            return None
        
        # First try to find user by hashed identity
        user = self._authenticate_by_hash(username, password)
        if user:
            return user
        
        # Fall back to regular email authentication
        user = self._authenticate_by_email(username, password)
        if user:
            # If user exists but doesn't have hashed identity, create one
            self._ensure_hashed_identity(user)
            return user
        
        return None
    
    def _authenticate_by_hash(self, email: str, password: str) -> Optional[User]:
        """Authenticate using hashed identity"""
        try:
            # Find all hashed identities and check each one
            hashed_identities = HashedIdentity.objects.select_related('user').all()
            
            for hashed_identity in hashed_identities:
                try:
                    if IdentityHasher.verify_email_hash(
                        email, 
                        hashed_identity.email_hash, 
                        hashed_identity.salt
                    ):
                        user = hashed_identity.user
                        if user.check_password(password) and self.user_can_authenticate(user):
                            logger.info(f"Successful hash-based authentication for user_{user.id}")
                            return user
                        break
                except Exception as inner_e:
                    logger.error(f"Error verifying hash for identity {hashed_identity.id}: {inner_e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error in hash-based authentication: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
        
        return None
    
    def _authenticate_by_email(self, email: str, password: str) -> Optional[User]:
        """Authenticate using regular email (backward compatibility)"""
        try:
            user = User.objects.get(email__iexact=email)
            if user.check_password(password) and self.user_can_authenticate(user):
                logger.info(f"Successful email-based authentication for user_{user.id}")
                return user
        except User.DoesNotExist:
            logger.debug(f"User not found with email: {email}")
        except Exception as e:
            logger.error(f"Error in email-based authentication: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
        
        return None
    
    def _ensure_hashed_identity(self, user: User) -> None:
        """Ensure user has a hashed identity record"""
        try:
            if not hasattr(user, 'hashed_identity') or user.hashed_identity is None:
                email_hash, salt = IdentityHasher.hash_email(user.email)
                HashedIdentity.objects.create(
                    user=user,
                    email_hash=email_hash,
                    salt=salt
                )
                logger.info(f"Created hashed identity for user_{user.id}")
        except Exception as e:
            logger.error(f"Failed to create hashed identity for user_{user.id}: {e}")


class EnhancedAuthenticationService:
    """
    Service for enhanced authentication operations with hashed identities.
    """
    
    @classmethod
    def find_user_by_email(cls, email: str) -> Optional[User]:
        """
        Find user by email, checking both hashed and regular email.
        Used for password reset and other operations.
        """
        # First try hashed identities
        user = cls._find_user_by_hash(email)
        if user:
            return user
        
        # Fall back to regular email lookup
        try:
            return User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return None
    
    @classmethod
    def _find_user_by_hash(cls, email: str) -> Optional[User]:
        """Find user by checking hashed identities"""
        try:
            hashed_identities = HashedIdentity.objects.select_related('user').all()
            
            for hashed_identity in hashed_identities:
                if IdentityHasher.verify_email_hash(
                    email, 
                    hashed_identity.email_hash, 
                    hashed_identity.salt
                ):
                    return hashed_identity.user
        except Exception as e:
            logger.error(f"Error finding user by hash: {e}")
        
        return None
    
    @classmethod
    def is_email_registered(cls, email: str) -> bool:
        """
        Check if email is already registered, checking both hashed and regular.
        Used during registration to prevent duplicates.
        """
        return cls.find_user_by_email(email) is not None
    
    @classmethod
    def create_user_with_hash(cls, email: str, password: str, **extra_fields) -> User:
        """
        Create a new user and immediately create hashed identity.
        """
        # Create user normally
        user = User.objects.create_user(
            email=email,
            username=email,  # Use email as username
            password=password,
            **extra_fields
        )
        
        # Create hashed identity
        try:
            email_hash, salt = IdentityHasher.hash_email(email)
            HashedIdentity.objects.create(
                user=user,
                email_hash=email_hash,
                salt=salt
            )
            logger.info(f"Created user with hashed identity: user_{user.id}")
        except Exception as e:
            logger.error(f"Failed to create hashed identity for new user: {e}")
            # Don't fail user creation if hashing fails
        
        return user
    
    @classmethod
    def migrate_user_to_hash(cls, user: User) -> bool:
        """
        Migrate an existing user to use hashed identity.
        Returns True if successful, False otherwise.
        """
        try:
            if hasattr(user, 'hashed_identity') and user.hashed_identity:
                return True  # Already has hashed identity
            
            email_hash, salt = IdentityHasher.hash_email(user.email)
            HashedIdentity.objects.create(
                user=user,
                email_hash=email_hash,
                salt=salt
            )
            logger.info(f"Migrated user_{user.id} to hashed identity")
            return True
        except Exception as e:
            logger.error(f"Failed to migrate user_{user.id} to hashed identity: {e}")
            return False
    
    @classmethod
    def verify_email_ownership(cls, user: User, email: str) -> bool:
        """
        Verify that a user owns a specific email address.
        Works with both hashed and regular email storage.
        """
        # Check regular email
        if user.email.lower() == email.lower():
            return True
        
        # Check hashed identity
        try:
            if hasattr(user, 'hashed_identity') and user.hashed_identity:
                return IdentityHasher.verify_email_hash(
                    email,
                    user.hashed_identity.email_hash,
                    user.hashed_identity.salt
                )
        except Exception as e:
            logger.error(f"Error verifying email ownership for user_{user.id}: {e}")
        
        return False