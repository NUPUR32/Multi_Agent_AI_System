"""Tests for the Memory system"""

import pytest
import asyncio
from ai_ecosystem.memory.memory_manager import MemoryManager, MemoryType, MemoryImportance


@pytest.fixture
def memory_manager():
    return MemoryManager()


@pytest.mark.asyncio
async def test_store_and_recall(memory_manager):
    entry = await memory_manager.store(
        content="Test memory content",
        memory_type=MemoryType.SHORT_TERM,
        importance=MemoryImportance.HIGH,
        tags=["test"],
        source="test",
    )
    
    retrieved = await memory_manager.recall(entry.id)
    assert retrieved is not None
    assert retrieved.content == "Test memory content"
    assert retrieved.importance == MemoryImportance.HIGH


@pytest.mark.asyncio
async def test_search(memory_manager):
    await memory_manager.store(
        content="Artificial intelligence is transforming the world",
        tags=["ai", "technology"],
        source="test",
    )
    await memory_manager.store(
        content="Python is a popular programming language",
        tags=["python", "coding"],
        source="test",
    )
    
    results = await memory_manager.search("artificial intelligence", top_k=5)
    assert len(results) >= 1
    assert "artificial intelligence" in results[0].content.lower()


@pytest.mark.asyncio
async def test_memory_types(memory_manager):
    await memory_manager.store("Working data", memory_type=MemoryType.WORKING, source="test")
    await memory_manager.store("Short term data", memory_type=MemoryType.SHORT_TERM, source="test")
    await memory_manager.store("Long term data", memory_type=MemoryType.LONG_TERM, source="test")
    
    working = await memory_manager.get_recent(memory_type=MemoryType.WORKING)
    assert len(working) == 1
    assert working[0].memory_type == MemoryType.WORKING


@pytest.mark.asyncio
async def test_consolidation(memory_manager):
    await memory_manager.store(
        "Important data",
        memory_type=MemoryType.SHORT_TERM,
        importance=MemoryImportance.HIGH,
        source="test",
    )
    
    await memory_manager.consolidate()
    
    long_term = await memory_manager.get_recent(memory_type=MemoryType.LONG_TERM)
    assert len(long_term) >= 1
    assert long_term[0].consolidated


@pytest.mark.asyncio
async def test_memory_stats(memory_manager):
    await memory_manager.store("Test 1", source="test")
    await memory_manager.store("Test 2", source="test")
    
    stats = memory_manager.get_stats()
    assert stats["total_entries"] >= 2
    assert "short_term" in stats["by_type"]


@pytest.mark.asyncio
async def test_agent_memory(memory_manager):
    await memory_manager.store(
        "Agent data",
        agent_id="agent-1",
        source="test",
    )
    
    memories = await memory_manager.get_memories_by_agent("agent-1")
    assert len(memories) == 1