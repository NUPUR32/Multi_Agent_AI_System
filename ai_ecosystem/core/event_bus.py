"""
Event Bus - Distributed Async Event System
===========================================
Supports pub/sub, event sourcing, CQRS events, streaming
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class EventPriority(Enum):
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3


class EventType(Enum):
    # System Events
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    SYSTEM_ERROR = "system.error"
    
    # Agent Events
    AGENT_REGISTERED = "agent.registered"
    AGENT_DEREGISTERED = "agent.deregistered"
    AGENT_TASK_STARTED = "agent.task.started"
    AGENT_TASK_COMPLETED = "agent.task.completed"
    AGENT_TASK_FAILED = "agent.task.failed"
    AGENT_MESSAGE = "agent.message"
    AGENT_HEARTBEAT = "agent.heartbeat"
    AGENT_CAPACITY_CHANGE = "agent.capacity.change"
    
    # Workflow Events
    WORKFLOW_CREATED = "workflow.created"
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
    WORKFLOW_PAUSED = "workflow.paused"
    WORKFLOW_RESUMED = "workflow.resumed"
    WORKFLOW_STEP_COMPLETED = "workflow.step.completed"
    
    # Memory Events
    MEMORY_WRITTEN = "memory.written"
    MEMORY_CONSOLIDATED = "memory.consolidated"
    MEMORY_FORGOTTEN = "memory.forgotten"
    
    # Knowledge Events
    KNOWLEDGE_ADDED = "knowledge.added"
    KNOWLEDGE_UPDATED = "knowledge.updated"
    KNOWLEDGE_VERIFIED = "knowledge.verified"
    KNOWLEDGE_INVALIDATED = "knowledge.invalidated"
    
    # Security Events
    SECURITY_ALERT = "security.alert"
    SECURITY_BREACH = "security.breach"
    AUTH_SUCCESS = "auth.success"
    AUTH_FAILURE = "auth.failure"
    
    # Learning Events
    LEARNING_EXPERIENCE = "learning.experience"
    MODEL_UPDATE = "model.update"
    PERFORMANCE_REPORT = "performance.report"
    
    # Monitoring Events
    METRIC_COLLECTED = "metric.collected"
    THRESHOLD_EXCEEDED = "threshold.exceeded"
    HEALTH_CHECK_FAILED = "healthcheck.failed"
    
    # Custom Events
    USER_DEFINED = "user.defined"


@dataclass
class Event:
    """Universal event structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: EventType = EventType.USER_DEFINED
    type_name: str = ""
    source: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: EventPriority = EventPriority.NORMAL
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    tenant_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type_name or self.type.value,
            "source": self.source,
            "payload": self.payload,
            "metadata": self.metadata,
            "priority": self.priority.name,
            "timestamp": self.timestamp,
            "correlation_id": self.correlation_id,
            "causation_id": self.causation_id,
            "tenant_id": self.tenant_id,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), default=str)

    @classmethod
    def from_json(cls, data: str) -> "Event":
        d = json.loads(data)
        return cls(
            id=d.get("id", str(uuid.uuid4())),
            type_name=d.get("type", ""),
            source=d.get("source", ""),
            payload=d.get("payload", {}),
            metadata=d.get("metadata", {}),
            priority=EventPriority[d.get("priority", "NORMAL")],
            timestamp=d.get("timestamp", datetime.utcnow().isoformat()),
            correlation_id=d.get("correlation_id"),
            causation_id=d.get("causation_id"),
            tenant_id=d.get("tenant_id"),
        )


class Subscription:
    """Represents a subscription to an event type"""
    
    def __init__(
        self,
        event_type: str,
        callback: Callable[[Event], Any],
        filter_fn: Optional[Callable[[Event], bool]] = None,
        subscriber_id: Optional[str] = None,
    ):
        self.id = str(uuid.uuid4())
        self.event_type = event_type
        self.callback = callback
        self.filter_fn = filter_fn
        self.subscriber_id = subscriber_id or callback.__name__
        self.created = datetime.utcnow()

    def matches(self, event: Event) -> bool:
        if event.type_name != self.event_type and event.type.value != self.event_type:
            return False
        if self.filter_fn and not self.filter_fn(event):
            return False
        return True

    async def invoke(self, event: Event) -> Any:
        try:
            if asyncio.iscoroutinefunction(self.callback):
                return await self.callback(event)
            return self.callback(event)
        except Exception as e:
            logger.error(f"Subscription {self.id} handler error: {e}")
            raise


class EventStore:
    """Event sourcing / persistence layer"""
    
    def __init__(self, max_events: int = 10000):
        self.events: List[Event] = []
        self.max_events = max_events
        self._lock = asyncio.Lock()
    
    async def append(self, event: Event):
        async with self._lock:
            self.events.append(event)
            if len(self.events) > self.max_events:
                self.events = self.events[-self.max_events:]
    
    async def get_events(
        self,
        event_type: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Event]:
        async with self._lock:
            filtered = self.events
            if event_type:
                filtered = [e for e in filtered if e.type_name == event_type or e.type.value == event_type]
            if source:
                filtered = [e for e in filtered if e.source == source]
            return filtered[offset:offset + limit]
    
    async def replay(self, event_type: str, callback: Callable[[Event], Any]):
        """Replay historical events to rebuild state"""
        events = await self.get_events(event_type=event_type)
        for event in events:
            try:
                await callback(event) if asyncio.iscoroutinefunction(callback) else callback(event)
            except Exception as e:
                logger.error(f"Replay error: {e}")


class EventBus:
    """
    High-performance distributed event bus
    Supports pub/sub, event sourcing, and streaming
    """
    
    def __init__(self, enable_persistence: bool = True):
        self.subscriptions: Dict[str, List[Subscription]] = {}
        self.global_subscriptions: List[Subscription] = []
        self.event_store = EventStore() if enable_persistence else None
        self._lock = asyncio.Lock()
        self._stats = {"published": 0, "delivered": 0, "failed": 0}
        logger.info("EventBus initialized")

    def subscribe(
        self,
        event_type: str,
        callback: Callable[[Event], Any],
        filter_fn: Optional[Callable[[Event], bool]] = None,
        subscriber_id: Optional[str] = None,
    ) -> Subscription:
        """Subscribe to a specific event type"""
        sub = Subscription(event_type, callback, filter_fn, subscriber_id)
        if event_type not in self.subscriptions:
            self.subscriptions[event_type] = []
        self.subscriptions[event_type].append(sub)
        logger.debug(f"Subscribed {sub.subscriber_id} to {event_type}")
        return sub

    def subscribe_all(
        self,
        callback: Callable[[Event], Any],
        filter_fn: Optional[Callable[[Event], bool]] = None,
        subscriber_id: Optional[str] = None,
    ) -> Subscription:
        """Subscribe to all events"""
        sub = Subscription("*", callback, filter_fn, subscriber_id or "global_listener")
        self.global_subscriptions.append(sub)
        logger.debug(f"Global subscriber added: {sub.subscriber_id}")
        return sub

    def unsubscribe(self, subscription: Subscription):
        """Remove a subscription"""
        if subscription.event_type in self.subscriptions:
            self.subscriptions[subscription.event_type] = [
                s for s in self.subscriptions[subscription.event_type]
                if s.id != subscription.id
            ]
        self.global_subscriptions = [
            s for s in self.global_subscriptions if s.id != subscription.id
        ]

    async def publish(self, event: Event) -> int:
        """
        Publish an event to all matching subscribers
        Returns number of successful deliveries
        """
        async with self._lock:
            self._stats["published"] += 1
        
        # Persist if store enabled
        if self.event_store:
            await self.event_store.append(event)
        
        # Find matched subscribers
        matched = []
        
        # Check type-specific subscribers
        subs = self.subscriptions.get(event.type.value, []) + \
               self.subscriptions.get(event.type_name, []) + \
               self.subscriptions.get("*", [])
        
        for sub in subs + self.global_subscriptions:
            if sub.matches(event):
                matched.append(sub)
        
        # Deliver in priority order
        deliveries = 0
        tasks = []
        for sub in matched:
            tasks.append(self._deliver(sub, event))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, Exception):
                logger.error(f"Event delivery failed: {r}")
            else:
                deliveries += 1
        
        async with self._lock:
            self._stats["delivered"] += deliveries
            self._stats["failed"] += (len(matched) - deliveries)
        
        return deliveries

    async def _deliver(self, subscription: Subscription, event: Event):
        try:
            await subscription.invoke(event)
        except Exception as e:
            logger.error(f"Failed to deliver event {event.id} to {subscription.subscriber_id}: {e}")
            raise

    async def publish_and_wait(
        self,
        event: Event,
        response_type: str,
        timeout: float = 30.0,
    ) -> Optional[Event]:
        """Publish and wait for a response event"""
        response_event = None
        response_received = asyncio.Event()
        
        def response_handler(event: Event):
            nonlocal response_event
            response_event = event
            response_received.set()
        
        sub = self.subscribe(response_type, response_handler)
        try:
            await self.publish(event)
            await asyncio.wait_for(response_received.wait(), timeout=timeout)
            return response_event
        except asyncio.TimeoutError:
            logger.warning(f"Timeout waiting for {response_type}")
            return None
        finally:
            self.unsubscribe(sub)

    async def stream(self, event_type: str, batch_size: int = 10, interval: float = 0.1):
        """Async generator for event streaming"""
        buffer = []
        while True:
            events = await self.event_store.get_events(event_type=event_type, limit=batch_size)
            for event in events:
                if event.id not in buffer:
                    buffer.append(event.id)
                    yield event
            await asyncio.sleep(interval)

    def get_stats(self) -> Dict[str, Any]:
        return {
            **self._stats,
            "subscriptions": sum(len(s) for s in self.subscriptions.values()),
            "global_subscriptions": len(self.global_subscriptions),
            "stored_events": len(self.event_store.events) if self.event_store else 0,
        }

    async def reset(self):
        """Reset event bus state"""
        async with self._lock:
            self.subscriptions.clear()
            self.global_subscriptions.clear()
            self._stats = {"published": 0, "delivered": 0, "failed": 0}
            if self.event_store:
                self.event_store.events.clear()


# Global singleton
global_event_bus = EventBus()