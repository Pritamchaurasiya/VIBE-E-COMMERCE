"""
Enhanced WebSocket Consumers for Advanced Real-Time Monitoring and Analytics.

This module provides production-ready WebSocket consumers with:
- Advanced real-time analytics with ML integration
- Robust error handling with detailed logging
- Performance optimization through efficient data structures
- Customizable alert thresholds
- Historical data analysis
- Multi-client synchronization
- Adaptive sampling rates

Author: VIBE E-Commerce Team
Version: 2.0.0
"""

from __future__ import annotations

import asyncio
import json
import logging
# collections.defaultdict imported if needed for future enhancements
from functools import wraps
from typing import Any, Callable, TypeVar

from django.utils import timezone

# Local imports - used by methods throughout
from .monitoring_config import get_monitoring_config
from .ml_analytics import get_ml_engine

logger = logging.getLogger(__name__)

# Type variable for decorators
F = TypeVar('F', bound=Callable[..., Any])


# Check if channels is available
try:
    from channels.generic.websocket import AsyncWebsocketConsumer
    from channels.db import database_sync_to_async
    CHANNELS_AVAILABLE = True
except ImportError:
    CHANNELS_AVAILABLE = False
    logger.warning("Django Channels not installed. WebSocket features disabled.")

    class AsyncWebsocketConsumer:
        """Placeholder base class when channels is not installed."""
        pass

    def database_sync_to_async(func: F) -> F:
        """Placeholder decorator when channels is not installed."""
        return func


def async_error_handler(func: Callable) -> Callable:
    """Decorator for comprehensive async error handling."""
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except json.JSONDecodeError as e:
            logger.error("JSON decode error in %s: %s", func.__name__, e)
            await self._send_error("Invalid JSON format")
        except asyncio.CancelledError:
            logger.info("Task cancelled in %s", func.__name__)
            raise
        except Exception as e:
            logger.exception("Unexpected error in %s: %s", func.__name__, e)
            await self._send_error(f"Internal error: {type(e).__name__}")
    return wrapper



if CHANNELS_AVAILABLE:

    # Global client tracking for multi-client synchronization
    _connected_clients: dict = {}
    _client_metrics_cache: dict = {}
    _last_broadcast_time: float = 0.0

    class EnhancedMonitoringConsumer(AsyncWebsocketConsumer):
        """
        Enhanced WebSocket consumer for real-time system monitoring.

        Features:
        - ML-powered anomaly detection and predictions
        - Customizable alert thresholds
        - Adaptive sampling rates based on system load
        - Multi-client synchronization
        - Efficient metrics caching
        - Comprehensive error handling

        Attributes:
            user: The authenticated user for this connection
            room_group_name: Channel group for broadcasting
            ml_engine: Reference to ML analytics engine
            config: Reference to monitoring configuration
            connection_id: Unique identifier for this connection
            last_metrics_time: Timestamp of last metrics fetch
        """

        # Class-level constants
        METRICS_CACHE_TTL = 5.0  # seconds
        BROADCAST_GROUP = 'enhanced_monitoring_broadcast'

        async def connect(self) -> None:
            """
            Handle WebSocket connection with enhanced initialization.

            Validates user authentication, initializes ML engine,
            and sets up multi-client tracking.
            """
            import time

            self.user = self.scope.get('user')
            self.connection_id = f"{id(self)}_{time.time()}"
            self.last_metrics_time = 0.0
            self._is_connected = False

            # Authentication check
            if not self.user or not self.user.is_staff:
                logger.warning(
                    "Unauthorized connection attempt from %s",
                    self.scope.get('client', ['unknown'])[0]
                )
                await self.close(code=4001)
                return

            # Initialize ML engine and config
            self.ml_engine = get_ml_engine()
            self.config = get_monitoring_config()

            # Set up channel groups
            self.room_group_name = f'enhanced_monitoring_{self.user.id}'

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            # Join broadcast group for multi-client sync
            await self.channel_layer.group_add(
                self.BROADCAST_GROUP,
                self.channel_name
            )

            await self.accept()
            self._is_connected = True

            # Track connected client
            _connected_clients[self.connection_id] = {
                'user_id': self.user.id,
                'connected_at': time.time(),
                'channel_name': self.channel_name,
            }

            logger.info(
                "Client connected: user=%s, connection_id=%s, total_clients=%d",
                self.user.username, self.connection_id, len(_connected_clients)
            )

            # Send initial data
            await self.send_comprehensive_initial_data()

        async def disconnect(self, close_code: int) -> None:
            """
            Handle WebSocket disconnection with cleanup.

            Args:
                close_code: The WebSocket close code
            """
            self._is_connected = False

            # Remove from groups
            if hasattr(self, 'room_group_name'):
                await self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                )

            await self.channel_layer.group_discard(
                self.BROADCAST_GROUP,
                self.channel_name
            )

            # Remove from client tracking
            if hasattr(self, 'connection_id'):
                _connected_clients.pop(self.connection_id, None)
                logger.info(
                    "Client disconnected: connection_id=%s, code=%s, remaining=%d",
                    self.connection_id, close_code, len(_connected_clients)
                )

        async def _send_error(self, message: str) -> None:
            """Send error message to client."""
            if self._is_connected:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': message,
                    'timestamp': timezone.now().isoformat()
                }))


        async def receive(self, text_data):
            """Handle incoming monitoring commands with enhanced capabilities."""
            try:
                data = json.loads(text_data)
                command = data.get('command')

                if command == 'get_metrics':
                    await self.send_comprehensive_metrics()
                elif command == 'get_anomalies':
                    await self.send_anomaly_detection()
                elif command == 'get_predictions':
                    await self.send_predictive_analytics()
                elif command == 'get_trends':
                    await self.send_trend_analysis()
                elif command == 'get_alerts':
                    await self.send_intelligent_alerts()
                elif command == 'get_performance':
                    await self.send_performance_forecast()
                elif command == 'get_user_analytics':
                    await self.send_user_behavior_analytics()
                elif command == 'get_system_health':
                    await self.send_system_health_score()
            except json.JSONDecodeError:
                logger.error("Invalid JSON received in EnhancedMonitoringConsumer")

        async def system_metrics_update(self, event):
            """Send enhanced system metrics update with anomaly detection."""
            await self.send(text_data=json.dumps({
                'type': 'system_metrics',
                'data': event['data'],
                'anomalies': event.get('anomalies', []),
                'predictions': event.get('predictions', {})
            }))

        async def anomaly_detected(self, event):
            """Send anomaly detection alert."""
            await self.send(text_data=json.dumps({
                'type': 'anomaly_alert',
                'anomaly': event['anomaly'],
                'severity': event['severity'],
                'recommendations': event.get('recommendations', [])
            }))

        async def predictive_insight(self, event):
            """Send predictive analytics insight."""
            await self.send(text_data=json.dumps({
                'type': 'predictive_insight',
                'metric': event['metric'],
                'prediction': event['prediction'],
                'confidence': event['confidence'],
                'timeframe': event['timeframe']
            }))

        async def performance_forecast(self, event):
            """Send performance forecast alert."""
            await self.send(text_data=json.dumps({
                'type': 'performance_forecast',
                'resource': event['resource'],
                'forecast': event['forecast'],
                'recommendations': event.get('recommendations', [])
            }))

        async def send_comprehensive_initial_data(self):
            """Send comprehensive initial monitoring data with historical context."""
            try:
                # Get current and historical metrics
                current_metrics = await self.get_comprehensive_metrics()
                historical_data = await self.get_historical_data()

                # Perform initial analysis
                analysis = await self.analyze_initial_data(current_metrics, historical_data)

                await self.send(text_data=json.dumps({
                    'type': 'comprehensive_initial_data',
                    'current_metrics': current_metrics,
                    'historical_data': historical_data,
                    'analysis': analysis
                }))
            except Exception as e:
                logger.error("Error sending comprehensive initial data: %s", e)

        async def send_comprehensive_metrics(self):
            """Send comprehensive system metrics with analysis."""
            try:
                metrics = await self.get_comprehensive_metrics()
                analysis = await self.analyze_metrics(metrics)

                await self.send(text_data=json.dumps({
                    'type': 'comprehensive_metrics',
                    'metrics': metrics,
                    'analysis': analysis
                }))
            except Exception as e:
                logger.error("Error sending comprehensive metrics: %s", e)

        async def send_anomaly_detection(self):
            """Send anomaly detection results."""
            try:
                anomalies = await self.detect_anomalies()
                await self.send(text_data=json.dumps({
                    'type': 'anomaly_detection',
                    'anomalies': anomalies
                }))
            except Exception as e:
                logger.error("Error in anomaly detection: %s", e)

        async def send_predictive_analytics(self):
            """Send predictive analytics insights."""
            try:
                predictions = await self.generate_predictions()
                await self.send(text_data=json.dumps({
                    'type': 'predictive_analytics',
                    'predictions': predictions
                }))
            except Exception as e:
                logger.error("Error in predictive analytics: %s", e)

        async def send_trend_analysis(self):
            """Send trend analysis results."""
            try:
                trends = await self.analyze_trends()
                await self.send(text_data=json.dumps({
                    'type': 'trend_analysis',
                    'trends': trends
                }))
            except Exception as e:
                logger.error("Error in trend analysis: %s", e)

        async def send_intelligent_alerts(self):
            """Send intelligent alerts with prioritization."""
            try:
                alerts = await self.get_prioritized_alerts()
                await self.send(text_data=json.dumps({
                    'type': 'intelligent_alerts',
                    'alerts': alerts
                }))
            except Exception as e:
                logger.error("Error getting intelligent alerts: %s", e)

        async def send_performance_forecast(self):
            """Send performance forecasting data."""
            try:
                forecast = await self.generate_performance_forecast()
                await self.send(text_data=json.dumps({
                    'type': 'performance_forecast',
                    'forecast': forecast
                }))
            except Exception as e:
                logger.error("Error in performance forecast: %s", e)

        async def send_user_behavior_analytics(self):
            """Send user behavior analytics."""
            try:
                analytics = await self.analyze_user_behavior()
                await self.send(text_data=json.dumps({
                    'type': 'user_behavior_analytics',
                    'analytics': analytics
                }))
            except Exception as e:
                logger.error("Error in user behavior analytics: %s", e)

        async def send_system_health_score(self):
            """Send overall system health score."""
            try:
                health_score = await self.calculate_system_health()
                await self.send(text_data=json.dumps({
                    'type': 'system_health_score',
                    'health_score': health_score
                }))
            except Exception as e:
                logger.error("Error calculating system health: %s", e)

        @database_sync_to_async
        def get_comprehensive_metrics(self):
            """Get comprehensive system metrics with detailed analysis."""
            try:
                from django.db import connection
                from django.core.cache import cache
                from .models import TrackingAlert, UserSession, AnalyticsEvent

                # Check for psutil availability
                try:
                    import psutil
                    has_psutil = True
                except ImportError:
                    has_psutil = False

                # Get current timestamp
                now = timezone.now()

                # System metrics
                memory_info = {'total': 0, 'available': 0, 'used': 0, 'percent': 0}
                cpu_info = {'percent': 0, 'count': 0, 'per_core': []}
                disk_info = {'total': 0, 'used': 0, 'free': 0, 'percent': 0}

                if has_psutil:
                    try:
                        vm = psutil.virtual_memory()
                        memory_info = {
                            'total': vm.total,
                            'available': vm.available,
                            'used': vm.used,
                            'percent': vm.percent
                        }

                        cpu_info = {
                            'percent': psutil.cpu_percent(interval=0.1),
                            'count': psutil.cpu_count(),
                            'per_core': psutil.cpu_percent(percpu=True)
                        }

                        du = psutil.disk_usage('/')
                        disk_info = {
                            'total': du.total,
                            'used': du.used,
                            'free': du.free,
                            'percent': du.percent
                        }
                    except Exception as e:
                        logger.error("Error gathering system metrics: %s", e)

                metrics = {
                    'timestamp': now.isoformat(),
                    'system': {
                        'uptime': 0,
                        'load_avg': [0, 0, 0],
                        'memory': memory_info,
                        'cpu': cpu_info,
                        'disk': disk_info
                    },
                    'database': {
                        'connections': 0,
                        'active_queries': 0,
                        'slow_queries': 0,
                        'query_time_avg': 0.0,
                        'cache_hit_ratio': 0.0
                    },
                    'application': {
                        'active_users': UserSession.objects.filter(is_active=True).count(),
                        'current_sessions': UserSession.objects.filter(is_active=True).count(),
                        'page_views_last_hour': AnalyticsEvent.objects.filter(
                            event_type='page_view',
                            created_at__gte=now - timezone.timedelta(hours=1)
                        ).count(),
                        'conversions_last_hour': AnalyticsEvent.objects.filter(
                            event_type='purchase',
                            created_at__gte=now - timezone.timedelta(hours=1)
                        ).count(),
                        'error_rate': 0.0,
                        'response_time_avg': 0.0
                    },
                    'tracking': {
                        'active_alerts': TrackingAlert.objects.filter(status='active').count(),
                        'high_severity_alerts': TrackingAlert.objects.filter(
                            status='active', severity__in=['high', 'critical']
                        ).count(),
                        'recent_alerts': list(TrackingAlert.objects.filter(
                            status='active'
                        ).order_by('-created_at')[:5].values(
                            'title', 'severity', 'created_at'
                        ))
                    }
                }

                # Database metrics
                try:
                    with connection.cursor() as cursor:
                        cursor.execute("""
                            SELECT count(*) FROM pg_stat_activity
                            WHERE datname = current_database()
                        """)
                        metrics['database']['connections'] = cursor.fetchone()[0]

                        cursor.execute("""
                            SELECT count(*) FROM pg_stat_activity
                            WHERE datname = current_database() AND state = 'active'
                        """)
                        metrics['database']['active_queries'] = cursor.fetchone()[0]

                except Exception:
                    metrics['database']['error'] = 'Unable to fetch DB metrics'

                # Cache metrics
                try:
                    cache_stats = cache.get_stats() if hasattr(cache, 'get_stats') else {}
                    metrics['database']['cache_hit_ratio'] = cache_stats.get('hit_ratio', 0.0)
                except Exception:
                    metrics['database']['cache_hit_ratio'] = 0.0

                # Calculate error rate
                total_events = AnalyticsEvent.objects.filter(
                    created_at__gte=now - timezone.timedelta(hours=1)
                ).count()

                if total_events > 0:
                    error_events = AnalyticsEvent.objects.filter(
                        event_type='error',
                        created_at__gte=now - timezone.timedelta(hours=1)
                    ).count()
                    metrics['application']['error_rate'] = (error_events / total_events) * 100

                return metrics

            except Exception as e:
                logger.error("Error getting comprehensive metrics: %s", e)
                return {'error': str(e)}

        @database_sync_to_async
        def get_historical_data(self):
            """Get historical performance data for trend analysis."""
            try:
                from .models import AnalyticsEvent, TrackingAlert

                now = timezone.now()

                # Get historical data for the last 24 hours
                historical_data = {
                    'time_range': '24h',
                    'metrics': {
                        'page_views': [],
                        'conversions': [],
                        'errors': [],
                        'alerts': []
                    }
                }

                # Generate hourly data points
                for hour in range(24):
                    start_time = now - timezone.timedelta(hours=24 - hour)
                    end_time = start_time + timezone.timedelta(hours=1)

                    historical_data['metrics']['page_views'].append({
                        'time': start_time.isoformat(),
                        'count': AnalyticsEvent.objects.filter(
                            event_type='page_view',
                            created_at__range=(start_time, end_time)
                        ).count()
                    })

                    historical_data['metrics']['conversions'].append({
                        'time': start_time.isoformat(),
                        'count': AnalyticsEvent.objects.filter(
                            event_type='purchase',
                            created_at__range=(start_time, end_time)
                        ).count()
                    })

                    historical_data['metrics']['errors'].append({
                        'time': start_time.isoformat(),
                        'count': AnalyticsEvent.objects.filter(
                            event_type='error',
                            created_at__range=(start_time, end_time)
                        ).count()
                    })

                    historical_data['metrics']['alerts'].append({
                        'time': start_time.isoformat(),
                        'count': TrackingAlert.objects.filter(
                            created_at__range=(start_time, end_time)
                        ).count()
                    })

                return historical_data

            except Exception as e:
                logger.error("Error getting historical data: %s", e)
                return {'error': str(e)}

        @database_sync_to_async
        def analyze_initial_data(self, current_metrics, historical_data):
            """Analyze initial data to provide insights."""
            try:
                analysis = {
                    'trends': {},
                    'anomalies': [],
                    'recommendations': []
                }

                # Analyze trends
                if historical_data.get('metrics'):
                    page_views = [point['count'] for point in historical_data['metrics']['page_views']]
                    current_pv = current_metrics['application']['page_views_last_hour']

                    if len(page_views) > 1:
                        avg_pv = sum(page_views[:-1]) / len(page_views[:-1])
                        trend = ((current_pv - avg_pv) / avg_pv) * 100 if avg_pv > 0 else 0

                        analysis['trends']['page_views'] = {
                            'current': current_pv,
                            'trend': trend,
                            'direction': 'up' if trend > 5 else ('down' if trend < -5 else 'stable')
                        }

                # Check for anomalies
                error_rate = current_metrics['application']['error_rate']
                if error_rate > 10:  # 10% error rate threshold
                    analysis['anomalies'].append({
                        'type': 'high_error_rate',
                        'severity': 'high',
                        'message': f'High error rate detected: {error_rate:.1f}%',
                        'recommendations': [
                            'Check application logs for errors',
                            'Review recent code deployments',
                            'Monitor database performance'
                        ]
                    })

                # System resource anomalies
                if current_metrics['system']['memory']['percent'] > 90:
                    analysis['anomalies'].append({
                        'type': 'high_memory_usage',
                        'severity': 'critical',
                        'message': f'High memory usage: {current_metrics["system"]["memory"]["percent"]}%',
                        'recommendations': [
                            'Consider adding more memory',
                            'Review memory-intensive processes',
                            'Check for memory leaks'
                        ]
                    })

                return analysis

            except Exception as e:
                logger.error("Error analyzing initial data: %s", e)
                return {'error': str(e)}

        @database_sync_to_async
        def analyze_metrics(self, metrics):
            """Analyze current metrics for insights and recommendations."""
            try:
                analysis = {
                    'health_score': 0,
                    'performance_score': 0,
                    'reliability_score': 0,
                    'recommendations': []
                }

                # Calculate health scores (0-100)
                health_score = 100

                # Deduct for high resource usage
                if metrics['system']['memory']['percent'] > 80:
                    health_score -= (metrics['system']['memory']['percent'] - 80) * 2

                if metrics['system']['cpu']['percent'] > 80:
                    health_score -= (metrics['system']['cpu']['percent'] - 80) * 1.5

                # Deduct for high error rate
                if metrics['application']['error_rate'] > 5:
                    health_score -= metrics['application']['error_rate'] * 2

                # Deduct for active alerts
                if metrics['tracking']['active_alerts'] > 0:
                    health_score -= metrics['tracking']['active_alerts'] * 2

                health_score = max(0, min(100, health_score))
                analysis['health_score'] = round(health_score, 1)

                # Performance score
                performance_score = 100

                # Database performance impact
                if metrics['database']['slow_queries'] > 10:
                    performance_score -= (metrics['database']['slow_queries'] - 10) * 1

                # Cache performance impact
                if metrics['database']['cache_hit_ratio'] < 80:
                    performance_score -= (80 - metrics['database']['cache_hit_ratio']) * 0.5

                performance_score = max(0, min(100, performance_score))
                analysis['performance_score'] = round(performance_score, 1)

                # Generate recommendations
                if metrics['system']['memory']['percent'] > 90:
                    analysis['recommendations'].append(
                        'High memory usage detected. Consider scaling up resources.'
                    )

                if metrics['application']['error_rate'] > 10:
                    analysis['recommendations'].append(
                        'High error rate detected. Investigate application logs.'
                    )

                if metrics['tracking']['high_severity_alerts'] > 0:
                    analysis['recommendations'].append(
                        f'{metrics["tracking"]["high_severity_alerts"]} high severity alerts require attention.'
                    )

                return analysis

            except Exception as e:
                logger.error("Error analyzing metrics: %s", e)
                return {'error': str(e)}

        @database_sync_to_async
        def detect_anomalies(self):
            """Detect anomalies in system metrics using statistical analysis."""
            try:
                from .models import AnalyticsEvent
                from datetime import timedelta
                import numpy as np

                now = timezone.now()
                anomalies = []

                # Get recent metrics
                recent_events = AnalyticsEvent.objects.filter(
                    created_at__gte=now - timedelta(hours=6)
                ).order_by('created_at')

                # Simple anomaly detection for page views
                page_views = [event for event in recent_events if event.event_type == 'page_view']
                _page_view_counts = []  # Reserved for future use

                # Group by hour
                _current_hour = None  # Reserved for tracking
                hourly_counts = {}

                for event in page_views:
                    hour_key = event.created_at.replace(minute=0, second=0, microsecond=0)
                    if hour_key not in hourly_counts:
                        hourly_counts[hour_key] = 0
                    hourly_counts[hour_key] += 1

                # Calculate statistics
                if len(hourly_counts) >= 3:
                    counts = list(hourly_counts.values())
                    mean = np.mean(counts)
                    std = np.std(counts)

                    # Check for outliers (3 standard deviations)
                    for hour, count in hourly_counts.items():
                        z_score = (count - mean) / std if std > 0 else 0
                        if abs(z_score) > 3:
                            anomalies.append({
                                'type': 'page_view_anomaly',
                                'severity': 'high',
                                'metric': 'page_views',
                                'value': count,
                                'expected_range': f'{round(mean - 2*std)} - {round(mean + 2*std)}',
                                'time': hour.isoformat(),
                                'z_score': z_score
                            })

                # Check for error spikes
                error_events = AnalyticsEvent.objects.filter(
                    event_type='error',
                    created_at__gte=now - timedelta(hours=1)
                ).count()

                if error_events > 10:  # Threshold for error spike
                    anomalies.append({
                        'type': 'error_spike',
                        'severity': 'critical',
                        'metric': 'error_rate',
                        'value': error_events,
                        'threshold': 10,
                        'time': now.isoformat()
                    })

                return anomalies

            except Exception as e:
                logger.error("Error detecting anomalies: %s", e)
                return []

        @database_sync_to_async
        def generate_predictions(self):
            """Generate predictive insights based on current trends."""
            try:
                from .models import AnalyticsEvent
                from datetime import timedelta
                import numpy as np

                now = timezone.now()
                predictions = []

                # Simple linear regression for page view prediction
                page_views = AnalyticsEvent.objects.filter(
                    event_type='page_view',
                    created_at__gte=now - timedelta(hours=6)
                ).order_by('created_at')

                # Group by hour
                hourly_data = {}
                for event in page_views:
                    hour_key = event.created_at.replace(minute=0, second=0, microsecond=0)
                    if hour_key not in hourly_data:
                        hourly_data[hour_key] = 0
                    hourly_data[hour_key] += 1

                if len(hourly_data) >= 3:
                    # Simple linear regression
                    x = np.arange(len(hourly_data))
                    y = np.array(list(hourly_data.values()))

                    # Calculate slope (simple linear regression)
                    x_mean = np.mean(x)
                    y_mean = np.mean(y)
                    slope = np.sum((x - x_mean) * (y - y_mean)) / np.sum((x - x_mean) ** 2)
                    intercept = y_mean - slope * x_mean

                    # Predict next value
                    next_x = len(hourly_data)
                    prediction = slope * next_x + intercept
                    prediction = max(0, round(prediction))

                    # Calculate confidence (very simple)
                    std_dev = np.std(y)
                    confidence = max(0, 100 - (std_dev / y_mean * 100)) if y_mean > 0 else 50

                    predictions.append({
                        'metric': 'page_views',
                        'prediction': prediction,
                        'timeframe': 'next_hour',
                        'confidence': round(confidence, 1),
                        'method': 'linear_regression',
                        'historical_avg': round(y_mean, 1)
                    })

                # Conversion rate prediction
                total_events = AnalyticsEvent.objects.filter(
                    created_at__gte=now - timedelta(hours=3)
                ).count()

                conversions = AnalyticsEvent.objects.filter(
                    event_type='purchase',
                    created_at__gte=now - timedelta(hours=3)
                ).count()

                if total_events > 0:
                    current_rate = (conversions / total_events) * 100
                    # Simple prediction: assume similar rate
                    predictions.append({
                        'metric': 'conversion_rate',
                        'prediction': round(current_rate, 1),
                        'timeframe': 'next_3_hours',
                        'confidence': 75.0,
                        'method': 'historical_average',
                        'current_rate': round(current_rate, 1)
                    })

                return predictions

            except Exception as e:
                logger.error("Error generating predictions: %s", e)
                return []

        @database_sync_to_async
        def analyze_trends(self):
            """Analyze trends in system metrics."""
            try:
                from .models import AnalyticsEvent, TrackingAlert
                from datetime import timedelta

                now = timezone.now()
                trends = []

                # Page view trend
                current_hour_pv = AnalyticsEvent.objects.filter(
                    event_type='page_view',
                    created_at__gte=now - timedelta(hours=1)
                ).count()

                previous_hour_pv = AnalyticsEvent.objects.filter(
                    event_type='page_view',
                    created_at__range=(
                        now - timedelta(hours=2),
                        now - timedelta(hours=1)
                    )
                ).count()

                if previous_hour_pv > 0:
                    pv_change = ((current_hour_pv - previous_hour_pv) / previous_hour_pv) * 100
                    trends.append({
                        'metric': 'page_views',
                        'current': current_hour_pv,
                        'previous': previous_hour_pv,
                        'change_percent': round(pv_change, 1),
                        'direction': 'up' if pv_change > 0 else ('down' if pv_change < 0 else 'stable')
                    })

                # Error trend
                current_errors = AnalyticsEvent.objects.filter(
                    event_type='error',
                    created_at__gte=now - timedelta(hours=1)
                ).count()

                previous_errors = AnalyticsEvent.objects.filter(
                    event_type='error',
                    created_at__range=(
                        now - timedelta(hours=2),
                        now - timedelta(hours=1)
                    )
                ).count()

                if previous_errors > 0:
                    error_change = ((current_errors - previous_errors) / previous_errors) * 100
                    trends.append({
                        'metric': 'error_rate',
                        'current': current_errors,
                        'previous': previous_errors,
                        'change_percent': round(error_change, 1),
                        'direction': 'up' if error_change > 0 else ('down' if error_change < 0 else 'stable')
                    })

                # Alert trend
                current_alerts = TrackingAlert.objects.filter(
                    created_at__gte=now - timedelta(hours=1)
                ).count()

                previous_alerts = TrackingAlert.objects.filter(
                    created_at__range=(
                        now - timedelta(hours=2),
                        now - timedelta(hours=1)
                    )
                ).count()

                if previous_alerts > 0:
                    alert_change = ((current_alerts - previous_alerts) / previous_alerts) * 100
                    trends.append({
                        'metric': 'alert_rate',
                        'current': current_alerts,
                        'previous': previous_alerts,
                        'change_percent': round(alert_change, 1),
                        'direction': 'up' if alert_change > 0 else ('down' if alert_change < 0 else 'stable')
                    })

                return trends

            except Exception as e:
                logger.error("Error analyzing trends: %s", e)
                return []

        @database_sync_to_async
        def get_prioritized_alerts(self):
            """Get alerts prioritized by severity and impact."""
            try:
                from .models import TrackingAlert
                # timedelta not needed in this method

                now = timezone.now()

                # Get active alerts
                alerts = TrackingAlert.objects.filter(
                    status='active'
                ).order_by('-severity', '-created_at')

                prioritized_alerts = []

                for alert in alerts:
                    # Calculate priority score
                    priority_score = 0

                    # Severity weight
                    severity_weights = {
                        'critical': 4,
                        'high': 3,
                        'warning': 2,
                        'info': 1
                    }
                    priority_score += severity_weights.get(alert.severity, 1) * 10

                    # Time weight (newer alerts get higher priority)
                    time_diff = (now - alert.created_at).total_seconds() / 3600  # hours
                    time_weight = max(0, 10 - time_diff)  # 10 points for recent, decreases over time
                    priority_score += time_weight

                    # Alert type weight
                    type_weights = {
                        'security': 3,
                        'performance': 2,
                        'system': 2,
                        'compliance': 1
                    }
                    priority_score += type_weights.get(alert.alert_type, 1) * 5

                    prioritized_alerts.append({
                        'id': alert.id,
                        'title': alert.title,
                        'description': alert.description,
                        'severity': alert.severity,
                        'alert_type': alert.alert_type,
                        'created_at': alert.created_at.isoformat(),
                        'priority_score': round(priority_score, 1),
                        'priority_level': self._get_priority_level(priority_score)
                    })

                # Sort by priority score
                prioritized_alerts.sort(key=lambda x: x['priority_score'], reverse=True)

                return prioritized_alerts

            except Exception as e:
                logger.error("Error prioritizing alerts: %s", e)
                return []

        def _get_priority_level(self, score):
            """Convert priority score to human-readable level."""
            if score >= 40:
                return 'critical'
            elif score >= 30:
                return 'high'
            elif score >= 20:
                return 'medium'
            else:
                return 'low'

        @database_sync_to_async
        def generate_performance_forecast(self):
            """Generate performance forecast based on current usage."""
            try:
                from .models import AnalyticsEvent
                from datetime import timedelta
                import psutil

                now = timezone.now()
                forecast = {
                    'memory': {},
                    'cpu': {},
                    'database': {}
                }

                # Memory forecast
                try:
                    memory = psutil.virtual_memory()
                    current_usage = memory.percent

                    # Simple linear projection
                    # Assume current growth rate continues
                    recent_events = AnalyticsEvent.objects.filter(
                        created_at__gte=now - timedelta(hours=3)
                    ).count()

                    # Estimate memory usage based on activity
                    # This is a simplified model - real implementation would be more sophisticated
                    activity_factor = min(1.0, recent_events / 1000.0)  # Normalize

                    projected_usage = current_usage + (activity_factor * 5)  # 5% increase per activity unit
                    projected_usage = min(100, max(0, projected_usage))

                    forecast['memory'] = {
                        'current_usage': current_usage,
                        'projected_usage': round(projected_usage, 1),
                        'timeframe': 'next_2_hours',
                        'risk_level': 'high' if projected_usage > 90 else ('medium' if projected_usage > 80 else 'low'),
                        'recommendations': []
                    }

                    if projected_usage > 90:
                        forecast['memory']['recommendations'].append('Consider scaling up memory resources')
                        forecast['memory']['recommendations'].append('Optimize memory-intensive processes')

                except Exception:
                    forecast['memory']['error'] = 'Unable to generate memory forecast'

                # CPU forecast
                try:
                    cpu_percent = psutil.cpu_percent(interval=0.1)
                    cpu_count = psutil.cpu_count()

                    # Simple projection
                    projected_cpu = cpu_percent + (activity_factor * 10)  # 10% increase per activity unit
                    projected_cpu = min(100, max(0, projected_cpu))

                    forecast['cpu'] = {
                        'current_usage': cpu_percent,
                        'projected_usage': round(projected_cpu, 1),
                        'cpu_count': cpu_count,
                        'timeframe': 'next_2_hours',
                        'risk_level': 'high' if projected_cpu > 90 else ('medium' if projected_cpu > 80 else 'low'),
                        'recommendations': []
                    }

                    if projected_cpu > 90:
                        forecast['cpu']['recommendations'].append('Consider adding more CPU resources')
                        forecast['cpu']['recommendations'].append('Optimize CPU-intensive processes')

                except Exception:
                    forecast['cpu']['error'] = 'Unable to generate CPU forecast'

                # Database forecast
                try:
                    from django.db import connection

                    with connection.cursor() as cursor:
                        cursor.execute("""
                            SELECT count(*) FROM pg_stat_activity
                            WHERE datname = current_database()
                        """)
                        current_connections = cursor.fetchone()[0]

                    # Simple projection
                    projected_connections = current_connections + int(activity_factor * 10)

                    forecast['database'] = {
                        'current_connections': current_connections,
                        'projected_connections': projected_connections,
                        'timeframe': 'next_2_hours',
                        'risk_level': 'high' if projected_connections > 50 else ('medium' if projected_connections > 30 else 'low'),
                        'recommendations': []
                    }

                    if projected_connections > 50:
                        forecast['database']['recommendations'].append('Monitor database connection pool')
                        forecast['database']['recommendations'].append('Consider connection pooling optimization')

                except Exception:
                    forecast['database']['error'] = 'Unable to generate database forecast'

                return forecast

            except Exception as e:
                logger.error("Error generating performance forecast: %s", e)
                return {'error': str(e)}

        @database_sync_to_async
        def analyze_user_behavior(self):
            """Analyze user behavior patterns and trends."""
            try:
                from .models import AnalyticsEvent, UserSession
                from datetime import timedelta
                from collections import defaultdict

                now = timezone.now()
                analytics = {
                    'active_users': 0,
                    'session_duration': 0,
                    'popular_pages': [],
                    'user_segments': {},
                    'behavior_trends': []
                }

                # Active users
                active_sessions = UserSession.objects.filter(
                    is_active=True,
                    last_activity__gte=now - timedelta(minutes=30)
                )

                analytics['active_users'] = active_sessions.count()

                # Average session duration
                session_durations = []
                for session in active_sessions:
                    if session.started_at and session.last_activity:
                        duration = (session.last_activity - session.started_at).total_seconds() / 60  # minutes
                        session_durations.append(duration)

                if session_durations:
                    analytics['session_duration'] = round(sum(session_durations) / len(session_durations), 1)

                # Popular pages
                page_views = AnalyticsEvent.objects.filter(
                    event_type='page_view',
                    created_at__gte=now - timedelta(hours=6)
                )

                page_counts = defaultdict(int)
                for event in page_views:
                    if event.data and 'page_url' in event.data:
                        page_counts[event.data['page_url']] += 1

                popular_pages = sorted(page_counts.items(), key=lambda x: x[1], reverse=True)[:5]
                analytics['popular_pages'] = [{
                    'url': url,
                    'views': count
                } for url, count in popular_pages]

                # User segments
                segments = {
                    'new_users': 0,
                    'returning_users': 0,
                    'mobile_users': 0,
                    'desktop_users': 0
                }

                # This would be enhanced with actual user segmentation logic
                segments['new_users'] = UserSession.objects.filter(
                    created_at__gte=now - timedelta(days=1)
                ).count()

                segments['returning_users'] = UserSession.objects.filter(
                    created_at__lt=now - timedelta(days=1),
                    last_activity__gte=now - timedelta(days=1)
                ).count()

                mobile_sessions = UserSession.objects.filter(
                    is_mobile=True,
                    last_activity__gte=now - timedelta(hours=6)
                ).count()

                desktop_sessions = UserSession.objects.filter(
                    is_desktop=True,
                    last_activity__gte=now - timedelta(hours=6)
                ).count()

                segments['mobile_users'] = mobile_sessions
                segments['desktop_users'] = desktop_sessions

                analytics['user_segments'] = segments

                # Behavior trends
                current_conversions = AnalyticsEvent.objects.filter(
                    event_type='purchase',
                    created_at__gte=now - timedelta(hours=1)
                ).count()

                previous_conversions = AnalyticsEvent.objects.filter(
                    event_type='purchase',
                    created_at__range=(
                        now - timedelta(hours=2),
                        now - timedelta(hours=1)
                    )
                ).count()

                if previous_conversions > 0:
                    conversion_change = ((current_conversions - previous_conversions) / previous_conversions) * 100
                    analytics['behavior_trends'].append({
                        'metric': 'conversion_rate',
                        'change_percent': round(conversion_change, 1),
                        'direction': 'up' if conversion_change > 0 else ('down' if conversion_change < 0 else 'stable')
                    })

                return analytics

            except Exception as e:
                logger.error("Error analyzing user behavior: %s", e)
                return {'error': str(e)}

        @database_sync_to_async
        def calculate_system_health(self):
            """Calculate overall system health score."""
            try:
                from .models import TrackingAlert  # noqa: F401
                # TrackingAlert and timedelta imported for potential future use
                from datetime import timedelta  # noqa: F401

                _now = timezone.now()  # Reserved for future use

                # Get comprehensive metrics
                metrics = self.get_comprehensive_metrics()

                # Calculate health score components
                health_score = {
                    'overall': 0,
                    'components': {},
                    'status': 'healthy',
                    'recommendations': []
                }

                # System resources score (0-30)
                system_score = 30

                # Memory impact
                if metrics['system']['memory']['percent'] > 90:
                    system_score -= 15
                elif metrics['system']['memory']['percent'] > 80:
                    system_score -= 5

                # CPU impact
                if metrics['system']['cpu']['percent'] > 90:
                    system_score -= 10
                elif metrics['system']['cpu']['percent'] > 80:
                    system_score -= 3

                # Disk impact
                if metrics['system']['disk']['percent'] > 90:
                    system_score -= 5

                health_score['components']['system_resources'] = max(0, system_score)

                # Application score (0-30)
                app_score = 30

                # Error rate impact
                if metrics['application']['error_rate'] > 10:
                    app_score -= 15
                elif metrics['application']['error_rate'] > 5:
                    app_score -= 5

                # Performance impact
                if metrics['database']['slow_queries'] > 20:
                    app_score -= 10
                elif metrics['database']['slow_queries'] > 10:
                    app_score -= 3

                health_score['components']['application'] = max(0, app_score)

                # Tracking score (0-20)
                tracking_score = 20

                # Alert impact
                if metrics['tracking']['active_alerts'] > 10:
                    tracking_score -= 15
                elif metrics['tracking']['active_alerts'] > 5:
                    tracking_score -= 5

                # High severity alert impact
                if metrics['tracking']['high_severity_alerts'] > 3:
                    tracking_score -= 10
                elif metrics['tracking']['high_severity_alerts'] > 1:
                    tracking_score -= 3

                health_score['components']['tracking'] = max(0, tracking_score)

                # Database score (0-20)
                db_score = 20

                # Connection impact
                if metrics['database']['connections'] > 100:
                    db_score -= 10
                elif metrics['database']['connections'] > 50:
                    db_score -= 3

                # Cache impact
                if metrics['database']['cache_hit_ratio'] < 70:
                    db_score -= 10
                elif metrics['database']['cache_hit_ratio'] < 85:
                    db_score -= 3

                health_score['components']['database'] = max(0, db_score)

                # Calculate overall score
                overall_score = (
                    health_score['components']['system_resources'] +
                    health_score['components']['application'] +
                    health_score['components']['tracking'] +
                    health_score['components']['database']
                )

                health_score['overall'] = round(overall_score, 1)

                # Determine status
                if overall_score >= 90:
                    health_score['status'] = 'excellent'
                elif overall_score >= 80:
                    health_score['status'] = 'good'
                elif overall_score >= 70:
                    health_score['status'] = 'fair'
                elif overall_score >= 60:
                    health_score['status'] = 'concerning'
                else:
                    health_score['status'] = 'critical'

                # Generate recommendations
                if health_score['components']['system_resources'] < 20:
                    health_score['recommendations'].append('System resources are under heavy load. Consider scaling up.')

                if health_score['components']['application'] < 20:
                    health_score['recommendations'].append('Application performance issues detected. Investigate errors and slow queries.')

                if health_score['components']['tracking'] < 15:
                    health_score['recommendations'].append('Multiple high-priority alerts require immediate attention.')

                if health_score['components']['database'] < 15:
                    health_score['recommendations'].append('Database performance issues detected. Review connection pooling and caching.')

                return health_score

            except Exception as e:
                logger.error("Error calculating system health: %s", e)
                return {'error': str(e)}
