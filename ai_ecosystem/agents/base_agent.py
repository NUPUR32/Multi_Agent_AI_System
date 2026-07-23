"""
Base Agent - Foundation for All AI Agents
==========================================
Each agent has: goals, personality, capabilities, memory, reflection, confidence, performance
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Type
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    CEO = "ceo"
    PROJECT_MANAGER = "project_manager"
    ARCHITECT = "architect"
    PLANNER = "planner"
    RESEARCHER = "researcher"
    INTERNET = "internet"
    REASONING = "reasoning"
    CODING = "coding"
    REVIEWER = "reviewer"
    DEBUGGER = "debugger"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    SECURITY = "security"
    DEVOPS = "devops"
    CLOUD = "cloud"
    DATA_ENGINEER = "data_engineer"
    ML_ENGINEER = "ml_engineer"
    VISION = "vision"
    SPEECH = "speech"
    IMAGE = "image"
    VIDEO = "video"
    BROWSER = "browser"
    COMPUTER_CONTROL = "computer_control"
    EMAIL = "email"
    CALENDAR = "calendar"
    FINANCE = "finance"
    LEGAL = "legal"
    ANALYTICS = "analytics"
    MEMORY = "memory"
    KNOWLEDGE = "knowledge"
    REFLECTION = "reflection"
    LEARNING = "learning"
    OPTIMIZATION = "optimization"
    MONITORING = "monitoring"
    SUPERVISOR = "supervisor"
    CONSENSUS = "consensus"
    QUALITY_ASSURANCE = "quality_assurance"
    ETHICS = "ethics"
    RISK_ANALYSIS = "risk_analysis"
    DECISION = "decision"
    EXECUTION = "execution"
    EMERGENCY_RECOVERY = "emergency_recovery"


class AgentCapability(Enum):
    PLANNING = "planning"
    RESEARCH = "research"
    CODING = "coding"
    DEBUGGING = "debugging"
    TESTING = "testing"
    REVIEWING = "reviewing"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"
    SECURITY = "security"
    DATA_ANALYSIS = "data_analysis"
    ML_TRAINING = "ml_training"
    VISION_PROCESSING = "vision_processing"
    SPEECH_PROCESSING = "speech_processing"
    IMAGE_GENERATION = "image_generation"
    VIDEO_PROCESSING = "video_processing"
    BROWSER_AUTOMATION = "browser_automation"
    COMPUTER_CONTROL = "computer_control"
    EMAIL = "email"
    CALENDAR = "calendar"
    FINANCE = "finance"
    LEGAL = "legal"
    ANALYTICS = "analytics"
    MEMORY_MANAGEMENT = "memory_management"
    KNOWLEDGE_MANAGEMENT = "knowledge_management"
    REASONING = "reasoning"
    REFLECTION = "reflection"
    LEARNING = "learning"
    OPTIMIZATION = "optimization"
    DECISION_MAKING = "decision_making"
    RISK_ASSESSMENT = "risk_assessment"
    CONSENSUS_BUILDING = "consensus_building"
    QUALITY_CONTROL = "quality_control"
    ETHICS = "ethics"
    EMERGENCY_RECOVERY = "emergency_recovery"
    ORCHESTRATION = "orchestration"
    DELEGATION = "delegation"
    DOCUMENTATION = "documentation"
    COMMUNICATION = "communication"


class AgentStatus(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    WORKING = "working"
    WAITING = "waiting"
    ERROR = "error"
    RECOVERING = "recovering"
    STOPPED = "stopped"


@dataclass
class AgentPersonality:
    """Agent personality traits"""
    openness: float = 0.7
    conscientiousness: float = 0.8
    extraversion: float = 0.5
    agreeableness: float = 0.6
    neuroticism: float = 0.3
    risk_tolerance: float = 0.5
    creativity: float = 0.6
    analytical: float = 0.8
    assertiveness: float = 0.6
    empathy: float = 0.5


@dataclass
class AgentMemory:
    """Agent's personal memory"""
    experiences: List[Dict[str, Any]] = field(default_factory=list)
    learnings: List[str] = field(default_factory=list)
    skills: Dict[str, float] = field(default_factory=dict)
    preferences: Dict[str, Any] = field(default_factory=dict)
    performance_history: List[Dict[str, Any]] = field(default_factory=list)
    max_experiences: int = 100


@dataclass
class TaskResult:
    """Result of an agent task execution"""
    task_id: str = ""
    agent_id: str = ""
    success: bool = False
    output: Any = None
    error: Optional[str] = None
    confidence: float = 0.0
    duration_ms: float = 0.0
    reasoning_path: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class BaseAgent:
    """
    Foundation class for all AI agents in the ecosystem.
    Provides: identity, goals, capabilities, memory, reflection, communication, performance tracking
    """
    
    def __init__(
        self,
        name: str,
        role: AgentRole,
        description: str = "",
        goal: str = "",
        personality: Optional[AgentPersonality] = None,
        capabilities: Optional[List[AgentCapability]] = None,
        model_name: str = "gpt-4o",
        max_concurrent_tasks: int = 3,
    ):
        self.id = str(uuid.uuid4())
        self.name = name
        self.role = role
        self.description = description or f"{role.value.replace('_', ' ').title()} Agent"
        self.goal = goal or f"Execute {role.value} tasks effectively"
        self.personality = personality or AgentPersonality()
        self.capabilities = capabilities or []
        self.model_name = model_name
        self.max_concurrent_tasks = max_concurrent_tasks
        
        # State
        self.status = AgentStatus.IDLE
        self.memory = AgentMemory()
        self.current_tasks: Dict[str, Any] = {}
        self.task_history: List[TaskResult] = []
        self.confidence_score: float = 0.5
        self.performance_score: float = 0.5
        self.total_tasks_completed: int = 0
        self.total_tasks_failed: int = 0
        self.average_duration_ms: float = 0.0
        self.created_at = datetime.utcnow().isoformat()
        self.last_active = self.created_at
        
        # Event bus reference
        self._event_bus = None
        
        logger.info(f"Agent created: {self.name} ({role.value})")
    
    async def think(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core thinking method - agent's reasoning process
        Override in specialized agents
        """
        self.status = AgentStatus.THINKING
        self.last_active = datetime.utcnow().isoformat()
        
        thought = {
            "agent_id": self.id,
            "agent_name": self.name,
            "timestamp": datetime.utcnow().isoformat(),
            "context": context,
            "reasoning": [],
            "conclusion": None,
        }
        
        return thought
    
    async def execute(self, task: Dict[str, Any]) -> TaskResult:
        """
        Execute a task with full lifecycle management
        """
        task_id = task.get("id", str(uuid.uuid4()))
        start_time = time.time()
        
        self.status = AgentStatus.WORKING
        self.current_tasks[task_id] = task
        self.last_active = datetime.utcnow().isoformat()
        
        logger.info(f"Agent {self.name} executing task {task_id}")
        
        # Publish event
        if self._event_bus:
            from ..core.event_bus import Event, EventType
            await self._event_bus.publish(Event(
                type=EventType.AGENT_TASK_STARTED,
                source=self.name,
                payload={"task_id": task_id, "agent_id": self.id, "task": task},
            ))
        
        try:
            # Think about the task
            thought = await self.think(task)
            
            # Execute the task (override in subclasses)
            result = await self._execute_task(task, thought)
            
            # Record success
            duration_ms = (time.time() - start_time) * 1000
            task_result = TaskResult(
                task_id=task_id,
                agent_id=self.id,
                success=True,
                output=result,
                confidence=self._calculate_confidence(result),
                duration_ms=duration_ms,
                reasoning_path=thought.get("reasoning", []),
            )
            
            self.total_tasks_completed += 1
            self._update_performance(task_result)
            
            # Learn from experience
            await self._learn_from_experience(task, result, task_result)
            
            logger.info(f"Agent {self.name} completed task {task_id} in {duration_ms:.0f}ms")
            
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            task_result = TaskResult(
                task_id=task_id,
                agent_id=self.id,
                success=False,
                error=str(e),
                confidence=0.0,
                duration_ms=duration_ms,
            )
            
            self.total_tasks_failed += 1
            logger.error(f"Agent {self.name} failed task {task_id}: {e}")
        
        finally:
            self.status = AgentStatus.IDLE
            self.current_tasks.pop(task_id, None)
            self.task_history.append(task_result)
            
            # Publish completion event
            if self._event_bus:
                from ..core.event_bus import Event, EventType
                await self._event_bus.publish(Event(
                    type=EventType.AGENT_TASK_COMPLETED if task_result.success else EventType.AGENT_TASK_FAILED,
                    source=self.name,
                    payload={"task_id": task_id, "agent_id": self.id, "result": task_result.to_dict() if hasattr(task_result, 'to_dict') else str(task_result)},
                ))
        
        return task_result
    
    async def _execute_task(self, task: Dict[str, Any], thought: Dict[str, Any]) -> Any:
        """
        Default task execution - all agents can handle tasks.
        Override in specialized agents for custom behavior.
        """
        task_type = task.get("type", "unknown")
        objective = task.get("objective", "")
        
        return {
            "status": "completed",
            "agent": self.name,
            "role": self.role.value,
            "task_type": task_type,
            "objective": objective[:100],
            "result": f"Processed {task_type} task for objective: {objective[:50]}",
            "confidence": 0.85,
            "duration_ms": 0,
        }
    
    def _calculate_confidence(self, result: Any) -> float:
        """Calculate confidence in the result"""
        # Override in specialized agents
        return 0.8
    
    def _update_performance(self, result: TaskResult):
        """Update performance metrics"""
        # Update average duration
        total = self.total_tasks_completed + self.total_tasks_failed
        self.average_duration_ms = (
            (self.average_duration_ms * (total - 1) + result.duration_ms) / total
        )
        
        # Update performance score (weighted moving average)
        success_weight = 1.0 if result.success else 0.0
        self.performance_score = self.performance_score * 0.9 + success_weight * 0.1
        
        # Update confidence
        self.confidence_score = self.confidence_score * 0.95 + result.confidence * 0.05
    
    async def _learn_from_experience(self, task: Dict[str, Any], result: Any, task_result: TaskResult):
        """Learn from task execution"""
        experience = {
            "task": task,
            "result": str(result)[:500] if result else None,
            "success": task_result.success,
            "error": task_result.error,
            "duration_ms": task_result.duration_ms,
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        self.memory.experiences.append(experience)
        if len(self.memory.experiences) > self.memory.max_experiences:
            self.memory.experiences = self.memory.experiences[-self.memory.max_experiences:]
        
        # Extract learnings from failures
        if not task_result.success and task_result.error:
            learning = f"Failed: {task.get('type', 'unknown')} - {task_result.error}"
            self.memory.learnings.append(learning)
    
    async def reflect(self) -> Dict[str, Any]:
        """Self-reflection on performance and learnings"""
        reflection = {
            "agent_id": self.id,
            "agent_name": self.name,
            "role": self.role.value,
            "status": self.status.value,
            "performance": {
                "score": round(self.performance_score, 3),
                "confidence": round(self.confidence_score, 3),
                "tasks_completed": self.total_tasks_completed,
                "tasks_failed": self.total_tasks_failed,
                "average_duration_ms": round(self.average_duration_ms, 1),
            },
            "recent_experiences": self.memory.experiences[-5:] if self.memory.experiences else [],
            "learnings": self.memory.learnings[-10:],
            "skills": self.memory.skills,
            "timestamp": datetime.utcnow().isoformat(),
        }
        return reflection
    
    async def communicate(self, message: Dict[str, Any], target_agent: "BaseAgent") -> Dict[str, Any]:
        """Communicate with another agent"""
        if self._event_bus:
            from ..core.event_bus import Event, EventType
            await self._event_bus.publish(Event(
                type=EventType.AGENT_MESSAGE,
                source=self.name,
                payload={
                    "from": self.id,
                    "to": target_agent.id,
                    "message": message,
                },
            ))
        
        return {"status": "sent", "to": target_agent.name, "message": message}
    
    def get_status_summary(self) -> Dict[str, Any]:
        """Get agent status summary"""
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role.value,
            "status": self.status.value,
            "confidence": round(self.confidence_score, 3),
            "performance": round(self.performance_score, 3),
            "tasks_completed": self.total_tasks_completed,
            "tasks_failed": self.total_tasks_failed,
            "avg_duration_ms": round(self.average_duration_ms, 1),
            "capabilities": [c.value for c in self.capabilities],
            "active_tasks": len(self.current_tasks),
            "last_active": self.last_active,
        }
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role.value,
            "description": self.description,
            "goal": self.goal,
            "status": self.status.value,
            "capabilities": [c.value for c in self.capabilities],
            "confidence": round(self.confidence_score, 3),
            "performance": round(self.performance_score, 3),
            "total_tasks": self.total_tasks_completed + self.total_tasks_failed,
            "success_rate": round(
                self.total_tasks_completed / max(1, self.total_tasks_completed + self.total_tasks_failed) * 100, 1
            ),
            "created_at": self.created_at,
        }
    
    def set_event_bus(self, event_bus):
        """Set event bus reference"""
        self._event_bus = event_bus