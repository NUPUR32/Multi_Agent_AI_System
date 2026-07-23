"""Tests for the Event Bus system"""

import pytest
import asyncio
from ai_ecosystem.core.event_bus import EventBus, Event, EventType, EventPriority


@pytest.fixture
def event_bus():
    return EventBus(enable_persistence=True)


@pytest.mark.asyncio
async def test_publish_and_subscribe(event_bus):
    received_events = []
    
    async def handler(event):
        received_events.append(event)
    
    event_bus.subscribe(EventType.AGENT_REGISTERED.value, handler)
    
    event = Event(
        type=EventType.AGENT_REGISTERED,
        source="test",
        payload={"agent": "test-agent"},
    )
    
    count = await event_bus.publish(event)
    assert count >= 1
    assert len(received_events) == 1
    assert received_events[0].source == "test"


@pytest.mark.asyncio
async def test_global_subscription(event_bus):
    received_events = []
    
    async def handler(event):
        received_events.append(event)
    
    event_bus.subscribe_all(handler)
    
    await event_bus.publish(Event(type=EventType.SYSTEM_STARTUP, source="test"))
    await event_bus.publish(Event(type=EventType.SYSTEM_SHUTDOWN, source="test"))
    
    assert len(received_events) == 2


@pytest.mark.asyncio
async def test_event_persistence(event_bus):
    await event_bus.publish(Event(type=EventType.SYSTEM_STARTUP, source="test"))
    await event_bus.publish(Event(type=EventType.AGENT_TASK_COMPLETED, source="test"))
    
    events = await event_bus.event_store.get_events(limit=10)
    assert len(events) == 2


@pytest.mark.asyncio
async def test_unsubscribe(event_bus):
    received = []
    
    def handler(event):
        received.append(event)
    
    sub = event_bus.subscribe(EventType.SYSTEM_STARTUP.value, handler)
    event_bus.unsubscribe(sub)
    
    await event_bus.publish(Event(type=EventType.SYSTEM_STARTUP, source="test"))
    assert len(received) == 0


@pytest.mark.asyncio
async def test_filtered_subscription(event_bus):
    received = []
    
    def handler(event):
        received.append(event)
    
    def filter_fn(event):
        return event.source == "important"
    
    event_bus.subscribe(EventType.SYSTEM_STARTUP.value, handler, filter_fn=filter_fn)
    
    await event_bus.publish(Event(type=EventType.SYSTEM_STARTUP, source="other"))
    await event_bus.publish(Event(type=EventType.SYSTEM_STARTUP, source="important"))
    
    assert len(received) == 1
    assert received[0].source == "important"


@pytest.mark.asyncio
async def test_event_stats(event_bus):
    await event_bus.publish(Event(type=EventType.SYSTEM_STARTUP, source="test"))
    stats = event_bus.get_stats()
    assert stats["published"] >= 1