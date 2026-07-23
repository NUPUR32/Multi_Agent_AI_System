"""
System Monitor - Complete Observability
=========================================
Metrics collection, health checks, performance tracking, GPU monitoring
"""

import json
import logging
import time
import uuid
from collections import defaultdict
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMING = "timing"


class Metric:
    """Individual metric entry"""
    def __init__(self, name: str, value: float, metric_type: MetricType = MetricType.GAUGE,
                 tags: Optional[Dict[str, str]] = None):
        self.name = name
        self.value = value
        self.type = metric_type
        self.tags = tags or {}
        self.timestamp = datetime.utcnow().isoformat()


class HealthCheck:
    """Health check definition"""
    def __init__(self, name: str, check_fn: Callable, interval: int = 60):
        self.name = name
        self.check_fn = check_fn
        self.interval = interval
        self.last_check = 0.0
        self.last_result = True
        self.last_error = None


class SystemMonitor:
    """
    Complete system monitoring with metrics, health checks, and alerting
    """
    
    def __init__(self):
        self._metrics: Dict[str, List[Metric]] = defaultdict(list)
        self._counters: Dict[str, float] = defaultdict(float)
        self._gauges: Dict[str, float] = {}
        self._health_checks: List[HealthCheck] = []
        self._alerts: List[Dict[str, Any]] = []
        self._timings: Dict[str, List[float]] = defaultdict(list)
        logger.info("SystemMonitor initialized")
    
    def increment(self, name: str, value: float = 1.0, tags: Optional[Dict[str, str]] = None):
        """Increment a counter metric"""
        self._counters[name] += value
        self._metrics[name].append(Metric(name, self._counters[name], MetricType.COUNTER, tags))
    
    def gauge(self, name: str, value: float, tags: Optional[Dict[str, str]] = None):
        """Set a gauge metric"""
        self._gauges[name] = value
        self._metrics[name].append(Metric(name, value, MetricType.GAUGE, tags))
    
    def timing(self, name: str, duration_ms: float):
        """Record a timing metric"""
        self._timings[name].append(duration_ms)
        # Keep only last 100 timings
        if len(self._timings[name]) > 100:
            self._timings[name] = self._timings[name][-100:]
    
    def time(self, name: str):
        """Context manager for timing"""
        class Timer:
            def __init__(self, monitor, name):
                self.monitor = monitor
                self.name = name
                self.start = 0.0
            
            def __enter__(self):
                self.start = time.time()
                return self
            
            def __exit__(self, *args):
                duration = (time.time() - self.start) * 1000
                self.monitor.timing(self.name, duration)
        
        return Timer(self, name)
    
    def register_health_check(self, name: str, check_fn: Callable, interval: int = 60):
        """Register a health check"""
        self._health_checks.append(HealthCheck(name, check_fn, interval))
    
    def run_health_checks(self) -> List[Dict[str, Any]]:
        """Run all registered health checks"""
        results = []
        now = time.time()
        
        for check in self._health_checks:
            if now - check.last_check >= check.interval:
                try:
                    result = check.check_fn()
                    check.last_result = bool(result)
                    check.last_error = None
                except Exception as e:
                    check.last_result = False
                    check.last_error = str(e)
                
                check.last_check = now
                
                results.append({
                    "name": check.name,
                    "healthy": check.last_result,
                    "error": check.last_error,
                    "timestamp": datetime.utcnow().isoformat(),
                })
                
                if not check.last_result:
                    self.trigger_alert(f"Health check failed: {check.name}", check.last_error)
        
        return results
    
    def trigger_alert(self, title: str, message: str = "", severity: str = "warning"):
        """Trigger an alert"""
        alert = {
            "id": str(uuid.uuid4()),
            "title": title,
            "message": message,
            "severity": severity,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._alerts.append(alert)
        logger.warning(f"ALERT: {title} - {message}")
        
        # Keep only last 100 alerts
        if len(self._alerts) > 100:
            self._alerts = self._alerts[-100:]
        
        return alert
    
    def get_metrics_snapshot(self) -> Dict[str, Any]:
        """Get current metrics snapshot"""
        # Calculate timing stats
        timing_stats = {}
        for name, values in self._timings.items():
            if values:
                timing_stats[name] = {
                    "avg": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "p95": sorted(values)[int(len(values) * 0.95)],
                    "count": len(values),
                }
        
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "timings": timing_stats,
            "alerts_active": len(self._alerts),
            "health_checks": len(self._health_checks),
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    def get_alerts(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._alerts[-limit:]
    
    def get_health_summary(self) -> Dict[str, Any]:
        healthy = sum(1 for c in self._health_checks if c.last_result)
        total = len(self._health_checks)
        return {
            "healthy_checks": healthy,
            "total_checks": total,
            "health_score": round(healthy / max(1, total) * 100, 1),
            "checks": [
                {"name": c.name, "healthy": c.last_result, "error": c.last_error}
                for c in self._health_checks
            ],
        }


# Global singleton
global_system_monitor = SystemMonitor()