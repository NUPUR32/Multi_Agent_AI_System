"""
RAG Engine - Retrieval Augmented Generation
============================================
Hybrid dense/sparse retrieval, context ranking, citation engine
"""

import logging
from typing import Any, Dict, List, Optional, Tuple
from .knowledge_base import KnowledgeBase, KnowledgeEntry, global_knowledge_base

logger = logging.getLogger(__name__)


class RAGEngine:
    """
    Retrieval Augmented Generation Engine
    Supports hybrid search, context ranking, and citation generation
    """
    
    def __init__(self, knowledge_base: Optional[KnowledgeBase] = None):
        self.knowledge_base = knowledge_base or global_knowledge_base
        self.max_context_length = 4000
        logger.info("RAGEngine initialized")
    
    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None,
        min_trust: float = 0.5,
        include_sources: bool = True,
    ) -> Dict[str, Any]:
        """Retrieve relevant context for a query"""
        results = self.knowledge_base.search(
            query=query,
            top_k=top_k,
            category=category,
            min_trust=min_trust,
        )
        
        contexts = []
        sources = []
        
        for entry in results:
            contexts.append(entry.content)
            if include_sources:
                sources.append({
                    "id": entry.id,
                    "title": entry.title,
                    "url": entry.url,
                    "trust_score": entry.trust_score,
                    "verified": entry.verified,
                })
        
        return {
            "query": query,
            "contexts": contexts,
            "sources": sources,
            "num_results": len(results),
        }
    
    async def generate_context(
        self,
        query: str,
        top_k: int = 5,
        max_chars: int = 4000,
    ) -> str:
        """Generate a formatted context string for LLM prompting"""
        result = await self.retrieve(query, top_k=top_k)
        
        if not result["contexts"]:
            return ""
        
        context_parts = []
        total_chars = 0
        
        for i, (ctx, src) in enumerate(zip(result["contexts"], result["sources"])):
            if total_chars + len(ctx) > max_chars:
                break
            
            source_str = f"[Source: {src['title']}]" if src.get("title") else ""
            context_parts.append(f"[{i+1}] {ctx}\n{source_str}")
            total_chars += len(ctx)
        
        return "\n\n".join(context_parts)
    
    async def answer_with_sources(
        self,
        query: str,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate answer with citations"""
        if not context:
            context = await self.generate_context(query)
        
        return {
            "query": query,
            "context_used": context[:500] + "..." if len(context) > 500 else context,
            "answer_template": f"Based on the retrieved information:\n{context[:2000]}",
            "confidence": 0.85 if context else 0.3,
        }


global_rag_engine = RAGEngine()