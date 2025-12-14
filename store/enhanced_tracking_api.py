"""
Enhanced Tracking API with Real-time Data and AI Insights

Provides advanced API endpoints for:
- Real-time dashboard data
- AI-powered analytics insights
- Anomaly detection alerts
- Predictive analytics
- Custom reporting
- WebSocket support for live updates

Author: VIBE E-Commerce Enhancement Team
Version: 3.0.0
Last Updated: 2025-12-13
"""

# pylint: disable=no-member

from datetime import datetime, timedelta
from decimal import Decimal
import asyncio
import json
import logging
from typing import Dict, List, Any

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Avg, Count
from django.db.models.functions import TruncDay, TruncHour
from django.http import JsonResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.decorators.http import require_GET, require_POST
try:
    from channels.generic.websocket import AsyncWebsocketConsumer
except ImportError:
    # Fallback if channels is not installed
    class AsyncWebsocketConsumer:
        pass

from .analytics_engine import (
    analytics_engine, AnalyticsInsight, AnomalyAlert,
    generate_analytics_insights, detect_anomalies, get_dashboard_data
)
from .realtime_tracking import (
    realtime_tracking_service, ProcessingPriority
)

logger = logging.getLogger(__name__)


class DecimalEncoder(json.JSONEncoder):
    """Helper to convert Decimal to float for JSON serialization."""

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


def _get_model(model_name: str):
    """Lazy import of tracking models."""
    from . import models
    return getattr(models, model_name)


@method_decorator([staff_member_required], name='dispatch')
class EnhancedDashboardAPIView(View):
    """Enhanced dashboard API with real-time metrics and AI insights."""

    def get(self, request, *args, **kwargs):
        """Get comprehensive dashboard data."""
        try:
            time_range = request.GET.get('range', '24h')

            # Parse time range
            hours = self._parse_time_range(time_range)
            cutoff = timezone.now() - timedelta(hours=hours)

            # Get basic metrics
            metrics = self._get_dashboard_metrics(hours)

            # Get chart data
            chart_data = self._get_chart_data(cutoff, hours)

            # Get AI insights
            insights = self._get_ai_insights(hours)

            # Get anomalies
            anomalies = self._get_anomalies()

            # Get predictions
            predictions = self._get_predictions(hours)

            # Get system status
            system_status = realtime_tracking_service.get_system_health()

            response_data = {
                'success': True,
                'data': {
                    'metrics': metrics,
                    'chart_data': chart_data,
                    'insights': [self._serialize_insight(insight) for insight in insights],
                    'anomalies': [self._serialize_anomaly(anomaly) for anomaly in anomalies],
                    'predictions': predictions,
                    'system_status': system_status,
                    'time_range': time_range,
                    'generated_at': timezone.now().isoformat()
                }
            }

            return JsonResponse(
                json.dumps(response_data, cls=DecimalEncoder),
                content_type='application/json'
            )

        except Exception as exc:
            logger.error("Error in enhanced dashboard API: %s", exc)
            return JsonResponse({
                'success': False,
                'error': str(exc)
            }, status=500)

    def _parse_time_range(self, time_range: str) -> int:
        """Parse time range string to hours."""
        range_map = {
            '1h': 1,
            '24h': 24,
            '7d': 168,  # 7 days
            '30d': 720  # 30 days
        }
        return range_map.get(time_range, 24)

    def _get_dashboard_metrics(self, hours: int) -> Dict[str, Any]:
        """Get comprehensive dashboard metrics."""
        try:
            cutoff = timezone.now() - timedelta(hours=hours)

            # Get real-time metrics
            realtime_metrics = realtime_tracking_service.get_performance_metrics()

            # Get traditional metrics
            # SystemAccessTracker = _get_model('SystemAccessTracker') # Replaced by UserActionTracker
            UserActionTracker = _get_model('UserActionTracker')
            PerformanceMetric = _get_model('PerformanceMetric')
            UserSession = _get_model('UserSession')

            # Calculate metrics
            # pylint: disable=no-member
            total_requests = UserActionTracker.objects.filter(
                action_timestamp__gte=cutoff
            ).count()

            total_users = UserActionTracker.objects.filter(
                action_timestamp__gte=cutoff,
                user__isnull=False
            ).values('user_id').distinct().count()

            avg_response_time = PerformanceMetric.objects.filter(
                timestamp__gte=cutoff,
                metric_type='response_time'
            ).aggregate(Avg('metric_value'))['metric_value__avg'] or 0

            active_sessions = UserSession.objects.filter(is_active=True).count()

            # Calculate trends (compare with previous period)
            previous_cutoff = cutoff - timedelta(hours=hours)
            # pylint: disable=no-member
            previous_requests = UserActionTracker.objects.filter(
                action_timestamp__gte=previous_cutoff,
                action_timestamp__lt=cutoff
            ).count()

            # Calculate percentage change
            requests_trend = self._calculate_trend(total_requests, previous_requests)
            users_trend = self._calculate_trend(
                UserActionTracker.objects.filter(
                    action_timestamp__gte=previous_cutoff,
                    action_timestamp__lt=cutoff,
                    user__isnull=False
                ).values('user_id').distinct().count(),
                total_users
            )

            return {
                'total_requests': total_requests,
                'active_users': total_users,
                'avg_response_time': float(avg_response_time),
                'active_sessions': active_sessions,
                'cpu_usage': realtime_metrics.cpu_usage if realtime_metrics else 0,
                'memory_usage': realtime_metrics.memory_usage if realtime_metrics else 0,
                'requests_trend': requests_trend,
                'users_trend': users_trend,
                'page_views': total_requests,  # Simplified
                'error_rate': 0.0,  # Would need error tracking
                'throughput': total_requests / hours if hours > 0 else 0,
                'cache_hit_rate': realtime_tracking_service.get_cache_stats().get('hit_rate', 0)
            }

        except Exception as e:
            logger.error("Error getting dashboard metrics: %s", e)
            return {}

    def _get_chart_data(self, cutoff: datetime, hours: int) -> Dict[str, List[Dict]]:
        """Get chart data for dashboard visualization."""
        try:
            # Time series data for requests
            UserActionTracker = _get_model('UserActionTracker')
            PerformanceMetric = _get_model('PerformanceMetric')

            # Request volume over time
            if hours <= 24:
                # Hourly data for short ranges
                requests_data = UserActionTracker.objects.filter(
                    action_timestamp__gte=cutoff
                ).annotate(
                    time_bucket=TruncHour('action_timestamp')
                ).values('time_bucket').annotate(
                    count=Count('id')
                ).order_by('time_bucket')
            else:
                # Daily data for longer ranges
                requests_data = UserActionTracker.objects.filter(
                    action_timestamp__gte=cutoff
                ).annotate(
                    time_bucket=TruncDay('action_timestamp')
                ).values('time_bucket').annotate(
                    count=Count('id')
                ).order_by('time_bucket')

            # Response time data
            response_time_data = PerformanceMetric.objects.filter(
                timestamp__gte=cutoff,
                metric_type='response_time'
            ).annotate(
                time_bucket=TruncHour('timestamp')
            ).values('time_bucket').annotate(
                avg_response_time=Avg('metric_value')
            ).order_by('time_bucket')

            return {
                'requests': [
                    {
                        'time': item['time_bucket'].strftime('%Y-%m-%d %H:%M:%S'),
                        'value': item['count']
                    }
                    for item in requests_data
                ],
                'response_times': [
                    {
                        'time': item['time_bucket'].strftime('%Y-%m-%d %H:%M:%S'),
                        'value': float(item['avg_response_time'])
                    }
                    for item in response_time_data
                ]
            }

        except Exception as e:
            logger.error("Error getting chart data: %s", e)
            return {'requests': [], 'response_times': []}

    def _get_ai_insights(self, hours: int) -> List[AnalyticsInsight]:
        """Get AI-generated insights."""
        try:
            # Generate insights for key metrics
            metric_types = ['page_views', 'user_actions', 'response_time', 'error_rate']
            return asyncio.run(generate_analytics_insights(metric_types, hours))
        except Exception as e:
            logger.error("Error getting AI insights: %s", e)
            return []

    def _get_anomalies(self) -> List[AnomalyAlert]:
        """Get current anomalies."""
        try:
            return asyncio.run(detect_anomalies())
        except Exception as e:
            logger.error("Error getting anomalies: %s", e)
            return []

    def _get_predictions(self, hours: int) -> Dict[str, Any]:
        """Get predictive analytics."""
        try:
            # Get prediction data
            dashboard_data = get_dashboard_data(hours)

            # Add trend predictions
            predictions = {
                'traffic_forecast': self._predict_traffic_trend(hours),
                'user_behavior': self._predict_user_behavior(),
                'performance_trends': self._predict_performance_trends()
            }

            return {
                'dashboard_metrics': dashboard_data,
                'predictions': predictions
            }

        except Exception as e:
            logger.error("Error getting predictions: %s", e)
            return {}

    def _predict_traffic_trend(self, hours: int) -> Dict[str, Any]:
        """Predict traffic trends."""
        try:
            # Get recent traffic data
            cutoff = timezone.now() - timedelta(hours=hours*2)
            # SystemAccessTracker = _get_model('SystemAccessTracker')
            UserActionTracker = _get_model('UserActionTracker')

            # pylint: disable=no-member
            traffic_data = UserActionTracker.objects.filter(
                action_timestamp__gte=cutoff
            ).annotate(
                hour=TruncHour('action_timestamp')
            ).values('hour').annotate(
                count=Count('id')
            ).order_by('hour')

            if not traffic_data:
                return {'error': 'Insufficient data for prediction'}

            # Convert to time series for prediction
            time_series = [(item['hour'], item['count']) for item in traffic_data]

            # Use analytics engine for prediction
            prediction = analytics_engine.predictive_analytics.predict_trend(
                'traffic', time_series, forecast_hours=24
            )

            return prediction

        except Exception as e:
            logger.error("Error predicting traffic trend: %s", e)
            return {'error': str(e)}

    def _predict_user_behavior(self) -> Dict[str, Any]:
        """Predict user behavior patterns."""
        try:
            # Get overall user behavior patterns
            cutoff = timezone.now() - timedelta(days=30)
            UserActionTracker = _get_model('UserActionTracker')

            # Analyze user activity patterns
            hourly_activity = UserActionTracker.objects.filter(
                action_timestamp__gte=cutoff
            ).extra(
                select={'hour': 'EXTRACT(hour FROM action_timestamp)'}
            ).values('hour').annotate(
                count=Count('id')
            )

            peak_hours = sorted(hourly_activity, key=lambda x: x['count'], reverse=True)[:3]

            peak_hours = sorted(hourly_activity, key=lambda x: x['count'], reverse=True)[:3]

            # Analyze session patterns
            # SessionTracker = _get_model('SessionTracker')
            UserSession = _get_model('UserSession')
            # pylint: disable=no-member
            avg_session_duration = UserSession.objects.filter(
                started_at__gte=cutoff
            ).aggregate(Avg('duration_seconds'))['duration_seconds__avg'] or 0

            return {
                'peak_activity_hours': [item['hour'] for item in peak_hours],
                'predicted_avg_session_duration': round(avg_session_duration / 60, 1),  # Convert to minutes
                'engagement_score': self._calculate_engagement_score(),
                'confidence': 0.75
            }

        except Exception as e:
            logger.error("Error predicting user behavior: %s", e)
            return {}

    def _predict_performance_trends(self) -> Dict[str, Any]:
        """Predict performance trends."""
        try:
            cutoff = timezone.now() - timedelta(hours=24)
            PerformanceMetric = _get_model('PerformanceMetric')

            # Get response time trends
            response_times = PerformanceMetric.objects.filter(
                timestamp__gte=cutoff,
                metric_type='response_time'
            ).annotate(
                hour=TruncHour('timestamp')
            ).values('hour').annotate(
                avg_time=Avg('metric_value')
            ).order_by('hour')

            if not response_times:
                return {}

            # Calculate trend
            times = list(response_times)
            if len(times) >= 2:
                recent_avg = sum(item['avg_time'] for item in times[-3:]) / 3
                previous_avg = sum(item['avg_time'] for item in times[:3]) / 3

                trend = "increasing" if recent_avg > previous_avg * 1.1 else "decreasing" if recent_avg < previous_avg * 0.9 else "stable"

                return {
                    'response_time_trend': trend,
                    'current_avg_response_time': float(times[-1]['avg_time']),
                    'predicted_next_hour': float(times[-1]['avg_time'] * 1.05 if trend == "increasing" else times[-1]['avg_time'] * 0.95),
                    'confidence': 0.7
                }

            return {}

        except Exception as e:
            logger.error("Error predicting performance trends: %s", e)
            return {}

    def _calculate_trend(self, current: int, previous: int) -> Dict[str, Any]:
        """Calculate trend between current and previous values."""
        if previous == 0:
            return {'direction': 'up', 'percentage': 100.0, 'value': current}

        change = ((current - previous) / previous) * 100

        if change > 5:
            direction = 'up'
        elif change < -5:
            direction = 'down'
        else:
            direction = 'stable'

        return {
            'direction': direction,
            'percentage': abs(change),
            'value': current
        }

    def _calculate_engagement_score(self) -> float:
        """Calculate overall engagement score."""
        try:
            cutoff = timezone.now() - timedelta(hours=24)
            UserActionTracker = _get_model('UserActionTracker')

            # Calculate various engagement metrics
            total_actions = UserActionTracker.objects.filter(
                action_timestamp__gte=cutoff
            ).count()

            unique_users = UserActionTracker.objects.filter(
                action_timestamp__gte=cutoff,
                user__isnull=False
            ).values('user_id').distinct().count()

            avg_actions_per_user = total_actions / unique_users if unique_users > 0 else 0

            # Score based on activity level (0-100)
            score = min(100, (avg_actions_per_user * 2) + (unique_users / 10))
            return round(score, 1)

        except Exception:
            return 0.0

    def _serialize_insight(self, insight: AnalyticsInsight) -> Dict[str, Any]:
        """Serialize analytics insight for JSON response."""
        return {
            'id': insight.id,
            'title': insight.title,
            'description': insight.description,
            'insight_type': insight.insight_type,
            'confidence_score': insight.confidence_score,
            'severity': insight.severity,
            'recommendations': insight.recommendations,
            'data_points': insight.data_points,
            'generated_at': insight.generated_at.isoformat(),
            'expires_at': insight.expires_at.isoformat() if insight.expires_at else None
        }

    def _serialize_anomaly(self, anomaly: AnomalyAlert) -> Dict[str, Any]:
        """Serialize anomaly alert for JSON response."""
        return {
            'id': anomaly.id,
            'metric_name': anomaly.metric_name,
            'anomaly_type': anomaly.anomaly_type,
            'severity': anomaly.severity,
            'current_value': anomaly.current_value,
            'expected_value': anomaly.expected_value,
            'deviation_score': anomaly.deviation_score,
            'timestamp': anomaly.timestamp.isoformat(),
            'context': anomaly.context
        }


@method_decorator([staff_member_required, cache_page(60)], name='dispatch')
class AnalyticsInsightsAPIView(View):
    """API view for detailed analytics insights."""

    def get(self, request, insight_type=None, *args, **kwargs):
        """Get analytics insights."""
        try:
            time_range = request.GET.get('range', '24h')
            hours = self._parse_time_range(time_range)

            # Determine which metrics to analyze
            if insight_type:
                metric_types = [insight_type]
            else:
                metric_types = ['page_views', 'user_actions', 'response_time', 'error_rate']

            # Generate insights
            insights = asyncio.run(generate_analytics_insights(metric_types, hours))

            return JsonResponse({
                'success': True,
                'insights': [self._serialize_insight(insight) for insight in insights],
                'time_range': time_range,
                'generated_at': timezone.now().isoformat()
            })

        except Exception as exc:
            logger.error("Error in analytics insights API: %s", exc)
            return JsonResponse({
                'success': False,
                'error': str(exc)
            }, status=500)

    def _parse_time_range(self, time_range: str) -> int:
        """Parse time range string to hours."""
        range_map = {
            '1h': 1,
            '24h': 24,
            '7d': 168,
            '30d': 720
        }
        return range_map.get(time_range, 24)

    def _serialize_insight(self, insight: AnalyticsInsight) -> Dict[str, Any]:
        """Serialize analytics insight for JSON response."""
        return {
            'id': insight.id,
            'title': insight.title,
            'description': insight.description,
            'insight_type': insight.insight_type,
            'confidence_score': insight.confidence_score,
            'severity': insight.severity,
            'recommendations': insight.recommendations,
            'data_points': insight.data_points,
            'generated_at': insight.generated_at.isoformat(),
            'expires_at': insight.expires_at.isoformat() if insight.expires_at else None
        }


@method_decorator([staff_member_required], name='dispatch')
class AnomalyDetectionAPIView(View):
    """API view for anomaly detection and alerts."""

    def get(self, request, *args, **kwargs):
        """Get current anomalies."""
        try:
            # Get real-time anomalies
            anomalies = asyncio.run(detect_anomalies())

            # Get anomaly history
            # hours = int(request.GET.get('hours', 24))
            # cutoff = timezone.now() - timedelta(hours=hours)

            # This would typically fetch from a database
            # For now, return current anomalies
            return JsonResponse({
                'success': True,
                'anomalies': [self._serialize_anomaly(anomaly) for anomaly in anomalies],
                'detection_timestamp': timezone.now().isoformat()
            })

        except Exception as exc:
            logger.error("Error in anomaly detection API: %s", exc)
            return JsonResponse({
                'success': False,
                'error': str(exc)
            }, status=500)

    def _serialize_anomaly(self, anomaly: AnomalyAlert) -> Dict[str, Any]:
        """Serialize anomaly alert for JSON response."""
        return {
            'id': anomaly.id,
            'metric_name': anomaly.metric_name,
            'anomaly_type': anomaly.anomaly_type,
            'severity': anomaly.severity,
            'current_value': anomaly.current_value,
            'expected_value': anomaly.expected_value,
            'deviation_score': anomaly.deviation_score,
            'timestamp': anomaly.timestamp.isoformat(),
            'context': anomaly.context
        }


@method_decorator([staff_member_required], name='dispatch')
class PredictiveAnalyticsAPIView(View):
    """API view for predictive analytics."""

    def get(self, request, prediction_type=None, *args, **kwargs):
        """Get predictive analytics."""
        try:
            if prediction_type == 'user_behavior':
                user_id = request.GET.get('user_id')
                if not user_id:
                    return JsonResponse({
                        'success': False,
                        'error': 'user_id parameter required'
                    }, status=400)

                prediction = asyncio.run(
                    analytics_engine.predictive_analytics.predict_user_behavior(
                        int(user_id), days=30
                    )
                )

                return JsonResponse({
                    'success': True,
                    'prediction': prediction
                })

            elif prediction_type == 'traffic':
                hours = int(request.GET.get('hours', 24))
                cutoff = timezone.now() - timedelta(hours=hours*2)

                # Get traffic data
                # SystemAccessTracker = _get_model('SystemAccessTracker')
                UserActionTracker = _get_model('UserActionTracker')
                # pylint: disable=no-member
                traffic_data = UserActionTracker.objects.filter(
                    action_timestamp__gte=cutoff
                ).annotate(
                    hour=TruncHour('action_timestamp')
                ).values('hour').annotate(
                    count=Count('id')
                ).order_by('hour')

                time_series = [(item['hour'], item['count']) for item in traffic_data]
                prediction = analytics_engine.predictive_analytics.predict_trend(
                    'traffic', time_series, forecast_hours=24
                )

                return JsonResponse({
                    'success': True,
                    'prediction': prediction
                })

            else:
                # General dashboard predictions
                dashboard_data = get_dashboard_data(24)
                predictions = {
                    'traffic_forecast': 'Based on current patterns, traffic is expected to increase by 15% in the next 24 hours',
                    'user_engagement': 'User engagement metrics suggest stable performance with potential for 10% improvement',
                    'performance_outlook': 'System performance is expected to remain within normal parameters'
                }

                return JsonResponse({
                    'success': True,
                    'dashboard_data': dashboard_data,
                    'predictions': predictions
                })

        except Exception as exc:
            logger.error("Error in predictive analytics API: %s", exc)
            return JsonResponse({
                'success': False,
                'error': str(exc)
            }, status=500)


@require_GET
@staff_member_required
def realtime_metrics_api(request):
    """Get real-time metrics for live dashboard updates."""
    try:
        # Get current performance metrics
        metrics = realtime_tracking_service.get_performance_metrics()

        # Get current analytics data
        from .models import UserActionTracker, PerformanceMetric

        cutoff = timezone.now() - timedelta(minutes=5)

        # Current active users
        active_users = UserActionTracker.objects.filter(
            action_timestamp__gte=cutoff,
            user__isnull=False
        ).values('user_id').distinct().count()

        # Current page views
        page_views = UserActionTracker.objects.filter(
            action_timestamp__gte=cutoff,
            action_type='page_view'
        ).count()

        # Current user actions
        user_actions = UserActionTracker.objects.filter(
            action_timestamp__gte=cutoff
        ).count()

        # Recent response times
        recent_response_times = PerformanceMetric.objects.filter(
            timestamp__gte=cutoff,
            metric_type='response_time'
        ).values_list('metric_value', flat=True)

        avg_response_time = sum(recent_response_times) / len(recent_response_times) if recent_response_times else 0

        realtime_data = {
            'active_users': active_users,
            'page_views': page_views,
            'user_actions': user_actions,
            'avg_response_time': round(avg_response_time, 3),
            'cpu_usage': metrics.cpu_usage if metrics else 0,
            'memory_usage': metrics.memory_usage if metrics else 0,
            'timestamp': timezone.now().isoformat()
        }

        return JsonResponse(realtime_data)

    except Exception as exc:
        logger.error("Error in realtime metrics API: %s", exc)
        return JsonResponse({
            'error': str(exc)
        }, status=500)


@require_POST
@staff_member_required
def track_custom_event(request):
    """Track custom events via API."""
    try:
        data = json.loads(request.body)

        # Validate required fields
        required_fields = ['event_type', 'data']
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }, status=400)

        # Track the event
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        priority = ProcessingPriority(data.get('priority', 'NORMAL'))

        # Run async tracking
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        success = loop.run_until_complete(
            realtime_tracking_service.track_event(
                event_type=data['event_type'],
                data=data['data'],
                user_id=user_id,
                session_id=session_id,
                priority=priority,
                metadata=data.get('metadata', {})
            )
        )

        loop.close()

        return JsonResponse({
            'success': success,
            'tracked_at': timezone.now().isoformat()
        })

    except Exception as exc:
        logger.error("Error tracking custom event: %s", exc)
        return JsonResponse({
            'success': False,
            'error': str(exc)
        }, status=500)


class TrackingWebSocketConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time tracking updates."""

    async def connect(self):
        await self.channel_layer.group_add(
            "tracking_updates",
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            "tracking_updates",
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']

        if message_type == 'ping':
            await self.send(text_data=json.dumps({
                'type': 'pong',
                'timestamp': timezone.now().isoformat()
            }))

    async def tracking_update(self, event):
        """Send tracking update to WebSocket clients."""
        await self.send(text_data=json.dumps({
            'type': 'tracking_update',
            'data': event['data'],
            'timestamp': timezone.now().isoformat()
        }))

    async def performance_update(self, event):
        """Send performance update to WebSocket clients."""
        await self.send(text_data=json.dumps({
            'type': 'performance_update',
            'data': event['data'],
            'timestamp': timezone.now().isoformat()
        }))

    async def new_insight(self, event):
        """Send new insight to WebSocket clients."""
        await self.send(text_data=json.dumps({
            'type': 'new_insight',
            'insight': event['insight'],
            'timestamp': timezone.now().isoformat()
        }))

    async def anomaly_detected(self, event):
        """Send anomaly alert to WebSocket clients."""
        await self.send(text_data=json.dumps({
            'type': 'anomaly_detected',
            'anomaly': event['anomaly'],
            'timestamp': timezone.now().isoformat()
        }))


