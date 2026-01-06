"""
Tracking Analytics API Views

Provides REST API endpoints for the tracking dashboard and analytics.
Requires admin authentication.
"""

import logging
from datetime import timedelta
from decimal import Decimal

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Avg, Count
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET

from .tracking_service import EnhancedTrackingService

logger = logging.getLogger(__name__)


def _get_model(model_name: str):
    """Lazy import of tracking models."""
    # pylint: disable=import-outside-toplevel
    from . import models
    # Mapping for models that might be missing or renamed
    if model_name == 'SessionTracker':
        if hasattr(models, 'SessionTracker'):
            return models.SessionTracker
        # Fallback or return None to handle gracefully
        return None

    if model_name == 'SystemAccessTracker':
        if hasattr(models, 'SystemAccessTracker'):
            return models.SystemAccessTracker
        return None

    if model_name == 'DataModificationTracker':
        if hasattr(models, 'DataModificationTracker'):
            return models.DataModificationTracker
        return None

    return getattr(models, model_name)


class DecimalEncoder:
    """Helper to convert Decimal to float for JSON serialization."""

    @staticmethod
    def process_dict(data):
        """Recursively convert Decimal values to floats."""
        if isinstance(data, dict):
            return {k: DecimalEncoder.process_dict(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [DecimalEncoder.process_dict(item) for item in data]
        elif isinstance(data, Decimal):
            return float(data)
        return data


@method_decorator([staff_member_required], name='dispatch')
class TrackingDashboardAPIView(View):
    """API view for tracking dashboard data."""

    def get(self, request, *args, **kwargs):
        """Get dashboard overview data."""
        try:
            days = int(request.GET.get('days', 7))
            cutoff = timezone.now() - timedelta(days=days)

            # Get basic statistics
            stats = EnhancedTrackingService.get_tracking_statistics()

            # Get configuration status
            TrackingConfiguration = _get_model('TrackingConfiguration')
            # pylint: disable=no-member
            configs = {
                config.category: config.is_enabled
                for config in TrackingConfiguration.objects.all()
            }

            # Get alert counts by severity
            TrackingAlert = _get_model('TrackingAlert')
            alerts = TrackingAlert.objects.filter(
                status='active'
            ).values('severity').annotate(count=Count('id'))

            alert_counts = {
                item['severity']: item['count']
                for item in alerts
            }

            # Get recent high-risk events
            SystemAccessTracker = _get_model('SystemAccessTracker')
            high_risk_events = SystemAccessTracker.objects.filter(
                access_timestamp__gte=cutoff,
                risk_level__in=['high', 'critical']
            ).order_by('-access_timestamp')[:10].values(
                'access_type', 'ip_address', 'access_timestamp', 'risk_level'
            )

            response_data = {
                'success': True,
                'data': {
                    'statistics': stats,
                    'configurations': configs,
                    'alert_counts': alert_counts,
                    'high_risk_events': list(high_risk_events),
                    'period_days': days,
                }
            }

            return JsonResponse(DecimalEncoder.process_dict(response_data))

        except Exception as exc:
            logger.error("Error in dashboard API: %s", exc)
            return JsonResponse({
                'success': False,
                'error': str(exc)
            }, status=500)


@method_decorator([staff_member_required, cache_page(60)], name='dispatch')
class TrackingAnalyticsAPIView(View):
    """API view for detailed tracking analytics."""

    def get(self, request, metric_type, *args, **kwargs):
        """Get analytics for a specific metric type."""
        try:
            days = int(request.GET.get('days', 7))
            cutoff = timezone.now() - timedelta(days=days)

            handlers = {
                'user_actions': self._get_user_actions_analytics,
                'system_access': self._get_system_access_analytics,
                'performance': self._get_performance_analytics,
                'sessions': self._get_session_analytics,
                'file_operations': self._get_file_operations_analytics,
                'data_modifications': self._get_data_modifications_analytics,
            }

            handler = handlers.get(metric_type)
            if not handler:
                return JsonResponse({
                    'success': False,
                    'error': f'Unknown metric type: {metric_type}'
                }, status=400)

            data = handler(cutoff, days)

            return JsonResponse(DecimalEncoder.process_dict({
                'success': True,
                'metric_type': metric_type,
                'data': data
            }))

        except Exception as exc:
            logger.error("Error in analytics API: %s", exc)
            return JsonResponse({
                'success': False,
                'error': str(exc)
            }, status=500)

    def _get_user_actions_analytics(self, cutoff, days):
        """Get user actions analytics."""
        UserActionTracker = _get_model('UserActionTracker')
        # pylint: disable=no-member
        action_distribution = UserActionTracker.objects.filter(
            action_timestamp__gte=cutoff
        ).values('action_type').annotate(count=Count('id')).order_by('-count')

        daily_trend = UserActionTracker.objects.filter(
            action_timestamp__gte=cutoff
        ).annotate(date=TruncDate('action_timestamp')).values('date').annotate(
            count=Count('id')
        ).order_by('date')

        return {
            'total_actions': UserActionTracker.objects.filter(
                action_timestamp__gte=cutoff
            ).count(),
            'action_distribution': list(action_distribution),
            'daily_trend': [
                {'date': str(item['date']), 'count': item['count']}
                for item in daily_trend
            ],
        }

    def _get_system_access_analytics(self, cutoff, days):
        """Get system access analytics."""
        SystemAccessTracker = _get_model('SystemAccessTracker')
        # pylint: disable=no-member
        access_distribution = SystemAccessTracker.objects.filter(
            access_timestamp__gte=cutoff
        ).values('access_type').annotate(count=Count('id')).order_by('-count')

        risk_distribution = SystemAccessTracker.objects.filter(
            access_timestamp__gte=cutoff
        ).values('risk_level').annotate(count=Count('id'))

        failed_attempts = SystemAccessTracker.objects.filter(
            access_timestamp__gte=cutoff,
            is_successful=False
        ).count()

        return {
            'total_accesses': SystemAccessTracker.objects.filter(
                access_timestamp__gte=cutoff
            ).count(),
            'access_distribution': list(access_distribution),
            'risk_distribution': {
                item['risk_level']: item['count']
                for item in risk_distribution
            },
            'failed_attempts': failed_attempts,
        }

    def _get_performance_analytics(self, cutoff, days):
        """Get performance analytics."""
        PerformanceMetric = _get_model('PerformanceMetric')
        # pylint: disable=no-member
        endpoint_performance = PerformanceMetric.objects.filter(
            timestamp__gte=cutoff,
            metric_type='response_time'
        ).values('endpoint').annotate(
            avg_time=Avg('metric_value'),
            request_count=Count('id')
        ).order_by('-avg_time')[:10]

        slow_requests = PerformanceMetric.objects.filter(
            timestamp__gte=cutoff,
            metric_type='response_time',
            metric_value__gt=2
        ).count()

        return {
            'endpoint_performance': list(endpoint_performance),
            'slow_requests_count': slow_requests,
        }

    def _get_session_analytics(self, cutoff, days):
        """Get session analytics."""
        SessionTracker = _get_model('SessionTracker')
        # pylint: disable=no-member
        active_sessions = SessionTracker.objects.filter(is_active=True).count()

        daily_sessions = SessionTracker.objects.filter(
            login_timestamp__gte=cutoff
        ).annotate(date=TruncDate('login_timestamp')).values('date').annotate(
            count=Count('id')
        ).order_by('date')

        device_distribution = SessionTracker.objects.filter(
            login_timestamp__gte=cutoff
        ).values('device_type').annotate(count=Count('id'))

        return {
            'active_sessions': active_sessions,
            'total_sessions': SessionTracker.objects.filter(
                login_timestamp__gte=cutoff
            ).count(),
            'daily_trend': [
                {'date': str(item['date']), 'count': item['count']}
                for item in daily_sessions
            ],
            'device_distribution': {
                item['device_type']: item['count']
                for item in device_distribution
            },
        }

    def _get_file_operations_analytics(self, cutoff, days):
        """Get file operations analytics."""
        SystemFileTracker = _get_model('SystemFileTracker')
        # pylint: disable=no-member
        operation_distribution = SystemFileTracker.objects.filter(
            operation_timestamp__gte=cutoff
        ).values('operation').annotate(count=Count('id')).order_by('-count')

        daily_trend = SystemFileTracker.objects.filter(
            operation_timestamp__gte=cutoff
        ).annotate(date=TruncDate('operation_timestamp')).values('date').annotate(
            count=Count('id')
        ).order_by('date')

        return {
            'total_operations': SystemFileTracker.objects.filter(
                operation_timestamp__gte=cutoff
            ).count(),
            'operation_distribution': list(operation_distribution),
            'daily_trend': [
                {'date': str(item['date']), 'count': item['count']}
                for item in daily_trend
            ],
        }

    def _get_data_modifications_analytics(self, cutoff, days):
        """Get data modifications analytics."""
        DataModificationTracker = _get_model('DataModificationTracker')
        # pylint: disable=no-member
        operation_distribution = DataModificationTracker.objects.filter(
            timestamp__gte=cutoff
        ).values('operation_type').annotate(count=Count('id'))

        model_distribution = DataModificationTracker.objects.filter(
            timestamp__gte=cutoff
        ).values('model_name').annotate(count=Count('id')).order_by('-count')[:10]

        return {
            'total_modifications': DataModificationTracker.objects.filter(
                timestamp__gte=cutoff
            ).count(),
            'operation_distribution': {
                item['operation_type']: item['count']
                for item in operation_distribution
            },
            'model_distribution': list(model_distribution),
        }


@method_decorator([staff_member_required], name='dispatch')
class TrackingAlertsAPIView(View):
    """API view for managing tracking alerts."""

    def get(self, request, *args, **kwargs):
        """Get alerts list."""
        try:
            status_filter = request.GET.get('status', 'active')
            severity_filter = request.GET.get('severity')
            limit = int(request.GET.get('limit', 50))

            TrackingAlert = _get_model('TrackingAlert')
            # pylint: disable=no-member
            queryset = TrackingAlert.objects.all()

            if status_filter:
                queryset = queryset.filter(status=status_filter)

            if severity_filter:
                queryset = queryset.filter(severity=severity_filter)

            alerts = queryset.order_by('-created_at')[:limit].values(
                'id', 'alert_type', 'title', 'description',
                'severity', 'status', 'created_at', 'triggered_by'
            )

            return JsonResponse({
                'success': True,
                'alerts': list(alerts),
                'total': queryset.count()
            })

        except Exception as exc:
            logger.error("Error fetching alerts: %s", exc)
            return JsonResponse({
                'success': False,
                'error': str(exc)
            }, status=500)

    def post(self, request, *args, **kwargs):
        """Acknowledge or resolve an alert."""
        try:
            import json
            data = json.loads(request.body)

            alert_id = data.get('alert_id')
            action = data.get('action')

            if not alert_id or not action:
                return JsonResponse({
                    'success': False,
                    'error': 'alert_id and action are required'
                }, status=400)

            TrackingAlert = _get_model('TrackingAlert')
            # pylint: disable=no-member
            alert = TrackingAlert.objects.get(id=alert_id)

            if action == 'acknowledge':
                alert.status = 'acknowledged'
                alert.acknowledged_by = request.user
                alert.acknowledged_at = timezone.now()
            elif action == 'resolve':
                alert.status = 'resolved'
                alert.resolved_by = request.user
                alert.resolved_at = timezone.now()
            elif action == 'false_positive':
                alert.status = 'false_positive'
                alert.resolved_by = request.user
                alert.resolved_at = timezone.now()
            else:
                return JsonResponse({
                    'success': False,
                    'error': f'Unknown action: {action}'
                }, status=400)

            alert.save()

            return JsonResponse({
                'success': True,
                'message': f'Alert {action}d successfully',
                'alert_id': alert_id
            })

        except Exception as exc:
            logger.error("Error updating alert: %s", exc)
            return JsonResponse({
                'success': False,
                'error': str(exc)
            }, status=500)


@require_GET
@staff_member_required
def tracking_realtime_stats(request):
    """Get real-time tracking statistics."""
    try:
        last_hour = timezone.now() - timedelta(hours=1)
        last_5_min = timezone.now() - timedelta(minutes=5)

        SessionTracker = _get_model('SessionTracker')
        SystemAccessTracker = _get_model('SystemAccessTracker')
        TrackingAlert = _get_model('TrackingAlert')
        PerformanceMetric = _get_model('PerformanceMetric')

        # pylint: disable=no-member
        stats = {
            'active_sessions': SessionTracker.objects.filter(
                is_active=True
            ).count(),
            'requests_last_5_min': SystemAccessTracker.objects.filter(
                access_timestamp__gte=last_5_min
            ).count(),
            'requests_last_hour': SystemAccessTracker.objects.filter(
                access_timestamp__gte=last_hour
            ).count(),
            'active_alerts': TrackingAlert.objects.filter(
                status='active'
            ).count(),
            'avg_response_time': PerformanceMetric.objects.filter(
                timestamp__gte=last_hour,
                metric_type='response_time'
            ).aggregate(avg=Avg('metric_value')).get('avg') or 0,
            'timestamp': timezone.now().isoformat(),
        }

        return JsonResponse(DecimalEncoder.process_dict({
            'success': True,
            'data': stats
        }))

    except Exception as exc:
        logger.error("Error fetching realtime stats: %s", exc)
        return JsonResponse({
            'success': False,
            'error': str(exc)
        }, status=500)
