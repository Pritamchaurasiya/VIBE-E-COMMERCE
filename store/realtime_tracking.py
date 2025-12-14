"""
Real-Time Tracking and Performance Optimization System

This module provides enterprise-grade real-time tracking with:
- High-performance async processing
- Intelligent caching strategies
- Real-time data streaming
- Performance optimization
- Circuit breaker patterns
- Memory-efficient batch processing

Author: VIBE E-Commerce Enhancement Team
Version: 3.0.0
Last Updated: 2025-12-13
"""

# pylint: disable=no-member

import asyncio
import time
import logging
import threading
from collections import deque, defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from concurrent.futures import ThreadPoolExecutor

from django.core.cache import cache
from django.utils import timezone
from django.db import models

logger = logging.getLogger(__name__)


class ProcessingPriority(Enum):
    """Priority levels for tracking operations."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BATCH = 5


class CircuitBreakerState(Enum):
    """Circuit breaker states for system protection."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Blocking requests
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreakerError(Exception):
    """Exception raised when circuit breaker is open."""


@dataclass
class TrackingEvent:
    """Standardized tracking event structure."""
    event_type: str
    timestamp: datetime
    data: Dict[str, Any]
    priority: ProcessingPriority = ProcessingPriority.NORMAL
    session_id: Optional[str] = None
    user_id: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class PerformanceMetrics:
    """Real-time performance metrics."""
    timestamp: datetime
    cpu_usage: float
    memory_usage: float
    request_count: int
    response_time_avg: float
    error_rate: float
    throughput: float
    cache_hit_rate: float
    active_connections: int


class CircuitBreaker:
    """Circuit breaker for fault tolerance."""

    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED

    def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == CircuitBreakerState.OPEN:
            if time.time() - self.last_failure_time >= self.timeout:
                self.state = CircuitBreakerState.HALF_OPEN
            else:
                raise CircuitBreakerError("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
            if self.state == CircuitBreakerState.HALF_OPEN:
                self.state = CircuitBreakerState.CLOSED
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = CircuitBreakerState.OPEN

            raise e


class CacheManager:
    """Advanced caching manager with intelligent strategies."""

    def __init__(self):
        self.local_cache = {}
        self.cache_stats = defaultdict(int)
        self._lock = threading.RLock()

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache with stats tracking."""
        with self._lock:
            try:
                # Try local cache first (fastest)
                if key in self.local_cache:
                    self.cache_stats['local_hits'] += 1
                    return self.local_cache[key]

                # Try Django cache
                value = cache.get(key)
                if value is not None:
                    self.cache_stats['django_hits'] += 1
                    # Promote to local cache
                    self.local_cache[key] = value
                    return value

                self.cache_stats['misses'] += 1
                return None

            except Exception as e:
                logger.error("Cache get error for key %s: %s", key, e)
                self.cache_stats['errors'] += 1
                return None

    def set(self, key: str, value: Any, timeout: int = 300) -> bool:
        """Set value in cache with timeout."""
        with self._lock:
            try:
                # Set in local cache
                self.local_cache[key] = value

                # Set in Django cache
                cache.set(key, value, timeout)
                self.cache_stats['sets'] += 1
                return True

            except Exception as e:
                logger.error("Cache set error for key %s: %s", key, e)
                self.cache_stats['errors'] += 1
                return False

    def delete(self, key: str) -> bool:
        """Delete key from all caches."""
        with self._lock:
            try:
                self.local_cache.pop(key, None)
                cache.delete(key)
                self.cache_stats['deletes'] += 1
                return True

            except Exception as e:
                logger.error("Cache delete error for key %s: %s", key, e)
                return False

    def get_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        with self._lock:
            return dict(self.cache_stats)


class AsyncBatchProcessor:
    """High-performance async batch processor."""

    def __init__(self, batch_size: int = 1000, flush_interval: float = 1.0):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.batch_queue = asyncio.Queue()
        self.processing_queue = []
        self.last_flush = time.time()
        self.is_running = False
        self._tasks = []

    async def start(self):
        """Start the batch processor."""
        self.is_running = True
        self._tasks = [
            asyncio.create_task(self._batch_processor()),
            asyncio.create_task(self._auto_flusher())
        ]

    async def stop(self):
        """Stop the batch processor."""
        self.is_running = False
        # Flush remaining items
        await self._flush_batch()
        # Cancel tasks
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)

    async def add_event(self, event: TrackingEvent):
        """Add tracking event to batch queue."""
        await self.batch_queue.put(event)

    async def _batch_processor(self):
        """Process batches of tracking events."""
        while self.is_running:
            try:
                # Collect batch of events
                batch = []
                try:
                    # Get first event with timeout
                    event = await asyncio.wait_for(self.batch_queue.get(), timeout=0.1)
                    batch.append(event)

                    # Collect more events up to batch size
                    while len(batch) < self.batch_size:
                        try:
                            # get_nowait does not accept a timeout argument
                            event = self.batch_queue.get_nowait()
                            batch.append(event)
                        except asyncio.QueueEmpty:
                            break

                except asyncio.TimeoutError:
                    continue

                if batch:
                    await self._process_batch(batch)

            except Exception as e:
                logger.error(f"Batch processor error: {e}")
                await asyncio.sleep(0.1)

    async def _auto_flusher(self):
        """Auto-flush batches based on time interval."""
        while self.is_running:
            try:
                await asyncio.sleep(self.flush_interval)
                if time.time() - self.last_flush >= self.flush_interval:
                    await self._flush_batch()
            except Exception as e:
                logger.error(f"Auto flusher error: {e}")

    async def _flush_batch(self):
        """Force flush current batch."""
        try:
            # Collect all pending events
            batch = []
            while not self.batch_queue.empty():
                try:
                    event = self.batch_queue.get_nowait()
                    batch.append(event)
                except asyncio.QueueEmpty:
                    break

            if batch:
                await self._process_batch(batch)
                self.last_flush = time.time()

        except Exception as e:
            logger.error(f"Flush batch error: {e}")

    async def _process_batch(self, batch: List[TrackingEvent]):
        """Process a batch of tracking events."""
        try:
            # Sort by priority
            batch.sort(key=lambda x: x.priority.value)

            # Process events in parallel
            tasks = []
            for event in batch:
                if event.priority == ProcessingPriority.CRITICAL:
                    # Process critical events immediately
                    task = asyncio.create_task(self._process_single_event(event))
                    tasks.append(task)
                else:
                    # Add to processing queue for batch processing
                    self.processing_queue.append(event)

            # Wait for critical events
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)

            # Process remaining queue
            if self.processing_queue:
                await self._process_queued_events()

        except Exception as e:
            logger.error(f"Batch processing error: {e}")

    async def _process_single_event(self, event: TrackingEvent):
        """Process a single tracking event."""
        try:
            # Store in database
            await self._store_event(event)

            # Trigger real-time notifications
            await self._notify_subscribers(event)

        except Exception as e:
            logger.error(f"Single event processing error: {e}")
            if event.retry_count < event.max_retries:
                event.retry_count += 1
                await self.add_event(event)

    async def _process_queued_events(self):
        """Process queued events efficiently."""
        if not self.processing_queue:
            return

        try:
            # Group events by type for efficient processing
            grouped = defaultdict(list)
            for event in self.processing_queue:
                grouped[event.event_type].append(event)

            # Process each group
            tasks = []
            for event_type, events in grouped.items():
                task = asyncio.create_task(self._process_event_group(event_type, events))
                tasks.append(task)

            await asyncio.gather(*tasks, return_exceptions=True)
            self.processing_queue.clear()

        except Exception as e:
            logger.error(f"Queued events processing error: {e}")

    async def _process_event_group(self, event_type: str, events: List[TrackingEvent]):
        """Process a group of events of the same type."""
        try:
            # Store all events in database
            await self._store_event_batch(event_type, events)

            # Generate aggregated analytics
            await self._generate_analytics(event_type, events)

        except Exception as e:
            logger.error(f"Event group processing error for {event_type}: {e}")

    async def _store_event(self, event: TrackingEvent):
        """Store a single tracking event."""
        from .tracking_service import EnhancedTrackingService

        try:
            # Map event types to tracking service methods
            event_mapping = {
                'page_view': lambda: EnhancedTrackingService.track_user_action(
                    action_type='page_view',
                    user_id=event.user_id,
                    session_id=event.session_id,
                    metadata=event.data
                ),
                'user_action': lambda: EnhancedTrackingService.track_user_action(
                    action_type=event.data.get('action_type', 'custom_action'),
                    user_id=event.user_id,
                    session_id=event.session_id,
                    metadata=event.data
                ),
                'system_access': lambda: EnhancedTrackingService.track_system_access(
                    access_type=event.data.get('access_type', 'page_access'),
                    user_id=event.user_id,
                    metadata=event.data
                ),
                'performance': lambda: EnhancedTrackingService.record_performance_metric(
                    metric_type=event.data.get('metric_type', 'custom'),
                    metric_value=event.data.get('value', 0),
                    metric_unit=event.data.get('unit', 'count'),
                    metadata=event.metadata
                )
            }

            if event.event_type in event_mapping:
                event_mapping[event.event_type]()

        except Exception as e:
            logger.error(f"Error storing event {event.event_type}: {e}")
            raise

    async def _store_event_batch(self, event_type: str, events: List[TrackingEvent]):
        """Store multiple events efficiently."""
        # Implementation would depend on the database backend
        # For now, process each event
        for event in events:
            await self._store_event(event)

    async def _notify_subscribers(self, event: TrackingEvent):
        """Notify subscribers about real-time events."""
        # Implementation for WebSocket or SSE notifications
        pass

    async def _generate_analytics(self, event_type: str, events: List[TrackingEvent]):
        """Generate analytics for event group."""
        # Generate real-time analytics
        pass


class RealTimeMetricsCollector:
    """Collects and processes real-time system metrics."""

    def __init__(self):
        self.metrics_buffer = deque(maxlen=10000)
        self.is_collecting = False
        self._collection_task = None
        self._lock = threading.Lock()

    async def start_collection(self, interval: float = 1.0):
        """Start metrics collection."""
        self.is_collecting = True
        self._collection_task = asyncio.create_task(
            self._collect_metrics_loop(interval)
        )

    async def stop_collection(self):
        """Stop metrics collection."""
        self.is_collecting = False
        if self._collection_task:
            self._collection_task.cancel()
            await asyncio.gather(self._collection_task, return_exceptions=True)

    async def _collect_metrics_loop(self, interval: float):
        """Main metrics collection loop."""
        while self.is_collecting:
            try:
                metrics = await self._collect_system_metrics()
                with self._lock:
                    self.metrics_buffer.append(metrics)

                await asyncio.sleep(interval)

            except Exception as e:
                logger.error("Metrics collection error: %s", e)
                await asyncio.sleep(interval)

    async def _collect_system_metrics(self) -> PerformanceMetrics:
        """Collect current system metrics."""
        try:
            import psutil

            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()

            # Get application metrics
            active_sessions = await self._get_active_sessions()
            avg_response_time = await self._get_average_response_time()
            error_rate = await self._get_error_rate()
            throughput = await self._get_throughput()
            cache_hit_rate = await self._get_cache_hit_rate()

            return PerformanceMetrics(
                timestamp=timezone.now(),
                cpu_usage=cpu_percent,
                memory_usage=memory.percent,
                request_count=await self._get_request_count(),
                response_time_avg=avg_response_time,
                error_rate=error_rate,
                throughput=throughput,
                cache_hit_rate=cache_hit_rate,
                active_connections=active_sessions
            )

        except ImportError:
            # Fallback if psutil not available
            return PerformanceMetrics(
                timestamp=timezone.now(),
                cpu_usage=0.0,
                memory_usage=0.0,
                request_count=0,
                response_time_avg=0.0,
                error_rate=0.0,
                throughput=0.0,
                cache_hit_rate=0.0,
                active_connections=0
            )
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
            raise

    async def _get_active_sessions(self) -> int:
        """Get number of active user sessions."""
        from .models import UserSession
        try:
            # pylint: disable=no-member
            return UserSession.objects.filter(is_active=True).count()
        except Exception as e:
            logger.warning(f"Error getting active sessions: {e}")
            return 0

    async def _get_average_response_time(self) -> float:
        """Get average response time from recent requests."""
        from .models import PerformanceMetric
        try:
            cutoff = timezone.now() - timedelta(minutes=5)
            # pylint: disable=no-member
            result = PerformanceMetric.objects.filter(
                timestamp__gte=cutoff,
                metric_type='response_time'
            ).aggregate(models.Avg('metric_value'))
            return float(result.get('metric_value__avg') or 0.0)
        except Exception as e:
            logger.warning(f"Error getting avg response time: {e}")
            return 0.0

    async def _get_error_rate(self) -> float:
        """Get current error rate."""
        try:
            # cutoff = timezone.now() - timedelta(minutes=5)
            # This would need to be implemented based on your logging system
            # For now, return a placeholder
            return 0.0

        except Exception as e:
            logger.warning(f"Error getting error rate: {e}")
            return 0.0

    async def _get_throughput(self) -> float:
        """Get current system throughput (requests per second)."""
        try:
            cutoff = timezone.now() - timedelta(minutes=1)
            from .models import UserActionTracker
            # pylint: disable=no-member
            count = UserActionTracker.objects.filter(
                action_timestamp__gte=cutoff
            ).count()
            return float(count / 60.0)  # requests per second
        except Exception as e:
            logger.warning(f"Error getting throughput: {e}")
            return 0.0

    async def _get_cache_hit_rate(self) -> float:
        """Get cache hit rate percentage."""
        try:
            cache_stats = cache_manager.get_stats()
            total_requests = sum([
                cache_stats.get('local_hits', 0),
                cache_stats.get('django_hits', 0),
                cache_stats.get('misses', 0)
            ])

            if total_requests > 0:
                hits = cache_stats.get('local_hits', 0) + cache_stats.get('django_hits', 0)
                return (hits / total_requests) * 100.0
            return 0.0
        except Exception as e:
            logger.warning(f"Error getting cache hit rate: {e}")
            return 0.0

    async def _get_request_count(self) -> int:
        """Get recent request count."""
        try:
            cutoff = timezone.now() - timedelta(minutes=1)
            from .models import UserActionTracker
            # pylint: disable=no-member
            return UserActionTracker.objects.filter(
                action_timestamp__gte=cutoff
            ).count()
        except Exception as e:
            logger.warning(f"Error getting request count: {e}")
            return 0

    def get_latest_metrics(self) -> Optional[PerformanceMetrics]:
        """Get the most recent metrics."""
        with self._lock:
            return self.metrics_buffer[-1] if self.metrics_buffer else None

    def get_metrics_history(self, minutes: int = 5) -> List[PerformanceMetrics]:
        """Get metrics history for specified duration."""
        with self._lock:
            cutoff = timezone.now() - timedelta(minutes=minutes)
            return [
                m for m in self.metrics_buffer
                if m.timestamp >= cutoff
            ]


# Global instances
cache_manager = CacheManager()
batch_processor = AsyncBatchProcessor()
metrics_collector = RealTimeMetricsCollector()

# Circuit breakers for external services
db_circuit_breaker = CircuitBreaker(failure_threshold=10, timeout=30)
redis_circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60)


class RealTimeTrackingService:
    """Main real-time tracking service."""

    def __init__(self):
        self.is_initialized = False
        self._executor = ThreadPoolExecutor(max_workers=10)

    async def initialize(self):
        """Initialize the real-time tracking system."""
        if self.is_initialized:
            return

        try:
            # Start batch processor
            await batch_processor.start()

            # Start metrics collection
            await metrics_collector.start_collection(interval=1.0)

            self.is_initialized = True
            logger.info("Real-time tracking system initialized successfully")

        except Exception as e:
            logger.error("Failed to initialize real-time tracking: %s", e)
            raise

    async def shutdown(self):
        """Shutdown the real-time tracking system."""
        try:
            await batch_processor.stop()
            await metrics_collector.stop_collection()
            self._executor.shutdown(wait=True)
            self.is_initialized = False
            logger.info("Real-time tracking system shutdown completed")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

    async def track_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        user_id: Optional[int] = None,
        session_id: Optional[str] = None,
        priority: ProcessingPriority = ProcessingPriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Track a real-time event."""
        try:
            if not self.is_initialized:
                await self.initialize()

            event = TrackingEvent(
                event_type=event_type,
                timestamp=timezone.now(),
                data=data,
                priority=priority,
                session_id=session_id,
                user_id=user_id,
                metadata=metadata or {}
            )

            await batch_processor.add_event(event)
            return True

        except Exception as e:
            logger.error("Error tracking event %s: %s", event_type, e)
            return False

    def get_performance_metrics(self) -> Optional[PerformanceMetrics]:
        """Get current performance metrics."""
        return metrics_collector.get_latest_metrics()

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return cache_manager.get_stats()

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status."""
        metrics = self.get_performance_metrics()

        health_status = {
            'overall_status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'components': {}
        }

        if metrics:
            # Check CPU usage
            if metrics.cpu_usage > 90:
                health_status['components']['cpu'] = 'critical'
                health_status['overall_status'] = 'critical'
            elif metrics.cpu_usage > 75:
                health_status['components']['cpu'] = 'warning'
                if health_status['overall_status'] == 'healthy':
                    health_status['overall_status'] = 'warning'

            # Check memory usage
            if metrics.memory_usage > 90:
                health_status['components']['memory'] = 'critical'
                health_status['overall_status'] = 'critical'
            elif metrics.memory_usage > 80:
                health_status['components']['memory'] = 'warning'
                if health_status['overall_status'] == 'healthy':
                    health_status['overall_status'] = 'warning'

            # Check error rate
            if metrics.error_rate > 10:
                health_status['components']['errors'] = 'critical'
                health_status['overall_status'] = 'critical'
            elif metrics.error_rate > 5:
                health_status['components']['errors'] = 'warning'
                if health_status['overall_status'] == 'healthy':
                    health_status['overall_status'] = 'warning'

            health_status['metrics'] = {
                'cpu_usage': metrics.cpu_usage,
                'memory_usage': metrics.memory_usage,
                'response_time': metrics.response_time_avg,
                'error_rate': metrics.error_rate,
                'throughput': metrics.throughput
            }

        return health_status


# Global service instance
realtime_tracking_service = RealTimeTrackingService()


# Convenience functions for easy integration
async def track_page_view(user_id: Optional[int], session_id: str,
                          page_url: str, metadata: Optional[Dict] = None):
    """Track a page view event."""
    return await realtime_tracking_service.track_event(
        event_type='page_view',
        data={'page_url': page_url, 'metadata': metadata},
        user_id=user_id,
        session_id=session_id,
        priority=ProcessingPriority.NORMAL
    )


async def track_user_action(user_id: Optional[int], session_id: str,
                           action_type: str, metadata: Optional[Dict] = None):
    """Track a user action event."""
    return await realtime_tracking_service.track_event(
        event_type='user_action',
        data={'action_type': action_type, 'metadata': metadata},
        user_id=user_id,
        session_id=session_id,
        priority=ProcessingPriority.NORMAL
    )


async def track_performance_metric(metric_type: str, value: float,
                                  unit: str = 'count', metadata: Optional[Dict] = None):
    """Track a performance metric."""
    return await realtime_tracking_service.track_event(
        event_type='performance',
        data={'metric_type': metric_type, 'value': value, 'unit': unit},
        priority=ProcessingPriority.HIGH,
        metadata=metadata
    )


# Initialize on import
try:
    # Start the service in the background
    asyncio.create_task(realtime_tracking_service.initialize())
except Exception as e:
    logger.error(f"Failed to auto-initialize real-time tracking: {e}")
