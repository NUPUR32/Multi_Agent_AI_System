"""
NUPUR32 AI OS - REST API Gateway
==================================
FastAPI-based REST API for external interaction with the AI ecosystem
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Depends, Security, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from .orchestrator import orchestrator
from .agents.agent_factory import global_agent_factory
from .memory.memory_manager import global_memory_manager
from .knowledge.knowledge_base import global_knowledge_base
from .reasoning.reasoning_engine import global_reasoning_engine, ReasoningMethod

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="NUPUR32 AI OS API",
    description="REST API for the NUPUR32 Autonomous AI Ecosystem",
    version="2035.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security_scheme = HTTPBearer(auto_error=False)


# ====================== MODELS ======================
class MissionRequest(BaseModel):
    objective: str
    priority: str = "normal"
    reasoning_method: Optional[str] = None


class MissionResponse(BaseModel):
    mission_id: str
    status: str
    phases: List[Dict[str, Any]]
    final_output: Optional[str] = None


class ReasonRequest(BaseModel):
    problem: str
    method: str = "chain_of_thought"
    context: Optional[Dict[str, Any]] = None


class MemoryStoreRequest(BaseModel):
    content: str
    memory_type: str = "short_term"
    importance: int = 3
    tags: Optional[List[str]] = None
    source: str = "api"


class SearchRequest(BaseModel):
    query: str
    top_k: int = 10
    category: Optional[str] = None


# ====================== MIDDLEWARE ======================
async def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme)):
    """Simple token verification - extend with JWT in production"""
    if credentials:
        return credentials.credentials
    return None


# ====================== ENDPOINTS ======================

@app.get("/", tags=["System"])
async def root():
    return {
        "name": "NUPUR32 AI OS",
        "version": "2035.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/health", tags=["System"])
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy" if orchestrator.running else "starting",
        "uptime_hours": (datetime.now() - orchestrator.start_time).total_seconds() / 3600 if orchestrator.start_time else 0,
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/status", tags=["System"])
async def system_status():
    """Comprehensive system status"""
    if not orchestrator.running:
        raise HTTPException(status_code=503, detail="System not initialized")
    return await orchestrator.get_system_status()


@app.post("/mission", response_model=MissionResponse, tags=["Missions"])
async def run_mission(request: MissionRequest):
    """Execute an AI mission"""
    if not orchestrator.running:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    result = await orchestrator.run_mission(request.objective)
    return MissionResponse(
        mission_id=result["mission_id"],
        status=result["status"],
        phases=result["phases"],
        final_output=result.get("final_output"),
    )


@app.post("/reason", tags=["Reasoning"])
async def reason(request: ReasonRequest):
    """Apply reasoning to a problem"""
    try:
        method = ReasoningMethod(request.method)
    except ValueError:
        method = ReasoningMethod.CHAIN_OF_THOUGHT
    
    result = await global_reasoning_engine.reason(
        problem=request.problem,
        method=method,
        context=request.context,
    )
    return result


@app.post("/memory/store", tags=["Memory"])
async def store_memory(request: MemoryStoreRequest):
    """Store a memory"""
    entry = await global_memory_manager.store(
        content=request.content,
        memory_type=request.memory_type,
        importance=request.importance,
        tags=request.tags,
        source=request.source,
    )
    return {"memory_id": entry.id, "status": "stored"}


@app.get("/memory/search", tags=["Memory"])
async def search_memory(query: str, top_k: int = 10):
    """Search memories"""
    results = await global_memory_manager.search(query=query, top_k=top_k)
    return {"results": [r.to_dict() for r in results]}


@app.get("/memory/stats", tags=["Memory"])
async def memory_stats():
    """Get memory statistics"""
    return global_memory_manager.get_stats()


@app.post("/knowledge/add", tags=["Knowledge"])
async def add_knowledge(content: str, title: str = "", category: str = "general",
                        tags: Optional[str] = None):
    """Add knowledge entry"""
    tag_list = tags.split(",") if tags else []
    entry = global_knowledge_base.add_text(
        content=content,
        title=title,
        category=category,
        tags=tag_list,
    )
    return {"entry_id": entry.id, "status": "added"}


@app.post("/knowledge/search", tags=["Knowledge"])
async def search_knowledge(request: SearchRequest):
    """Search knowledge base"""
    results = global_knowledge_base.search(
        query=request.query,
        top_k=request.top_k,
        category=request.category,
    )
    return {
        "results": [
            {
                "id": r.id,
                "title": r.title,
                "content": r.content[:500],
                "trust_score": r.trust_score,
                "source": r.source.value,
            }
            for r in results
        ]
    }


@app.get("/agents", tags=["Agents"])
async def list_agents():
    """List all agents"""
    agents = global_agent_factory.get_all_agents()
    return {
        "total": len(agents),
        "agents": [a.get_status_summary() for a in agents],
    }


@app.get("/agents/{role}", tags=["Agents"])
async def get_agent(role: str):
    """Get agent by role"""
    from .agents.base_agent import AgentRole
    try:
        agent_role = AgentRole(role)
    except ValueError:
        raise HTTPException(status_code=404, detail=f"Agent role '{role}' not found")
    
    agent = global_agent_factory.get_agent_by_role(agent_role)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{role}' not found")
    
    return agent.get_status_summary()


@app.get("/metrics", tags=["Monitoring"])
async def get_metrics():
    """Get system metrics"""
    from .monitoring.monitor import global_system_monitor
    return global_system_monitor.get_metrics_snapshot()


@app.get("/alerts", tags=["Monitoring"])
async def get_alerts():
    """Get recent alerts"""
    from .monitoring.monitor import global_system_monitor
    return {"alerts": global_system_monitor.get_alerts()}


@app.post("/init", tags=["System"])
async def initialize():
    """Initialize the system"""
    if orchestrator.running:
        return {"status": "already_running"}
    
    await orchestrator.initialize()
    return {"status": "initialized"}


@app.post("/shutdown", tags=["System"])
async def shutdown():
    """Shutdown the system"""
    await orchestrator.shutdown()
    return {"status": "shutdown_initiated"}