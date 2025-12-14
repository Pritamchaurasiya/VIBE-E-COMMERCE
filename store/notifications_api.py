"""
Notification API Views
REST API endpoints for managing user notifications.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .notifications import NotificationService


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_notifications(request):
    """
    Get notifications for the authenticated user.

    Query Parameters:
        - unread_only: If 'true', only return unread notifications
        - limit: Maximum number of notifications (default: 50, max: 100)
    """
    unread_only = request.GET.get('unread_only', '').lower() == 'true'
    limit = min(int(request.GET.get('limit', 50)), 100)

    service = NotificationService()
    notifications = service.get_user_notifications(
        user=request.user,
        unread_only=unread_only,
        limit=limit
    )

    return Response({
        'status': 'success',
        'count': len(notifications),
        'notifications': notifications,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_unread_count(request):
    """Get count of unread notifications for the authenticated user."""
    service = NotificationService()
    count = service.get_unread_count(user=request.user)

    return Response({
        'status': 'success',
        'unread_count': count,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_as_read(request):
    """
    Mark notifications as read.

    Request Body:
        - notification_ids: List of notification IDs to mark as read.
                           If empty or not provided, marks all as read.
    """
    notification_ids = request.data.get('notification_ids', [])

    service = NotificationService()

    if notification_ids:
        count = service.mark_as_read(
            user=request.user,
            notification_ids=notification_ids
        )
    else:
        count = service.mark_all_as_read(user=request.user)

    return Response({
        'status': 'success',
        'marked_count': count,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_all_read(request):
    """Mark all notifications as read for the authenticated user."""
    service = NotificationService()
    count = service.mark_all_as_read(user=request.user)

    return Response({
        'status': 'success',
        'marked_count': count,
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_notification(request, notification_id):
    """Delete a specific notification."""
    service = NotificationService()
    deleted = service.delete_notification(
        user=request.user,
        notification_id=notification_id
    )

    if deleted:
        return Response({
            'status': 'success',
            'message': 'Notification deleted',
        })

    return Response({
        'status': 'error',
        'message': 'Notification not found',
    }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_settings(_request):
    """Get notification settings for the authenticated user."""
    # This would typically fetch from a UserNotificationSettings model
    # For now, return default settings
    return Response({
        'status': 'success',
        'settings': {
            'email_notifications': True,
            'push_notifications': True,
            'order_updates': True,
            'promotions': True,
            'price_drops': True,
            'flash_sales': True,
            'messages': True,
        }
    })


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_notification_settings(request):
    """Update notification settings for the authenticated user."""
    # This would typically update a UserNotificationSettings model
    settings = request.data.get('settings', {})

    # Validate settings
    valid_keys = {
        'email_notifications', 'push_notifications', 'order_updates',
        'promotions', 'price_drops', 'flash_sales', 'messages'
    }

    for key in settings:
        if key not in valid_keys:
            return Response({
                'status': 'error',
                'message': f'Invalid setting: {key}',
            }, status=status.HTTP_400_BAD_REQUEST)

    # For now, just return success (would save to model in production)
    return Response({
        'status': 'success',
        'message': 'Settings updated',
        'settings': settings,
    })
