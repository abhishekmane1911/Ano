"""
Custom permissions for admin dashboard
"""
from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Permission class to check if user is an admin/staff member
    """
    
    def has_permission(self, request, view):
        """Check if user is authenticated and is staff/admin"""
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.is_staff or request.user.is_superuser)
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permission class to allow read-only access to all, but write access only to admins
    """
    
    def has_permission(self, request, view):
        """Allow read access to all, write access only to admins"""
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.is_staff or request.user.is_superuser)
        )
