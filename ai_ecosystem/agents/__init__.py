"""
Agent Ecosystem - 40+ Specialized AI Agents
============================================
Each agent has goals, personality, capabilities, memory, reflection, and performance metrics
All agents are dynamically created by AgentFactory from configuration
"""

from .base_agent import BaseAgent, AgentRole, AgentCapability, AgentStatus, AgentPersonality, TaskResult
from .ceo_agent import CEOAgent
from .agent_factory import AgentFactory, global_agent_factory, AGENT_CONFIGS

__all__ = [
    "BaseAgent", "AgentRole", "AgentCapability", "AgentStatus", "AgentPersonality", "TaskResult",
    "CEOAgent",
    "AgentFactory", "global_agent_factory", "AGENT_CONFIGS",
]