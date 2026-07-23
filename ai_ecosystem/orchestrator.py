"""
NUPUR32 AI OS - Main Orchestrator
==================================
The central system that initializes, configures, and manages all components
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from .config.settings import load_settings, get_settings
from .config.model_config import global_model_registry
from .core.event_bus import EventBus, Event, EventType, global_event_bus
from .core.service_discovery import ServiceRegistry, ServiceType, global_service_registry
from .core.di_container import global_container, DIContainer
from .core.secret_manager import global_secret_manager, SecretManager
from .core.plugin_system import global_plugin_manager, PluginManager
from .agents.base_agent import BaseAgent, AgentRole
from .agents.agent_factory import global_agent_factory, AgentFactory
from .agents.ceo_agent import CEOAgent
from .memory.memory_manager import global_memory_manager, MemoryManager, MemoryType, MemoryImportance
from .knowledge.knowledge_base import global_knowledge_base
from .knowledge.rag_engine import global_rag_engine
from .knowledge.knowledge_graph import global_knowledge_graph
from .reasoning.reasoning_engine import global_reasoning_engine, ReasoningEngine

logger = logging.getLogger(__name__)


class AIOrchestrator:
    """
    Main orchestrator of the NUPUR32 AI Ecosystem
    Initializes all components, manages lifecycle, handles shutdown
    """
    
    def __init__(self):
        self.settings = load_settings()
        self.running = False
        self.start_time = None
        self._shutdown_event = asyncio.Event()
        
        # Component references
        self.event_bus = global_event_bus
        self.service_registry = global_service_registry
        self.secret_manager = global_secret_manager
        self.plugin_manager = global_plugin_manager
        self.agent_factory = global_agent_factory
        self.memory_manager = global_memory_manager
        self.knowledge_base = global_knowledge_base
        self.rag_engine = global_rag_engine
        self.knowledge_graph = global_knowledge_graph
        self.reasoning_engine = global_reasoning_engine
        
        # Created agents
        self.agents: Dict[str, BaseAgent] = {}
        
        logger.info(f"{self.settings.project_name} Orchestrator initialized")
    
    async def initialize(self):
        """Initialize all system components"""
        logger.info("Initializing NUPUR32 AI Ecosystem...")
        self.start_time = datetime.now()
        
        # 1. Initialize core infrastructure
        await self._init_core()
        
        # 2. Initialize model registry
        self._init_models()
        
        # 3. Register core services
        await self._register_services()
        
        # 4. Initialize memory system
        await self._init_memory()
        
        # 5. Initialize knowledge system
        await self._init_knowledge()
        
        # 6. Initialize all agents
        await self._init_agents()
        
        # 7. Initialize plugin system
        await self._init_plugins()
        
        # 8. Start health checks
        await self.service_registry.start_health_checks(interval=30)
        
        # 9. Publish system startup event
        await self.event_bus.publish(Event(
            type=EventType.SYSTEM_STARTUP,
            source="Orchestrator",
            payload={
                "version": self.settings.version,
                "environment": self.settings.environment,
                "start_time": self.start_time.isoformat(),
            },
        ))
        
        # 10. Log system info
        agent_count = len(self.agents)
        logger.info(f"=== {self.settings.project_name} v{self.settings.version} ===")
        logger.info(f"Environment: {self.settings.environment}")
        logger.info(f"Agents initialized: {agent_count}")
        logger.info(f"System ready for missions")
        
        self.running = True
    
    async def _init_core(self):
        """Initialize core infrastructure"""
        logger.info("Initializing core infrastructure...")
        
        # Wire event bus to components
        self.service_registry.set_event_bus(self.event_bus)
        self.memory_manager.set_event_bus(self.event_bus)
        self.plugin_manager.set_event_bus(self.event_bus)
        
        # Register core in DI container
        global_container.register_singleton("EventBus", self.event_bus)
        global_container.register_singleton("ServiceRegistry", self.service_registry)
        global_container.register_singleton("SecretManager", self.secret_manager)
        
        logger.info("Core infrastructure initialized")
    
    def _init_models(self):
        """Initialize model registry with defaults"""
        logger.info("Initializing model registry...")
        global_model_registry.initialize_defaults()
        logger.info(f"Registered {len(global_model_registry.get_all_models())} models")
    
    async def _register_services(self):
        """Register core services in service registry"""
        await self.service_registry.register(
            name="EventBus",
            service_type=ServiceType.CORE,
            version=self.settings.version,
        )
        await self.service_registry.register(
            name="MemoryManager",
            service_type=ServiceType.MEMORY,
            version=self.settings.version,
        )
        await self.service_registry.register(
            name="KnowledgeBase",
            service_type=ServiceType.KNOWLEDGE,
            version=self.settings.version,
        )
        await self.service_registry.register(
            name="ReasoningEngine",
            service_type=ServiceType.REASONING,
            version=self.settings.version,
        )
    
    async def _init_memory(self):
        """Initialize memory system"""
        logger.info("Initializing memory system...")
        await self.memory_manager.store(
            content=f"NUPUR32 AI Ecosystem initialized at {self.start_time.isoformat()}",
            memory_type=MemoryType.SYSTEM if hasattr(MemoryType, 'SYSTEM') else MemoryType.SHORT_TERM,
            importance=MemoryImportance.CRITICAL,
            tags=["system", "startup"],
            source="Orchestrator",
        )
        logger.info("Memory system initialized")
    
    async def _init_knowledge(self):
        """Initialize knowledge system"""
        logger.info("Initializing knowledge system...")
        self.knowledge_base.add_text(
            content=f"NUPUR32 AI Ecosystem v{self.settings.version} - System Documentation",
            title="System Overview",
            category="system",
            tags=["system", "documentation"],
        )
        logger.info("Knowledge system initialized")
    
    async def _init_agents(self):
        """Initialize all agents"""
        logger.info("Initializing agent ecosystem...")
        
        # Register CEO agent class
        self.agent_factory.register_agent_class(AgentRole.CEO, CEOAgent)
        
        # Create all agents
        agents = self.agent_factory.create_all_agents()
        
        # Wire event bus to each agent
        for agent in agents.values():
            agent.set_event_bus(self.event_bus)
        
        # Register agents in service registry
        for agent in agents.values():
            await self.service_registry.register(
                name=agent.name,
                service_type=ServiceType.AGENT,
                version="1.0.0",
                capabilities=[c.value for c in agent.capabilities],
                metadata={"role": agent.role.value, "model": agent.model_name},
            )
        
        self.agents = agents
        logger.info(f"Initialized {len(agents)} agents")
    
    async def _init_plugins(self):
        """Initialize plugin system"""
        logger.info("Initializing plugin system...")
        self.plugin_manager.discover_plugins()
        for plugin in self.plugin_manager.plugins.values():
            try:
                self.plugin_manager.load_plugin(plugin.manifest.name)
            except Exception as e:
                logger.warning(f"Could not load plugin {plugin.manifest.name}: {e}")
    
    async def run_mission(self, objective: str) -> Dict[str, Any]:
        """
        Execute a full mission using the AI ecosystem
        1. CEO agent creates strategic plan
        2. Project manager breaks into tasks
        3. Specialized agents execute tasks
        4. Consensus and QA validate results
        5. Reflection agent learns from outcome
        """
        mission_id = f"mission_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Starting mission {mission_id}: {objective}")
        
        mission_result = {
            "mission_id": mission_id,
            "objective": objective,
            "started_at": datetime.utcnow().isoformat(),
            "phases": [],
            "final_output": None,
            "status": "in_progress",
        }
        
        try:
            # Phase 1: Strategic Planning (CEO)
            ceo = self.agent_factory.get_agent_by_role(AgentRole.CEO)
            if ceo:
                plan = await ceo.execute({
                    "id": f"{mission_id}_plan",
                    "type": "strategic_planning",
                    "objective": objective,
                })
                mission_result["phases"].append({
                    "phase": "strategic_planning",
                    "agent": "CEO",
                    "result": plan.output,
                })
            
            # Phase 2: Task Breakdown (Project Manager)
            pm = self.agent_factory.get_agent_by_role(AgentRole.PROJECT_MANAGER)
            if pm:
                breakdown = await pm.execute({
                    "id": f"{mission_id}_breakdown",
                    "type": "planning",
                    "objective": objective,
                })
                mission_result["phases"].append({
                    "phase": "task_breakdown",
                    "agent": "ProjectManager",
                    "result": breakdown.output,
                })
            
            # Phase 3: Research
            researcher = self.agent_factory.get_agent_by_role(AgentRole.RESEARCHER)
            if researcher:
                research = await researcher.execute({
                    "id": f"{mission_id}_research",
                    "type": "research",
                    "objective": objective,
                    "query": objective,
                })
                mission_result["phases"].append({
                    "phase": "research",
                    "agent": "Researcher",
                    "result": research.output,
                })
            
            # Phase 4: Reasoning
            reasoning_agent = self.agent_factory.get_agent_by_role(AgentRole.REASONING)
            if reasoning_agent:
                reasoning = await reasoning_agent.execute({
                    "id": f"{mission_id}_reasoning",
                    "type": "analysis",
                    "objective": objective,
                })
                mission_result["phases"].append({
                    "phase": "reasoning",
                    "agent": "Reasoning",
                    "result": reasoning.output,
                })
            
            # Phase 5: Quality Assurance
            qa = self.agent_factory.get_agent_by_role(AgentRole.QUALITY_ASSURANCE)
            if qa:
                quality = await qa.execute({
                    "id": f"{mission_id}_qa",
                    "type": "quality_check",
                    "objective": objective,
                })
                mission_result["phases"].append({
                    "phase": "quality_assurance",
                    "agent": "QA",
                    "result": quality.output,
                })
            
            # Phase 6: Store outcome in memory
            await self.memory_manager.store(
                content=f"Mission {mission_id}: {objective}",
                memory_type=MemoryType.PROJECT if hasattr(MemoryType, 'PROJECT') else MemoryType.LONG_TERM,
                importance=MemoryImportance.HIGH,
                tags=["mission", "completed"],
                source="Orchestrator",
            )
            
            mission_result["status"] = "completed"
            mission_result["final_output"] = f"Mission '{objective}' executed successfully across all phases"
            
            logger.info(f"Mission {mission_id} completed successfully")
            
        except Exception as e:
            mission_result["status"] = "failed"
            mission_result["error"] = str(e)
            logger.error(f"Mission {mission_id} failed: {e}")
        
        return mission_result
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        uptime = (datetime.now() - self.start_time).total_seconds() / 3600 if self.start_time else 0
        
        return {
            "name": self.settings.project_name,
            "version": self.settings.version,
            "environment": self.settings.environment,
            "status": "OPERATIONAL" if self.running else "STOPPED",
            "uptime_hours": round(uptime, 2),
            "agents": {
                "total": len(self.agents),
                "roles": [a.role.value for a in self.agents.values()],
            },
            "memory": self.memory_manager.get_stats(),
            "knowledge": self.knowledge_base.get_stats(),
            "event_bus": self.event_bus.get_stats(),
            "service_registry": self.service_registry.get_stats(),
            "secret_manager": self.secret_manager.get_stats(),
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    async def shutdown(self):
        """Graceful shutdown of all components"""
        logger.info("Shutting down NUPUR32 AI Ecosystem...")
        
        # Publish shutdown event
        await self.event_bus.publish(Event(
            type=EventType.SYSTEM_SHUTDOWN,
            source="Orchestrator",
            payload={"uptime_hours": (datetime.now() - self.start_time).total_seconds() / 3600 if self.start_time else 0},
        ))
        
        self.running = False
        self._shutdown_event.set()
        logger.info("NUPUR32 AI Ecosystem shutdown complete")


# Global orchestrator instance
orchestrator = AIOrchestrator()