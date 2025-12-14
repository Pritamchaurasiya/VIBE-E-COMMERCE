"""
Monitoring Configuration Module

Provides customizable alert thresholds, sampling rates, and configuration
for the enhanced monitoring system.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    HIGH = "high"
    CRITICAL = "critical"


class MetricType(Enum):
    """Types of metrics tracked."""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    DATABASE = "database"
    ERROR_RATE = "error_rate"
    RESPONSE_TIME = "response_time"
    PAGE_VIEWS = "page_views"
    CONVERSIONS = "conversions"


@dataclass
class AlertThreshold:
    """Configurable alert threshold."""
    metric: MetricType
    warning_value: float
    high_value: float
    critical_value: float
    enabled: bool = True
    cooldown_minutes: int = 5  # Prevent alert spam


@dataclass
class SamplingConfig:
    """Adaptive sampling configuration."""
    base_interval_seconds: float = 5.0
    min_interval_seconds: float = 1.0
    max_interval_seconds: float = 30.0
    adaptive_enabled: bool = True
    high_load_threshold: float = 80.0  # CPU/Memory %


@dataclass
class MonitoringConfig:
    """Main monitoring configuration."""
    # Alert thresholds
    thresholds: Dict[str, AlertThreshold] = field(default_factory=dict)

    # Sampling configuration
    sampling: SamplingConfig = field(default_factory=SamplingConfig)

    # Feature flags
    anomaly_detection_enabled: bool = True
    predictive_analytics_enabled: bool = True
    ml_integration_enabled: bool = False

    # Data retention
    metrics_retention_hours: int = 168  # 7 days
    alerts_retention_days: int = 30

    # Performance settings
    max_clients_per_group: int = 100
    batch_size: int = 50
    cache_ttl_seconds: int = 60

    def __post_init__(self):
        """Initialize default thresholds if not provided."""
        if not self.thresholds:
            self.thresholds = self._get_default_thresholds()

    def _get_default_thresholds(self) -> Dict[str, AlertThreshold]:
        """Get default alert thresholds."""
        return {
            'cpu': AlertThreshold(
                metric=MetricType.CPU,
                warning_value=70.0,
                high_value=85.0,
                critical_value=95.0
            ),
            'memory': AlertThreshold(
                metric=MetricType.MEMORY,
                warning_value=75.0,
                high_value=85.0,
                critical_value=95.0
            ),
            'disk': AlertThreshold(
                metric=MetricType.DISK,
                warning_value=80.0,
                high_value=90.0,
                critical_value=95.0
            ),
            'error_rate': AlertThreshold(
                metric=MetricType.ERROR_RATE,
                warning_value=5.0,
                high_value=10.0,
                critical_value=20.0
            ),
            'response_time': AlertThreshold(
                metric=MetricType.RESPONSE_TIME,
                warning_value=500.0,  # ms
                high_value=1000.0,
                critical_value=3000.0
            ),
        }

    def get_threshold(self, metric_name: str) -> Optional[AlertThreshold]:
        """Get threshold for a specific metric."""
        return self.thresholds.get(metric_name)

    def update_threshold(self, metric_name: str, **kwargs) -> bool:
        """Update threshold values for a metric."""
        if metric_name not in self.thresholds:
            logger.warning("Unknown metric: %s", metric_name)
            return False

        threshold = self.thresholds[metric_name]
        for key, value in kwargs.items():
            if hasattr(threshold, key):
                setattr(threshold, key, value)
        return True

    def get_adaptive_interval(self, current_load: float) -> float:
        """Calculate adaptive sampling interval based on system load."""
        if not self.sampling.adaptive_enabled:
            return self.sampling.base_interval_seconds

        if current_load >= self.sampling.high_load_threshold:
            # More frequent sampling under high load
            return self.sampling.min_interval_seconds
        elif current_load < 30.0:
            # Less frequent sampling under low load
            return self.sampling.max_interval_seconds
        else:
            # Linear interpolation
            load_ratio = (current_load - 30.0) / (self.sampling.high_load_threshold - 30.0)
            interval_range = self.sampling.base_interval_seconds - self.sampling.min_interval_seconds
            return self.sampling.base_interval_seconds - (load_ratio * interval_range)


# Singleton configuration instance
_config_instance: Optional[MonitoringConfig] = None


def get_monitoring_config() -> MonitoringConfig:
    """Get the global monitoring configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = MonitoringConfig()
    return _config_instance


def update_monitoring_config(**kwargs) -> MonitoringConfig:
    """Update the global monitoring configuration."""
    global _config_instance
    config = get_monitoring_config()
    for key, value in kwargs.items():
        if hasattr(config, key):
            setattr(config, key, value)
    return config
