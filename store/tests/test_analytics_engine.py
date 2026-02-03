from django.test import TestCase
from store.ml_analytics import MLAnalyticsEngine
from datetime import datetime

class MLAnalyticsEngineTest(TestCase):
    def setUp(self):
        self.engine = MLAnalyticsEngine(window_size=20)

    def test_anomaly_detection_zscore(self):
        # Add normal data
        for i in range(10):
            self.engine.add_data_point('test_metric', 10.0)

        # Add a slightly deviant point
        self.engine.add_data_point('test_metric', 10.5)

        # Detect anomaly on a massive outlier
        result = self.engine.detect_anomaly('test_metric', 100.0)
        self.assertTrue(result.is_anomaly)
        self.assertEqual(result.metric_name, 'test_metric')
        self.assertEqual(result.severity, 'critical')

    def test_prediction_linear(self):
        # Add linear trend data: 1, 2, 3, 4, 5...
        for i in range(10):
            self.engine.add_data_point('trend_metric', float(i))

        # Predict next value (should be 10)
        prediction = self.engine.predict_next_value('trend_metric')

        self.assertIsNotNone(prediction)
        self.assertEqual(prediction.metric_name, 'trend_metric')
        # Prediction might not be exactly 10.0 due to float math, but close
        self.assertAlmostEqual(prediction.predicted_value, 10.0, delta=0.5)
        self.assertEqual(prediction.trend, 'up')

    def test_trend_analysis(self):
         # Stable trend
        for i in range(10):
            self.engine.add_data_point('stable_metric', 10.0)

        trend = self.engine.get_trend('stable_metric')
        self.assertEqual(trend['trend'], 'stable')

        # Increasing trend
        for i in range(10):
            self.engine.add_data_point('growth_metric', float(i))

        trend = self.engine.get_trend('growth_metric')
        # Logic in ml_analytics.py: if change > 5%, it's increasing
        # 0,1,2,3,4 (avg 2) -> 5,6,7,8,9 (avg 7) -> change is huge
        self.assertEqual(trend['trend'], 'increasing')
