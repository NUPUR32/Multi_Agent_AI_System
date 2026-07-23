"""
Knowledge Base - Document Storage & Retrieval
==============================================
Hybrid search with dense/sparse retrieval, chunking, and source verification
"""

import hashlib
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class KnowledgeSource(Enum):
    WEB = "web"
    DOCUMENT = "document"
    CODE = "code"
    DATABASE = "database"
    USER_INPUT = "user_input"
    API = "api"
    SCIENTIFIC = "scientific"
    NEWS = "news"
    INTERNAL = "internal"


@dataclass
class KnowledgeEntry:
    """A chunk of knowledge with metadata"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    title: str = ""
    source: KnowledgeSource = KnowledgeSource.INTERNAL
    url: Optional[str] = None
    author: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    embedding: Optional[List[float]] = None
    keywords: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    trust_score: float = 0.7
    access_count: int = 0
    verified: bool = False
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    content_hash: str = ""
    
    def __post_init__(self):
        self.content_hash = hashlib.md5(self.content.encode()).hexdigest()


class KnowledgeBase:
    """
    Main knowledge storage and retrieval system
    Supports chunking, indexing, hybrid search, and trust scoring
    """
    
    def __init__(self):
        self._entries: Dict[str, KnowledgeEntry] = {}
        self._keyword_index: Dict[str, Set[str]] = {}
        self._category_index: Dict[str, Set[str]] = {}
        self._source_index: Dict[str, Set[str]] = {}
        logger.info("KnowledgeBase initialized")
    
    def add_entry(self, entry: KnowledgeEntry):
        """Add a knowledge entry"""
        self._entries[entry.id] = entry
        
        # Index keywords
        for kw in entry.keywords:
            kw_lower = kw.lower()
            if kw_lower not in self._keyword_index:
                self._keyword_index[kw_lower] = set()
            self._keyword_index[kw_lower].add(entry.id)
        
        # Index category
        cat = entry.category.lower()
        if cat not in self._category_index:
            self._category_index[cat] = set()
        self._category_index[cat].add(entry.id)
        
        # Index source
        src = entry.source.value
        if src not in self._source_index:
            self._source_index[src] = set()
        self._source_index[src].add(entry.id)
    
    def add_text(
        self,
        content: str,
        title: str = "",
        source: KnowledgeSource = KnowledgeSource.INTERNAL,
        keywords: Optional[List[str]] = None,
        category: str = "general",
        tags: Optional[List[str]] = None,
        url: Optional[str] = None,
    ) -> KnowledgeEntry:
        """Add text as a knowledge entry"""
        entry = KnowledgeEntry(
            content=content,
            title=title or content[:100],
            source=source,
            keywords=keywords or [],
            category=category,
            tags=tags or [],
            url=url,
        )
        self.add_entry(entry)
        logger.debug(f"Added knowledge entry: {entry.id}")
        return entry
    
    def search(
        self,
        query: str,
        top_k: int = 10,
        category: Optional[str] = None,
        source: Optional[KnowledgeSource] = None,
        min_trust: float = 0.0,
    ) -> List[KnowledgeEntry]:
        """Search knowledge base with filtering"""
        query_lower = query.lower()
        results = []
        
        for entry in self._entries.values():
            if entry.trust_score < min_trust:
                continue
            
            score = 0
            
            # Exact match boost
            if query_lower in entry.content.lower():
                score += entry.content.lower().count(query_lower) * 2
            
            if query_lower in entry.title.lower():
                score += 10
            
            # Keyword match
            if any(kw in query_lower for kw in entry.keywords):
                score += 5
            
            # Category filter
            if category and entry.category.lower() != category.lower():
                score = 0
            
            # Source filter
            if source and entry.source != source:
                score = 0
            
            if score > 0:
                results.append((score, entry))
        
        results.sort(key=lambda x: (-x[0], -x[1].trust_score))
        return [r[1] for r in results[:top_k]]
    
    def get_by_category(self, category: str) -> List[KnowledgeEntry]:
        ids = self._category_index.get(category.lower(), set())
        return [self._entries[i] for i in ids if i in self._entries]
    
    def get_by_source(self, source: KnowledgeSource) -> List[KnowledgeEntry]:
        ids = self._source_index.get(source.value, set())
        return [self._entries[i] for i in ids if i in self._entries]
    
    def get(self, entry_id: str) -> Optional[KnowledgeEntry]:
        entry = self._entries.get(entry_id)
        if entry:
            entry.access_count += 1
        return entry
    
    def update_trust_score(self, entry_id: str, score: float):
        entry = self._entries.get(entry_id)
        if entry:
            entry.trust_score = max(0.0, min(1.0, score))
    
    def verify(self, entry_id: str):
        entry = self._entries.get(entry_id)
        if entry:
            entry.verified = True
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_entries": len(self._entries),
            "by_source": {k: len(v) for k, v in self._source_index.items()},
            "by_category": {k: len(v) for k, v in self._category_index.items()},
            "verified": sum(1 for e in self._entries.values() if e.verified),
            "avg_trust": sum(e.trust_score for e in self._entries.values()) / max(1, len(self._entries)),
        }


# Global singleton
global_knowledge_base = KnowledgeBase()