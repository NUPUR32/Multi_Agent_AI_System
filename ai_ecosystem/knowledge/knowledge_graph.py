"""
Knowledge Graph - Entity Relationship Network
==============================================
Triple store with entity linking, relationship extraction, and graph queries
"""

import json
import logging
import uuid
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeTriple:
    """Subject-Predicate-Object triple"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    subject: str = ""
    predicate: str = ""
    object: str = ""
    confidence: float = 1.0
    source: str = ""
    created_at: str = ""


@dataclass
class GraphNode:
    """Node in the knowledge graph"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    label: str = ""
    type: str = "entity"
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""


class KnowledgeGraph:
    """
    Knowledge graph with triple storage and graph traversal
    """
    
    def __init__(self):
        self._nodes: Dict[str, GraphNode] = {}
        self._triples: Dict[str, KnowledgeTriple] = {}
        self._node_label_index: Dict[str, Set[str]] = {}
        self._subject_index: Dict[str, Set[str]] = {}
        self._object_index: Dict[str, Set[str]] = {}
        logger.info("KnowledgeGraph initialized")
    
    def add_node(self, label: str, node_type: str = "entity",
                 properties: Optional[Dict[str, Any]] = None) -> GraphNode:
        """Add a node to the graph"""
        node = GraphNode(
            label=label,
            type=node_type,
            properties=properties or {},
        )
        self._nodes[node.id] = node
        
        label_lower = label.lower()
        if label_lower not in self._node_label_index:
            self._node_label_index[label_lower] = set()
        self._node_label_index[label_lower].add(node.id)
        
        return node
    
    def add_triple(self, subject: str, predicate: str, object: str,
                   confidence: float = 1.0, source: str = "") -> KnowledgeTriple:
        """Add a knowledge triple"""
        triple = KnowledgeTriple(
            subject=subject,
            predicate=predicate,
            object=object,
            confidence=confidence,
            source=source,
        )
        self._triples[triple.id] = triple
        
        # Index by subject and object
        subj_lower = subject.lower()
        if subj_lower not in self._subject_index:
            self._subject_index[subj_lower] = set()
        self._subject_index[subj_lower].add(triple.id)
        
        obj_lower = object.lower()
        if obj_lower not in self._object_index:
            self._object_index[obj_lower] = set()
        self._object_index[obj_lower].add(triple.id)
        
        return triple
    
    def query_subject(self, subject: str) -> List[KnowledgeTriple]:
        """Find all triples with given subject"""
        subj_lower = subject.lower()
        ids = self._subject_index.get(subj_lower, set())
        return [self._triples[i] for i in ids if i in self._triples]
    
    def query_object(self, object: str) -> List[KnowledgeTriple]:
        """Find all triples with given object"""
        obj_lower = object.lower()
        ids = self._object_index.get(obj_lower, set())
        return [self._triples[i] for i in ids if i in self._triples]
    
    def query_path(self, start: str, end: str, max_depth: int = 3) -> List[List[KnowledgeTriple]]:
        """Find paths between two entities"""
        paths = []
        
        def dfs(current: str, target: str, depth: int, path: List[KnowledgeTriple], visited: Set[str]):
            if depth > max_depth:
                return
            if current == target and path:
                paths.append(path.copy())
                return
            
            for triple in self.query_subject(current):
                if triple.object not in visited:
                    visited.add(triple.object)
                    path.append(triple)
                    dfs(triple.object, target, depth + 1, path, visited)
                    path.pop()
                    visited.discard(triple.object)
        
        dfs(start, end, 0, [], {start})
        return paths
    
    def get_related(self, entity: str, relation: Optional[str] = None) -> List[Tuple[str, str, float]]:
        """Get entities related to a given entity"""
        results = []
        for triple in self.query_subject(entity):
            if relation and triple.predicate != relation:
                continue
            results.append((triple.object, triple.predicate, triple.confidence))
        return results


global_knowledge_graph = KnowledgeGraph()