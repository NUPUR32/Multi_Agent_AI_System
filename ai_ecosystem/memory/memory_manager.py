"""
Memory Manager - Complete Cognitive Memory System
==================================================
Working Memory | Short-term | Long-term | Semantic | Episodic | Procedural | ...
"""

import json
import logging
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class MemoryType(Enum):
    WORKING = "working"
    SHORT_TERM = "short_term"
    LONG_TERM = "long_term"
    SEMANTIC = "semantic"
    EPISODIC = "episodic"
    PROCEDURAL = "procedural"
    CONVERSATION = "conversation"
    KNOWLEDGE = "knowledge"
    SKILL = "skill"
    PROJECT = "project"
    USER = "user"
    EMOTIONAL = "emotional"
    SPATIAL = "spatial"
    MUSCLE = "muscle"  # procedural skills
    ENCRYPTED = "encrypted"


class MemoryImportance(Enum):
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    TRIVIAL = 1


@dataclass
class MemoryEntry:
    """Single memory entry with rich metadata"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    summary: str = ""
    memory_type: MemoryType = MemoryType.WORKING
    importance: MemoryImportance = MemoryImportance.MEDIUM
    vector: Optional[List[float]] = None
    embedding: Optional[List[float]] = None
    tags: List[str] = field(default_factory=list)
    source: str = ""
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    project_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    access_count: int = 0
    last_accessed: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    expires_at: Optional[str] = None
    consolidated: bool = False
    forgotten: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content[:500],
            "summary": self.summary,
            "type": self.memory_type.value,
            "importance": self.importance.value,
            "tags": self.tags,
            "source": self.source,
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "project_id": self.project_id,
            "access_count": self.access_count,
            "created_at": self.created_at,
            "consolidated": self.consolidated,
        }


@dataclass
class MemoryStats:
    """Memory system statistics"""
    total_entries: int = 0
    by_type: Dict[str, int] = field(default_factory=dict)
    by_importance: Dict[str, int] = field(default_factory=dict)
    total_consolidated: int = 0
    total_forgotten: int = 0
    avg_access_count: float = 0.0
    storage_estimate_bytes: int = 0


class MemoryStore:
    """In-memory storage backend (pluggable with Redis/PostgreSQL)"""
    
    def __init__(self, max_entries: int = 100000):
        self._entries: Dict[str, MemoryEntry] = {}
        self._type_index: Dict[str, Set[str]] = {}
        self._tag_index: Dict[str, Set[str]] = {}
        self._agent_index: Dict[str, Set[str]] = {}
        self._max_entries = max_entries
    
    def add(self, entry: MemoryEntry):
        self._entries[entry.id] = entry
        
        # Index by type
        type_key = entry.memory_type.value
        if type_key not in self._type_index:
            self._type_index[type_key] = set()
        self._type_index[type_key].add(entry.id)
        
        # Index by tags
        for tag in entry.tags:
            if tag not in self._tag_index:
                self._tag_index[tag] = set()
            self._tag_index[tag].add(entry.id)
        
        # Index by agent
        if entry.agent_id:
            if entry.agent_id not in self._agent_index:
                self._agent_index[entry.agent_id] = set()
            self._agent_index[entry.agent_id].add(entry.id)
        
        # Enforce max entries
        if len(self._entries) > self._max_entries:
            self._evict_oldest()
    
    def get(self, memory_id: str) -> Optional[MemoryEntry]:
        entry = self._entries.get(memory_id)
        if entry:
            entry.access_count += 1
            entry.last_accessed = datetime.utcnow().isoformat()
        return entry
    
    def get_by_type(self, memory_type: MemoryType) -> List[MemoryEntry]:
        ids = self._type_index.get(memory_type.value, set())
        return [self._entries[i] for i in ids if i in self._entries and not self._entries[i].forgotten]
    
    def get_by_tag(self, tag: str) -> List[MemoryEntry]:
        ids = self._tag_index.get(tag, set())
        return [self._entries[i] for i in ids if i in self._entries and not self._entries[i].forgotten]
    
    def get_by_agent(self, agent_id: str) -> List[MemoryEntry]:
        ids = self._agent_index.get(agent_id, set())
        return [self._entries[i] for i in ids if i in self._entries and not self._entries[i].forgotten]
    
    def search(self, query: str, top_k: int = 10) -> List[MemoryEntry]:
        """Simple text-based search (replace with vector search in production)"""
        query_lower = query.lower()
        results = []
        for entry in self._entries.values():
            if entry.forgotten:
                continue
            if query_lower in entry.content.lower() or query_lower in entry.summary.lower():
                score = 0
                if query_lower in entry.content.lower():
                    score += entry.content.lower().count(query_lower)
                if query_lower in entry.summary.lower():
                    score += 3
                results.append((score, entry))
        
        results.sort(key=lambda x: -x[0])
        return [r[1] for r in results[:top_k]]
    
    def delete(self, memory_id: str) -> bool:
        if memory_id in self._entries:
            self._entries[memory_id].forgotten = True
            return True
        return False
    
    def get_stats(self) -> MemoryStats:
        stats = MemoryStats()
        stats.total_entries = len(self._entries)
        
        type_counts = {}
        importance_counts = {}
        for entry in self._entries.values():
            type_key = entry.memory_type.value
            type_counts[type_key] = type_counts.get(type_key, 0) + 1
            
            imp_key = entry.importance.name
            importance_counts[imp_key] = importance_counts.get(imp_key, 0) + 1
            
            if entry.consolidated:
                stats.total_consolidated += 1
            if entry.forgotten:
                stats.total_forgotten += 1
        
        stats.by_type = type_counts
        stats.by_importance = importance_counts
        stats.avg_access_count = sum(e.access_count for e in self._entries.values()) / max(1, len(self._entries))
        
        return stats
    
    def _evict_oldest(self):
        """Evict oldest working memory entries"""
        working = self.get_by_type(MemoryType.WORKING)
        if working:
            oldest = min(working, key=lambda e: e.created_at)
            del self._entries[oldest.id]
            logger.debug(f"Evicted oldest working memory: {oldest.id}")


class MemoryManager:
    """
    Complete cognitive memory system with all memory types
    Supports storage, retrieval, consolidation, forgetting, and ranking
    """
    
    def __init__(self):
        self._store = MemoryStore()
        self._event_bus = None
        self._consolidation_task = None
        logger.info("MemoryManager initialized")
    
    async def store(
        self,
        content: str,
        memory_type: MemoryType = MemoryType.SHORT_TERM,
        importance: MemoryImportance = MemoryImportance.MEDIUM,
        summary: str = "",
        tags: Optional[List[str]] = None,
        source: str = "",
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None,
        user_id: Optional[str] = None,
        project_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        expires_in_hours: Optional[int] = None,
    ) -> MemoryEntry:
        """Store a new memory entry"""
        expires_at = None
        if expires_in_hours:
            from datetime import timedelta
            expires_at = (datetime.utcnow() + timedelta(hours=expires_in_hours)).isoformat()
        
        entry = MemoryEntry(
            content=content,
            summary=summary or content[:200],
            memory_type=memory_type,
            importance=importance,
            tags=tags or [],
            source=source,
            agent_id=agent_id,
            session_id=session_id,
            user_id=user_id,
            project_id=project_id,
            context=context or {},
            metadata=metadata or {},
            expires_at=expires_at,
        )
        
        self._store.add(entry)
        
        if self._event_bus:
            from ..core.event_bus import Event, EventType
            await self._event_bus.publish(Event(
                type=EventType.MEMORY_WRITTEN,
                source="MemoryManager",
                payload={"memory_id": entry.id, "type": memory_type.value, "summary": entry.summary},
            ))
        
        logger.debug(f"Stored memory: {entry.id} ({memory_type.value})")
        return entry
    
    async def recall(self, memory_id: str) -> Optional[MemoryEntry]:
        """Recall a specific memory"""
        return self._store.get(memory_id)
    
    async def search(
        self,
        query: str,
        memory_type: Optional[MemoryType] = None,
        tags: Optional[List[str]] = None,
        top_k: int = 10,
    ) -> List[MemoryEntry]:
        """Search memories"""
        results = self._store.search(query, top_k=top_k)
        
        if memory_type:
            results = [r for r in results if r.memory_type == memory_type]
        
        if tags:
            results = [r for r in results if any(t in r.tags for t in tags)]
        
        return results[:top_k]
    
    async def get_recent(
        self,
        memory_type: Optional[MemoryType] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[MemoryEntry]:
        """Get most recent memories"""
        entries = list(self._store._entries.values())
        if memory_type:
            entries = [e for e in entries if e.memory_type == memory_type and not e.forgotten]
        else:
            entries = [e for e in entries if not e.forgotten]
        
        entries.sort(key=lambda e: e.created_at, reverse=True)
        return entries[offset:offset + limit]
    
    async def get_working_memory(self) -> List[MemoryEntry]:
        """Get current working memory"""
        return self._store.get_by_type(MemoryType.WORKING)
    
    async def consolidate(self):
        """Consolidate short-term memories to long-term"""
        short_term = self._store.get_by_type(MemoryType.SHORT_TERM)
        count = 0
        for entry in short_term:
            if entry.importance.value >= MemoryImportance.MEDIUM.value and not entry.consolidated:
                entry.memory_type = MemoryType.LONG_TERM
                entry.consolidated = True
                count += 1
        
        if count > 0:
            logger.info(f"Consolidated {count} memories to long-term")
            
            if self._event_bus:
                from ..core.event_bus import Event, EventType
                await self._event_bus.publish(Event(
                    type=EventType.MEMORY_CONSOLIDATED,
                    source="MemoryManager",
                    payload={"count": count},
                ))
    
    async def forget(self, threshold_days: int = 30):
        """Forget low-importance memories older than threshold"""
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=threshold_days)
        cutoff_str = cutoff.isoformat()
        
        count = 0
        for entry in list(self._store._entries.values()):
            if (entry.importance == MemoryImportance.TRIVIAL and 
                entry.created_at < cutoff_str and
                not entry.forgotten):
                entry.forgotten = True
                count += 1
        
        if count > 0:
            logger.info(f"Forgot {count} trivial memories")
            
            if self._event_bus:
                from ..core.event_bus import Event, EventType
                await self._event_bus.publish(Event(
                    type=EventType.MEMORY_FORGOTTEN,
                    source="MemoryManager",
                    payload={"count": count},
                ))
    
    async def get_memories_by_agent(self, agent_id: str) -> List[MemoryEntry]:
        return self._store.get_by_agent(agent_id)
    
    async def get_context_for_agent(self, agent_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get relevant context for an agent"""
        memories = self._store.get_by_agent(agent_id)
        memories.sort(key=lambda e: e.access_count, reverse=True)
        return [m.to_dict() for m in memories[:limit]]
    
    def get_stats(self) -> Dict[str, Any]:
        stats = self._store.get_stats()
        return {
            "total_entries": stats.total_entries,
            "by_type": stats.by_type,
            "by_importance": stats.by_importance,
            "consolidated": stats.total_consolidated,
            "forgotten": stats.total_forgotten,
            "avg_access_count": round(stats.avg_access_count, 2),
        }
    
    def set_event_bus(self, event_bus):
        self._event_bus = event_bus


# Global singleton
global_memory_manager = MemoryManager()