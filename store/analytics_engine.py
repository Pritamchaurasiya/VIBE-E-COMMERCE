"""
Advanced Analytics Engine with ML-based Insights

This module provides enterprise-grade analytics with:
- Machine learning-based pattern recognition
- Predictive analytics for trend forecasting
- Anomaly detection algorithms
- Real-time data processing
- Advanced statistical analysis
- User behavior clustering
- Performance optimization insights

Author: VIBE E-Commerce Enhancement Team
Version: 3.0.0
Last Updated: 2025-12-13
"""

import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from collections import defaultdict, deque

import numpy as np
# pandas might be missing in some environments, so we rely on numpy for core stats
# import pandas as pd

# Django imports
from django.db.models import Avg, Count
from django.db.models.functions import TruncHour, ExtractHour, ExtractWeekDay
from django.utils import timezone

logger = logging.getLogger(__name__)


@dataclass
class AnalyticsInsight:
    """Represents a generated analytics insight."""
    id: str
    title: str
    description: str
    insight_type: str
    confidence_score: float
    severity: str
    recommendations: List[str]
    data_points: Dict[str, Any]
    generated_at: datetime
    expires_at: Optional[datetime] = None


@dataclass
class AnomalyAlert:
    """Represents an detected anomaly."""
    id: str
    metric_name: str
    anomaly_type: str
    severity: str
    current_value: float
    expected_value: float
    deviation_score: float
    timestamp: datetime
    context: Dict[str, Any]


class StatisticalAnalyzer:
    """Statistical analysis utilities for analytics."""

    @staticmethod
    def calculate_z_score(value: float, mean: float, std_dev: float) -> float:
        """Calculate z-score for anomaly detection."""
        if std_dev == 0:
            return 0.0
        return (value - mean) / std_dev

    @staticmethod
    def calculate_percentile(data: List[float], percentile: float) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower_index = int(index)
            upper_index = lower_index + 1
            weight = index - lower_index
            return sorted_data[lower_index] * (1 - weight) + sorted_data[upper_index] * weight

    @staticmethod
    def detect_trend(data: List[float], window_size: int = 7) -> str:
        """Detect trend direction in time series data."""
        if len(data) < window_size * 2:
            return "insufficient_data"

        recent_avg = np.mean(data[-window_size:])
        previous_avg = np.mean(data[-window_size*2:-window_size])

        if recent_avg > previous_avg * 1.05:
            return "increasing"
        elif recent_avg < previous_avg * 0.95:
            return "decreasing"
        else:
            return "stable"


class AnomalyDetector:
    """Advanced anomaly detection using multiple algorithms."""

    def __init__(self):
        self.statistical_analyzer = StatisticalAnalyzer()
        self.historical_data = defaultdict(deque)
        self.anomaly_thresholds = {
            'z_score_threshold': 2.5,
            'percentile_low': 5,
            'percentile_high': 95,
            'rolling_window': 24  # hours
        }

    def add_data_point(self, metric_name: str, value: float, timestamp: datetime):
        """Add a new data point for analysis."""
        self.historical_data[metric_name].append((timestamp, value))

        # Keep only recent data to manage memory
        cutoff_time = timestamp - timedelta(days=30)
        while (self.historical_data[metric_name] and
               self.historical_data[metric_name][0][0] < cutoff_time):
            self.historical_data[metric_name].popleft()

    def detect_anomaly(self, metric_name: str, value: float,
                      timestamp: datetime) -> Optional[AnomalyAlert]:
        """Detect if current value is anomalous."""
        if metric_name not in self.historical_data:
            return None

        historical_values = [v for t, v in self.historical_data[metric_name]]
        if len(historical_values) < 24:  # Need at least 24 data points
            return None

        # Method 1: Z-score based detection
        z_score = self.statistical_analyzer.calculate_z_score(
            value, np.mean(historical_values), np.std(historical_values)
        )

        if abs(z_score) > self.anomaly_thresholds['z_score_threshold']:
            return self._create_anomaly_alert(
                metric_name, value, timestamp, "statistical_outlier",
                np.mean(historical_values), abs(z_score), {"z_score": z_score}
            )

        # Method 2: Percentile-based detection
        p5 = self.statistical_analyzer.calculate_percentile(
            historical_values, self.anomaly_thresholds['percentile_low']
        )
        p95 = self.statistical_analyzer.calculate_percentile(
            historical_values, self.anomaly_thresholds['percentile_high']
        )

        if value < p5 or value > p95:
            expected_value = np.median(historical_values)
            severity = "high" if value < p5 * 0.8 or value > p95 * 1.2 else "medium"
            return self._create_anomaly_alert(
                metric_name, value, timestamp, "percentile_outlier",
                expected_value, abs(value - expected_value) / expected_value,
                {"percentile_5": p5, "percentile_95": p95, "severity": severity}
            )

        return None

    def _create_anomaly_alert(self, metric_name: str, current_value: float,
                            timestamp: datetime, anomaly_type: str,
                            expected_value: float, deviation_score: float,
                            context: Dict[str, Any]) -> AnomalyAlert:
        """Create an anomaly alert object."""
        severity = "high" if deviation_score > 0.5 else "medium"

        return AnomalyAlert(
            id=f"{metric_name}_{timestamp.isoformat()}",
            metric_name=metric_name,
            anomaly_type=anomaly_type,
            severity=severity,
            current_value=current_value,
            expected_value=expected_value,
            deviation_score=deviation_score,
            timestamp=timestamp,
            context=context
        )


class PredictiveAnalytics:
    """Predictive analytics for trend forecasting."""

    def __init__(self):
        self.models = {}
        self.prediction_cache = {}
        self.statistical_analyzer = StatisticalAnalyzer()

    def predict_trend(self, metric_name: str, data_points: List[Tuple[datetime, float]],
                     forecast_hours: int = 24) -> Dict[str, Any]:
        """Predict future trends using simple linear regression."""
        if len(data_points) < 10:
            return {"error": "Insufficient data for prediction"}

        try:
            # Convert timestamps to numeric values (hours since first point)
            timestamps = [(t - data_points[0][0]).total_seconds() / 3600
                         for t, v in data_points]
            values = [v for t, v in data_points]

            # Simple linear regression
            n = len(timestamps)
            sum_x = sum(timestamps)
            sum_y = sum(values)
            sum_xy = sum(x * y for x, y in zip(timestamps, values))
            sum_x2 = sum(x * x for x in timestamps)

            # Use safe division
            denom = (n * sum_x2 - sum_x * sum_x)
            if denom == 0:
                raise ValueError("Denominator is zero in linear regression")

            # Calculate slope and intercept
            slope = (n * sum_xy - sum_x * sum_y) / denom
            intercept = (sum_y - slope * sum_x) / n

            # Make predictions
            future_predictions = []
            for i in range(1, forecast_hours + 1):
                future_time = timestamps[-1] + i
                predicted_value = slope * future_time + intercept
                future_predictions.append({
                    "timestamp": data_points[0][0] + timedelta(hours=future_time),
                    "predicted_value": max(0, predicted_value)  # Ensure non-negative
                })

            # Calculate confidence metrics
            r_squared = self._calculate_r_squared(values, timestamps, slope, intercept)
            trend_direction = "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"

            return {
                "predictions": future_predictions,
                "trend_direction": trend_direction,
                "slope": slope,
                "confidence": r_squared,
                "forecast_hours": forecast_hours,
                "generated_at": timezone.now()
            }

        except Exception as e:
            logger.error("Prediction error for %s: %s", metric_name, e)
            return {"error": str(e)}

    def _calculate_r_squared(self, values: List[float], timestamps: List[float],
                           slope: float, intercept: float) -> float:
        """Calculate R-squared for regression quality."""
        try:
            n = len(values)
            if n <= 2:
                return 0.0

            # Calculate predicted values
            predicted = [slope * x + intercept for x in timestamps]

            # Calculate R-squared
            mean_actual = sum(values) / n
            ss_tot = sum((y - mean_actual) ** 2 for y in values)
            ss_res = sum((y - p) ** 2 for y, p in zip(values, predicted))

            if ss_tot == 0:
                return 1.0 if ss_res == 0 else 0.0

            return 1 - (ss_res / ss_tot)

        except Exception:
            return 0.0

    def predict_user_behavior(self, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Predict user behavior patterns."""
        try:
            from .models import UserActionTracker

            # Get user activity data
            cutoff = timezone.now() - timedelta(days=days)

            base_qs = UserActionTracker.objects.filter(  # pylint: disable=no-member
                user_id=user_id,
                action_timestamp__gte=cutoff
            )

            if not base_qs.exists():
                return {"error": "No user data available"}

            # Bolt Optimization: Database Aggregations
            # Action counts
            action_counts_qs = base_qs.values('action_type').annotate(count=Count('id'))
            action_counts = {item['action_type']: item['count'] for item in action_counts_qs}

            # Hourly activity
            hourly_qs = base_qs.annotate(hour=ExtractHour('action_timestamp')).values('hour').annotate(count=Count('id'))
            hourly_activity = defaultdict(int, {item['hour']: item['count'] for item in hourly_qs})

            # Daily activity
            # Django ExtractWeekDay returns 1 (Sunday) to 7 (Saturday)
            # Python timestamp.weekday() returns 0 (Monday) to 6 (Sunday)
            daily_qs = base_qs.annotate(weekday=ExtractWeekDay('action_timestamp')).values('weekday').annotate(count=Count('id'))
            daily_activity = defaultdict(int)
            for item in daily_qs:
                # Convert Django 1-7 (Sun-Sat) to Python 0-6 (Mon-Sun)
                py_weekday = (item['weekday'] - 2) % 7
                daily_activity[py_weekday] = item['count']

            # Predict next week activity
            total_actions = sum(action_counts.values())
            avg_daily_actions = total_actions / days

            # Most active hours
            peak_hours = sorted(hourly_activity.items(), key=lambda x: x[1], reverse=True)[:3]

            # Most active days
            day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            peak_days = [(day_names[i], count) for i, count in
                        sorted(daily_activity.items(), key=lambda x: x[1], reverse=True)[:3]]

            return {
                "user_id": user_id,
                "predicted_daily_actions": round(avg_daily_actions, 1),
                "peak_activity_hours": [hour for hour, _ in peak_hours],
                "most_active_days": peak_days,
                "preferred_actions": dict(sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:5]),
                "engagement_score": min(100, total_actions / days),
                "prediction_confidence": min(95, (total_actions / days) * 2),
                "generated_at": timezone.now()
            }

        except Exception as e:
            logger.error("User behavior prediction error: %s", e)
            return {"error": str(e)}


class AdvancedAnalyticsEngine:
    """Main analytics engine orchestrating all analytics functions."""

    def __init__(self):
        self.anomaly_detector = AnomalyDetector()
        self.predictive_analytics = PredictiveAnalytics()
        self.insights_cache = {}
        self._executor = ThreadPoolExecutor(max_workers=4)

    async def generate_insights(self, metric_types: List[str] = None,
                              time_range_hours: int = 24) -> List[AnalyticsInsight]:
        """Generate comprehensive analytics insights."""
        if metric_types is None:
            metric_types = ['page_views', 'user_actions', 'response_time', 'error_rate']

        insights = []

        try:
            for metric_type in metric_types:
                # Generate insights for each metric type
                insight_tasks = [
                    self._analyze_trend_insights(metric_type, time_range_hours),
                    self._analyze_performance_insights(metric_type, time_range_hours),
                    self._analyze_user_behavior_insights(metric_type, time_range_hours)
                ]

                results = await asyncio.gather(*insight_tasks, return_exceptions=True)
                for result in results:
                    if isinstance(result, list):
                        insights.extend(result)
                    elif isinstance(result, AnalyticsInsight):
                        insights.append(result)

            # Cache insights
            cache_key = f"analytics_insights_{metric_types}_{time_range_hours}"
            self.insights_cache[cache_key] = {
                'insights': insights,
                'generated_at': timezone.now(),
                'expires_at': timezone.now() + timedelta(hours=1)
            }

            return insights

        except Exception as e:
            logger.error("Error generating insights: %s", e)
            return []

    async def _analyze_trend_insights(self, metric_type: str,
                                    time_range_hours: int) -> List[AnalyticsInsight]:
        """Analyze trends and generate insights."""
        try:
            cutoff = timezone.now() - timedelta(hours=time_range_hours)

            # Get time series data
            if metric_type == 'page_views':
                from .models import UserActionTracker
                data = UserActionTracker.objects.filter(  # pylint: disable=no-member
                    action_type='page_view',
                    action_timestamp__gte=cutoff
                ).annotate(
                    hour=TruncHour('action_timestamp')
                ).values('hour').annotate(
                    count=Count('id')
                ).order_by('hour')
            else:
                from .models import PerformanceMetric
                data = PerformanceMetric.objects.filter( # pylint: disable=no-member
                    metric_type=metric_type,
                    timestamp__gte=cutoff
                ).annotate(
                    hour=TruncHour('timestamp')
                ).values('hour').annotate(
                    avg_value=Avg('metric_value')
                ).order_by('hour')

            if not data:
                return []

            # Convert to list of (timestamp, value) tuples
            time_series = [(item['hour'], item.get('count', item.get('avg_value', 0)))
                          for item in data]

            # Generate trend analysis
            values = [v for t, v in time_series]
            trend = self.predictive_analytics.statistical_analyzer.detect_trend(values)

            insights = []

            if trend == "increasing":
                insights.append(AnalyticsInsight(
                    id=f"trend_{metric_type}_increasing_{timezone.now().isoformat()}",
                    title=f"{metric_type.replace('_', ' ').title()} Trending Up",
                    description=f"Detected increasing trend in {metric_type} over the last {time_range_hours} hours",
                    insight_type="trend",
                    confidence_score=0.8,
                    severity="info",
                    recommendations=[
                        "Monitor resource usage to handle increased load",
                        "Consider scaling infrastructure if trend continues",
                        "Analyze what factors are driving the increase"
                    ],
                    data_points={
                        "metric_type": metric_type,
                        "trend": trend,
                        "data_points": len(values),
                        "avg_value": np.mean(values) if values else 0
                    },
                    generated_at=timezone.now()
                ))

            return insights

        except Exception as e:
            logger.error("Trend analysis error for %s: %s", metric_type, e)
            return []

    async def _analyze_performance_insights(self, metric_type: str,
                                          time_range_hours: int) -> List[AnalyticsInsight]:
        """Analyze performance metrics and generate insights."""
        try:
            if metric_type == 'response_time':
                cutoff = timezone.now() - timedelta(hours=time_range_hours)
                from .models import PerformanceMetric

                # Get recent response times
                response_times = PerformanceMetric.objects.filter( # pylint: disable=no-member
                    metric_type='response_time',
                    timestamp__gte=cutoff
                ).values_list('metric_value', flat=True)

                if not response_times:
                    return []

                response_times = list(response_times)
                avg_response_time = np.mean(response_times)
                p95_response_time = self.predictive_analytics.statistical_analyzer.calculate_percentile(
                    response_times, 95
                )

                insights = []

                if avg_response_time > 2.0:
                    insights.append(AnalyticsInsight(
                        id=f"perf_slow_response_{timezone.now().isoformat()}",
                        title="Slow Response Times Detected",
                        description=f"Average response time is {avg_response_time:.2f}s, which exceeds optimal threshold",
                        insight_type="performance",
                        confidence_score=0.9,
                        severity="high",
                        recommendations=[
                            "Investigate slow database queries",
                            "Check for resource bottlenecks",
                            "Consider implementing caching strategies",
                            "Monitor server load and performance"
                        ],
                        data_points={
                            "avg_response_time": avg_response_time,
                            "p95_response_time": p95_response_time,
                            "threshold": 2.0,
                            "data_points": len(response_times)
                        },
                        generated_at=timezone.now()
                    ))

                return insights

            return []

        except Exception as e:
            logger.error("Performance analysis error for %s: %s", metric_type, e)
            return []

    async def _analyze_user_behavior_insights(self, metric_type: str,
                                            time_range_hours: int) -> List[AnalyticsInsight]:
        """Analyze user behavior patterns and generate insights."""
        try:
            if metric_type == 'user_actions':
                cutoff = timezone.now() - timedelta(hours=time_range_hours)
                from .models import UserActionTracker

                # Analyze user engagement patterns
                user_activity = UserActionTracker.objects.filter( # pylint: disable=no-member
                    action_timestamp__gte=cutoff
                ).values('user_id').annotate(
                    action_count=Count('id')
                ).order_by('-action_count')[:10]

                if not user_activity:
                    return []

                # Calculate engagement metrics
                total_users = UserActionTracker.objects.filter( # pylint: disable=no-member
                    action_timestamp__gte=cutoff
                ).values('user_id').distinct().count()

                avg_actions_per_user = sum(item['action_count'] for item in user_activity) / total_users if total_users > 0 else 0

                insights = []

                # High engagement insight
                if avg_actions_per_user > 10:
                    insights.append(AnalyticsInsight(
                        id=f"engagement_high_{timezone.now().isoformat()}",
                        title="High User Engagement Detected",
                        description=f"Users are highly engaged with average {avg_actions_per_user:.1f} actions per user",
                        insight_type="engagement",
                        confidence_score=0.85,
                        severity="info",
                        recommendations=[
                            "Leverage high engagement for conversion optimization",
                            "Identify what content/features drive engagement",
                            "Consider implementing loyalty programs"
                        ],
                        data_points={
                            "avg_actions_per_user": avg_actions_per_user,
                            "total_users": total_users,
                            "top_users": len([u for u in user_activity if u['action_count'] > avg_actions_per_user])
                        },
                        generated_at=timezone.now()
                    ))

                return insights

            return []

        except Exception as e:
            logger.error("User behavior analysis error: %s", e)
            return []

    async def detect_anomalies_real_time(self) -> List[AnomalyAlert]:
        """Detect anomalies in real-time data."""
        alerts = []

        try:
            # Define metrics to monitor
            metrics_to_monitor = [
                'response_time',
                'error_rate',
                'page_views',
                'user_actions'
            ]

            for metric_name in metrics_to_monitor:
                # Get current value
                current_value = await self._get_current_metric_value(metric_name)
                if current_value is not None:
                    # Add to anomaly detector
                    self.anomaly_detector.add_data_point(
                        metric_name, current_value, timezone.now()
                    )

                    # Check for anomalies
                    anomaly = self.anomaly_detector.detect_anomaly(
                        metric_name, current_value, timezone.now()
                    )

                    if anomaly:
                        alerts.append(anomaly)

            return alerts

        except Exception as e:
            logger.error("Anomaly detection error: %s", e)
            return []

    async def _get_current_metric_value(self, metric_name: str) -> Optional[float]:
        """Get current value for a specific metric."""
        try:
            if metric_name == 'response_time':
                from .models import PerformanceMetric
                cutoff = timezone.now() - timedelta(minutes=5)
                result = PerformanceMetric.objects.filter( # pylint: disable=no-member
                    metric_type='response_time',
                    timestamp__gte=cutoff
                ).aggregate(Avg('metric_value'))
                return float(result.get('metric_value__avg') or 0.0)

            elif metric_name == 'page_views':
                from .models import UserActionTracker
                cutoff = timezone.now() - timedelta(minutes=5)
                return float(UserActionTracker.objects.filter( # pylint: disable=no-member
                    action_type='page_view',
                    action_timestamp__gte=cutoff
                ).count())

            elif metric_name == 'user_actions':
                from .models import UserActionTracker
                cutoff = timezone.now() - timedelta(minutes=5)
                return float(UserActionTracker.objects.filter( # pylint: disable=no-member
                    action_timestamp__gte=cutoff
                ).count())

            return None

        except Exception as e:
            logger.error("Error getting current metric value for %s: %s", metric_name, e)
            return None

    def get_dashboard_metrics(self, time_range_hours: int = 24) -> Dict[str, Any]:
        """Get metrics for dashboard display."""
        try:
            cutoff = timezone.now() - timedelta(hours=time_range_hours)

            # Basic metrics
            from .models import UserActionTracker, PerformanceMetric, UserSession

            total_users = UserActionTracker.objects.filter( # pylint: disable=no-member
                action_timestamp__gte=cutoff
            ).values('user_id').distinct().count()

            total_actions = UserActionTracker.objects.filter( # pylint: disable=no-member
                action_timestamp__gte=cutoff
            ).count()

            avg_response_time = PerformanceMetric.objects.filter( # pylint: disable=no-member
                metric_type='response_time',
                timestamp__gte=cutoff
            ).aggregate(Avg('metric_value'))['metric_value__avg'] or 0

            active_sessions = UserSession.objects.filter(is_active=True).count() # pylint: disable=no-member

            # Hourly breakdown for charts
            hourly_data = UserActionTracker.objects.filter( # pylint: disable=no-member
                action_timestamp__gte=cutoff
            ).annotate(
                hour=TruncHour('action_timestamp')
            ).values('hour').annotate(
                count=Count('id')
            ).order_by('hour')

            chart_data = [
                {"time": item['hour'].strftime('%H:%M'), "value": item['count']}
                for item in hourly_data
            ]

            return {
                "summary": {
                    "total_users": total_users,
                    "total_actions": total_actions,
                    "avg_response_time": round(float(avg_response_time), 2),
                    "active_sessions": active_sessions
                },
                "chart_data": chart_data,
                "generated_at": timezone.now().isoformat()
            }

        except Exception as e:
            logger.error("Error generating dashboard metrics: %s", e)
            return {"error": str(e)}


# Global analytics engine instance
analytics_engine = AdvancedAnalyticsEngine()


# Convenience functions
async def generate_analytics_insights(metric_types: List[str] = None,
                                     time_range_hours: int = 24) -> List[AnalyticsInsight]:
    """Generate analytics insights."""
    return await analytics_engine.generate_insights(metric_types, time_range_hours)


async def detect_anomalies() -> List[AnomalyAlert]:
    """Detect anomalies in real-time data."""
    return await analytics_engine.detect_anomalies_real_time()


def get_dashboard_data(time_range_hours: int = 24) -> Dict[str, Any]:
    """Get dashboard metrics data."""
    return analytics_engine.get_dashboard_metrics(time_range_hours)


async def predict_user_behavior(user_id: int, days: int = 30) -> Dict[str, Any]:
    """Predict user behavior."""
    return analytics_engine.predictive_analytics.predict_user_behavior(user_id, days)
