"""
ML Analytics Module

Provides machine learning-based analytics including:
- Isolation Forest for anomaly detection
- Time series forecasting
- Pattern recognition
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class AnomalyResult:
    """Result of anomaly detection."""
    is_anomaly: bool
    score: float
    confidence: float
    metric_name: str
    value: float
    expected_range: Tuple[float, float]
    timestamp: datetime
    severity: str


@dataclass
class PredictionResult:
    """Result of predictive analytics."""
    metric_name: str
    predicted_value: float
    confidence: float
    prediction_interval: Tuple[float, float]
    timeframe: str
    method: str
    trend: str  # 'up', 'down', 'stable'


class MLAnalyticsEngine:
    """
    Machine learning analytics engine for monitoring.

    Provides anomaly detection using statistical methods (with optional
    scikit-learn integration) and time series forecasting.
    """

    def __init__(self, window_size: int = 100):
        """
        Initialize the ML analytics engine.

        Args:
            window_size: Number of data points to keep in sliding window
        """
        self.window_size = window_size
        self._data_windows: Dict[str, List[float]] = {}
        self._sklearn_available = self._check_sklearn()
        self._isolation_forests: Dict[str, Any] = {}

    def _check_sklearn(self) -> bool:
        """Check if scikit-learn is available."""
        import importlib.util
        if importlib.util.find_spec('sklearn') is not None:
            return True
        logger.info("scikit-learn not available, using statistical methods")
        return False

    def add_data_point(self, metric_name: str, value: float) -> None:
        """
        Add a data point to the sliding window.

        Args:
            metric_name: Name of the metric
            value: Metric value
        """
        if metric_name not in self._data_windows:
            self._data_windows[metric_name] = []

        window = self._data_windows[metric_name]
        window.append(value)

        # Maintain window size
        if len(window) > self.window_size:
            window.pop(0)

    def detect_anomaly(
        self,
        metric_name: str,
        value: float,
        z_threshold: float = 3.0
    ) -> AnomalyResult:
        """
        Detect if a value is an anomaly using statistical or ML methods.

        Args:
            metric_name: Name of the metric
            value: Current value to check
            z_threshold: Z-score threshold for anomaly detection

        Returns:
            AnomalyResult with detection details
        """
        window = self._data_windows.get(metric_name, [])
        now = datetime.now()

        # Need minimum data points
        if len(window) < 10:
            return AnomalyResult(
                is_anomaly=False,
                score=0.0,
                confidence=0.0,
                metric_name=metric_name,
                value=value,
                expected_range=(0, 0),
                timestamp=now,
                severity='info'
            )

        # Use Isolation Forest if sklearn available and enough data
        if self._sklearn_available and len(window) >= 50:
            return self._detect_with_isolation_forest(metric_name, value, window, now)

        # Fall back to statistical method
        return self._detect_with_zscore(metric_name, value, window, z_threshold, now)

    def _detect_with_zscore(
        self,
        metric_name: str,
        value: float,
        window: List[float],
        z_threshold: float,
        timestamp: datetime
    ) -> AnomalyResult:
        """Detect anomalies using Z-score method."""
        arr = np.array(window)
        mean = np.mean(arr)
        std = np.std(arr)

        if std == 0:
            z_score = 0.0
        else:
            z_score = abs((value - mean) / std)

        is_anomaly = z_score > z_threshold
        confidence = min(100.0, (z_score / z_threshold) * 100) if z_threshold > 0 else 0

        # Determine severity
        if z_score > z_threshold * 2:
            severity = 'critical'
        elif z_score > z_threshold * 1.5:
            severity = 'high'
        elif z_score > z_threshold:
            severity = 'warning'
        else:
            severity = 'info'

        expected_low = max(0, mean - (2 * std))
        expected_high = mean + (2 * std)

        return AnomalyResult(
            is_anomaly=is_anomaly,
            score=z_score,
            confidence=round(confidence, 1),
            metric_name=metric_name,
            value=value,
            expected_range=(round(expected_low, 2), round(expected_high, 2)),
            timestamp=timestamp,
            severity=severity
        )

    def _detect_with_isolation_forest(
        self,
        metric_name: str,
        value: float,
        window: List[float],
        timestamp: datetime
    ) -> AnomalyResult:
        """Detect anomalies using Isolation Forest."""
        try:
            from sklearn.ensemble import IsolationForest

            # Get or create isolation forest for this metric
            if metric_name not in self._isolation_forests:
                self._isolation_forests[metric_name] = IsolationForest(
                    contamination=0.1,
                    random_state=42,
                    n_estimators=100
                )

            model = self._isolation_forests[metric_name]

            # Fit on window data
            X = np.array(window).reshape(-1, 1)
            model.fit(X)

            # Predict for current value
            prediction = model.predict([[value]])[0]
            score = model.decision_function([[value]])[0]

            is_anomaly = prediction == -1

            # Calculate expected range from window
            arr = np.array(window)
            mean = np.mean(arr)
            std = np.std(arr)

            # Convert score to confidence
            confidence = min(100.0, abs(score) * 100)

            if is_anomaly:
                if score < -0.5:
                    severity = 'critical'
                elif score < -0.3:
                    severity = 'high'
                else:
                    severity = 'warning'
            else:
                severity = 'info'

            return AnomalyResult(
                is_anomaly=is_anomaly,
                score=abs(score),
                confidence=round(confidence, 1),
                metric_name=metric_name,
                value=value,
                expected_range=(round(mean - 2*std, 2), round(mean + 2*std, 2)),
                timestamp=timestamp,
                severity=severity
            )

        except Exception as e:
            logger.error("Isolation Forest detection failed: %s", e)
            return self._detect_with_zscore(metric_name, value, window, 3.0, timestamp)

    def predict_next_value(
        self,
        metric_name: str,
        forecast_periods: int = 1
    ) -> Optional[PredictionResult]:
        """
        Predict future values using linear regression.

        Args:
            metric_name: Name of the metric
            forecast_periods: Number of periods to forecast

        Returns:
            PredictionResult or None if insufficient data
        """
        window = self._data_windows.get(metric_name, [])

        if len(window) < 5:
            return None

        try:
            arr = np.array(window)
            x = np.arange(len(arr))

            # Linear regression
            x_mean = np.mean(x)
            y_mean = np.mean(arr)

            numerator = np.sum((x - x_mean) * (arr - y_mean))
            denominator = np.sum((x - x_mean) ** 2)

            if denominator == 0:
                slope = 0
            else:
                slope = numerator / denominator

            intercept = y_mean - slope * x_mean

            # Predict next value(s)
            next_x = len(arr) + forecast_periods - 1
            predicted_value = slope * next_x + intercept
            predicted_value = max(0, predicted_value)  # Non-negative

            # Calculate confidence based on R-squared
            y_pred = slope * x + intercept
            ss_res = np.sum((arr - y_pred) ** 2)
            ss_tot = np.sum((arr - y_mean) ** 2)

            if ss_tot > 0:
                r_squared = 1 - (ss_res / ss_tot)
                confidence = max(0, min(100, r_squared * 100))
            else:
                confidence = 50.0

            # Prediction interval
            std = np.std(arr)
            interval = (
                round(max(0, predicted_value - 2 * std), 2),
                round(predicted_value + 2 * std, 2)
            )

            # Determine trend
            if slope > 0.1:
                trend = 'up'
            elif slope < -0.1:
                trend = 'down'
            else:
                trend = 'stable'

            return PredictionResult(
                metric_name=metric_name,
                predicted_value=round(predicted_value, 2),
                confidence=round(confidence, 1),
                prediction_interval=interval,
                timeframe=f'next_{forecast_periods}_periods',
                method='linear_regression',
                trend=trend
            )

        except Exception as e:
            logger.error("Prediction failed for %s: %s", metric_name, e)
            return None

    def get_trend(self, metric_name: str) -> Dict[str, Any]:
        """
        Analyze trend for a metric.

        Returns:
            Dictionary with trend analysis
        """
        window = self._data_windows.get(metric_name, [])

        if len(window) < 3:
            return {'trend': 'unknown', 'change_percent': 0, 'volatility': 0}

        arr = np.array(window)

        # Calculate change
        first_half = np.mean(arr[:len(arr)//2])
        second_half = np.mean(arr[len(arr)//2:])

        if first_half > 0:
            change_percent = ((second_half - first_half) / first_half) * 100
        else:
            change_percent = 0

        # Volatility (coefficient of variation)
        mean = np.mean(arr)
        if mean > 0:
            volatility = (np.std(arr) / mean) * 100
        else:
            volatility = 0

        # Determine trend direction
        if change_percent > 5:
            trend = 'increasing'
        elif change_percent < -5:
            trend = 'decreasing'
        else:
            trend = 'stable'

        return {
            'trend': trend,
            'change_percent': round(change_percent, 1),
            'volatility': round(volatility, 1),
            'current_avg': round(np.mean(arr[-10:]) if len(arr) >= 10 else mean, 2),
            'data_points': len(window)
        }

    def clear_data(self, metric_name: Optional[str] = None) -> None:
        """Clear data windows."""
        if metric_name:
            self._data_windows.pop(metric_name, None)
            self._isolation_forests.pop(metric_name, None)
        else:
            self._data_windows.clear()
            self._isolation_forests.clear()


# Global instance
_ml_engine: Optional[MLAnalyticsEngine] = None


def get_ml_engine() -> MLAnalyticsEngine:
    """Get the global ML analytics engine instance."""
    global _ml_engine
    if _ml_engine is None:
        _ml_engine = MLAnalyticsEngine()
    return _ml_engine
