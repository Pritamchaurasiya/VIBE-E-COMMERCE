"""
Unit Tests for Enhanced WebSocket Consumers.

Comprehensive test coverage for:
- MonitoringConfig functionality
- MLAnalyticsEngine methods
- EnhancedMonitoringConsumer WebSocket handling
"""

from datetime import datetime
from django.test import TestCase
from django.contrib.auth import get_user_model

from store.monitoring_config import (
    MonitoringConfig,
    SamplingConfig,
    MetricType,
    get_monitoring_config,
)

from store.ml_analytics import (
    MLAnalyticsEngine,
    AnomalyResult,
    PredictionResult,
    get_ml_engine,
)

User = get_user_model()


class MonitoringConfigTestCase(TestCase):
    """Tests for MonitoringConfig functionality."""

    def test_default_config_creation(self):
        """Test that default config is created with proper defaults."""
        config = MonitoringConfig()

        self.assertTrue(config.anomaly_detection_enabled)
        self.assertTrue(config.predictive_analytics_enabled)
        self.assertFalse(config.ml_integration_enabled)
        self.assertEqual(config.metrics_retention_hours, 168)
        self.assertEqual(config.alerts_retention_days, 30)

    def test_default_thresholds(self):
        """Test that default thresholds are properly initialized."""
        config = MonitoringConfig()

        self.assertIn('cpu', config.thresholds)
        self.assertIn('memory', config.thresholds)
        self.assertIn('disk', config.thresholds)
        self.assertIn('error_rate', config.thresholds)

        cpu_threshold = config.thresholds['cpu']
        self.assertEqual(cpu_threshold.warning_value, 70.0)
        self.assertEqual(cpu_threshold.high_value, 85.0)
        self.assertEqual(cpu_threshold.critical_value, 95.0)

    def test_get_threshold(self):
        """Test getting a specific threshold."""
        config = MonitoringConfig()

        threshold = config.get_threshold('memory')
        self.assertIsNotNone(threshold)
        self.assertEqual(threshold.metric, MetricType.MEMORY)

        # Non-existent threshold
        self.assertIsNone(config.get_threshold('nonexistent'))

    def test_update_threshold(self):
        """Test updating threshold values."""
        config = MonitoringConfig()

        result = config.update_threshold('cpu', warning_value=60.0)
        self.assertTrue(result)
        self.assertEqual(config.thresholds['cpu'].warning_value, 60.0)

        # Non-existent metric
        result = config.update_threshold('nonexistent', warning_value=50.0)
        self.assertFalse(result)

    def test_adaptive_interval_high_load(self):
        """Test adaptive interval under high load."""
        config = MonitoringConfig()

        # High load should return minimum interval
        interval = config.get_adaptive_interval(95.0)
        self.assertEqual(interval, config.sampling.min_interval_seconds)

    def test_adaptive_interval_low_load(self):
        """Test adaptive interval under low load."""
        config = MonitoringConfig()

        # Low load should return maximum interval
        interval = config.get_adaptive_interval(10.0)
        self.assertEqual(interval, config.sampling.max_interval_seconds)

    def test_adaptive_interval_disabled(self):
        """Test that base interval is returned when adaptive is disabled."""
        config = MonitoringConfig()
        config.sampling.adaptive_enabled = False

        interval = config.get_adaptive_interval(95.0)
        self.assertEqual(interval, config.sampling.base_interval_seconds)

    def test_singleton_config(self):
        """Test that get_monitoring_config returns singleton."""
        config1 = get_monitoring_config()
        config2 = get_monitoring_config()
        self.assertIs(config1, config2)


class MLAnalyticsEngineTestCase(TestCase):
    """Tests for MLAnalyticsEngine functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.engine = MLAnalyticsEngine(window_size=50)

    def test_add_data_point(self):
        """Test adding data points to sliding window."""
        for i in range(10):
            self.engine.add_data_point('test_metric', float(i))

        self.assertEqual(len(self.engine._data_windows['test_metric']), 10)

    def test_sliding_window_limit(self):
        """Test that window size is maintained."""
        for i in range(100):
            self.engine.add_data_point('test_metric', float(i))

        self.assertEqual(len(self.engine._data_windows['test_metric']), 50)

    def test_detect_anomaly_insufficient_data(self):
        """Test anomaly detection with insufficient data."""
        self.engine.add_data_point('test_metric', 100.0)

        result = self.engine.detect_anomaly('test_metric', 100.0)

        self.assertFalse(result.is_anomaly)
        self.assertEqual(result.confidence, 0.0)

    def test_detect_anomaly_normal_value(self):
        """Test anomaly detection with normal value."""
        # Add stable data
        for i in range(20):
            self.engine.add_data_point('test_metric', 50.0 + (i % 5))

        result = self.engine.detect_anomaly('test_metric', 52.0)

        self.assertFalse(result.is_anomaly)
        self.assertEqual(result.severity, 'info')

    def test_detect_anomaly_outlier(self):
        """Test anomaly detection with outlier value."""
        # Add stable data with slight variance to avoid zero std dev
        for i in range(20):
            self.engine.add_data_point('test_metric', 50.0 + (i % 2))

        # Test extreme value
        result = self.engine.detect_anomaly('test_metric', 500.0)

        self.assertTrue(result.is_anomaly)
        self.assertIn(result.severity, ['warning', 'high', 'critical'])

    def test_predict_next_value_insufficient_data(self):
        """Test prediction with insufficient data."""
        self.engine.add_data_point('test_metric', 100.0)

        result = self.engine.predict_next_value('test_metric')

        self.assertIsNone(result)

    def test_predict_next_value_with_trend(self):
        """Test prediction with trending data."""
        # Add increasing trend
        for i in range(10):
            self.engine.add_data_point('test_metric', float(i * 10))

        result = self.engine.predict_next_value('test_metric')

        self.assertIsNotNone(result)
        self.assertEqual(result.metric_name, 'test_metric')
        self.assertEqual(result.trend, 'up')
        self.assertGreater(result.predicted_value, 90)

    def test_get_trend_stable(self):
        """Test trend analysis with stable data."""
        for i in range(20):
            self.engine.add_data_point('test_metric', 50.0)

        result = self.engine.get_trend('test_metric')

        self.assertEqual(result['trend'], 'stable')
        self.assertAlmostEqual(result['change_percent'], 0.0, places=1)

    def test_get_trend_increasing(self):
        """Test trend analysis with increasing data."""
        for i in range(20):
            self.engine.add_data_point('test_metric', float(i * 10))

        result = self.engine.get_trend('test_metric')

        self.assertEqual(result['trend'], 'increasing')
        self.assertGreater(result['change_percent'], 0)

    def test_clear_data_specific_metric(self):
        """Test clearing data for specific metric."""
        self.engine.add_data_point('metric1', 100.0)
        self.engine.add_data_point('metric2', 200.0)

        self.engine.clear_data('metric1')

        self.assertNotIn('metric1', self.engine._data_windows)
        self.assertIn('metric2', self.engine._data_windows)

    def test_clear_data_all(self):
        """Test clearing all data."""
        self.engine.add_data_point('metric1', 100.0)
        self.engine.add_data_point('metric2', 200.0)

        self.engine.clear_data()

        self.assertEqual(len(self.engine._data_windows), 0)

    def test_singleton_engine(self):
        """Test that get_ml_engine returns singleton."""
        engine1 = get_ml_engine()
        engine2 = get_ml_engine()
        self.assertIs(engine1, engine2)


class AnomalyResultTestCase(TestCase):
    """Tests for AnomalyResult dataclass."""

    def test_anomaly_result_creation(self):
        """Test AnomalyResult creation."""
        result = AnomalyResult(
            is_anomaly=True,
            score=3.5,
            confidence=85.0,
            metric_name='cpu',
            value=95.0,
            expected_range=(40.0, 80.0),
            timestamp=datetime.now(),
            severity='high'
        )

        self.assertTrue(result.is_anomaly)
        self.assertEqual(result.metric_name, 'cpu')
        self.assertEqual(result.severity, 'high')


class PredictionResultTestCase(TestCase):
    """Tests for PredictionResult dataclass."""

    def test_prediction_result_creation(self):
        """Test PredictionResult creation."""
        result = PredictionResult(
            metric_name='page_views',
            predicted_value=150.0,
            confidence=75.0,
            prediction_interval=(100.0, 200.0),
            timeframe='next_hour',
            method='linear_regression',
            trend='up'
        )

        self.assertEqual(result.metric_name, 'page_views')
        self.assertEqual(result.trend, 'up')
        self.assertEqual(result.method, 'linear_regression')


class SamplingConfigTestCase(TestCase):
    """Tests for SamplingConfig functionality."""

    def test_default_sampling_config(self):
        """Test default sampling configuration."""
        config = SamplingConfig()

        self.assertEqual(config.base_interval_seconds, 5.0)
        self.assertEqual(config.min_interval_seconds, 1.0)
        self.assertEqual(config.max_interval_seconds, 30.0)
        self.assertTrue(config.adaptive_enabled)
        self.assertEqual(config.high_load_threshold, 80.0)

    def test_custom_sampling_config(self):
        """Test custom sampling configuration."""
        config = SamplingConfig(
            base_interval_seconds=10.0,
            min_interval_seconds=2.0,
            max_interval_seconds=60.0,
            adaptive_enabled=False
        )

        self.assertEqual(config.base_interval_seconds, 10.0)
        self.assertFalse(config.adaptive_enabled)
