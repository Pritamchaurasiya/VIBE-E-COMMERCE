"""
Custom permission classes for the store API.

Provides granular access control for vendors, admins, and customers.
"""
from rest_framework import permissions


class IsVendorUser(permissions.BasePermission):
    """
    Custom permission to only allow vendors to access a view.
    """
    message = "You must be a registered vendor to perform this action."

    def has_permission(self, request, view):
        """Check if the user is authenticated and has a vendor account."""
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'vendor')
        )

    def has_object_permission(self, request, view, obj):
        """Check if the vendor owns the object."""
        # For objects with vendor field, ensure ownership
        if hasattr(obj, 'vendor'):
            return obj.vendor == request.user.vendor
        return True


class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users (staff) to access a view.
    """
    message = "Admin access required for this action."

    def has_permission(self, request, view):
        """Check if the user is authenticated and is a staff member."""
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_staff
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to allow owners of an object or admins.
    """
    message = "You don't have permission to access this resource."

    def has_object_permission(self, request, view, obj):
        """Check if user owns the object or is admin."""
        # Admin can access anything
        if request.user.is_staff:
            return True
        # Check for user field
        if hasattr(obj, 'user'):
            return obj.user == request.user
        # Check for created_by field
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        return False


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    Allow read-only access for unauthenticated users,
    write access only for authenticated users.
    """

    def has_permission(self, request, view):
        """Allow safe methods for all, others require authentication."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated


class IsVendorOwnerOrReadOnly(permissions.BasePermission):
    """
    Allow read-only access for all,
    write access only for the vendor who owns the object.
    """
    message = "Only the product vendor can modify this resource."

    def has_permission(self, request, view):
        """Allow safe methods for all."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Check vendor ownership for write operations."""
        if request.method in permissions.SAFE_METHODS:
            return True
        # Must be the vendor who owns the object
        if hasattr(obj, 'vendor') and hasattr(request.user, 'vendor'):
            return obj.vendor == request.user.vendor
        return False


class CanManageOrders(permissions.BasePermission):
    """
    Permission for order management.
    Users can view their own orders, vendors can manage orders for their products.
    """
    message = "You don't have permission to manage this order."

    def has_object_permission(self, request, view, obj):
        """Check order access permissions."""
        user = request.user

        # Admin can access all
        if user.is_staff:
            return True

        # User can access their own orders
        if hasattr(obj, 'user') and obj.user == user:
            return True

        # Vendor can access orders containing their products
        if hasattr(user, 'vendor'):
            # pylint: disable=import-outside-toplevel
            from .models import OrderItem
            return OrderItem.objects.filter(  # pylint: disable=no-member
                order=obj,
                vendor=user.vendor
            ).exists()

        return False
