"""Tests for Agent system"""

import pytest
import asyncio
from ai_ecosystem.agents.base_agent import BaseAgent, AgentRole, AgentCapability
from ai_ecosystem.agents.ceo_agent import CEOAgent
from ai_ecosystem.agents.agent_factory import AgentFactory, global_agent_factory


@pytest.mark.asyncio
async def test_base_agent_creation():
    agent = BaseAgent(
        name="Test-Agent",
        role=AgentRole.CODING,
        goal="Write clean code",
        capabilities=[AgentCapability.CODING, AgentCapability.TESTING],
    )
    
    assert agent.name == "Test-Agent"
    assert agent.role == AgentRole.CODING
    assert len(agent.capabilities) == 2


@pytest.mark.asyncio
async def test_agent_execute():
    agent = CEOAgent("Test-CEO")
    
    result = await agent.execute({
        "id": "test-1",
        "type": "strategic_planning",
        "objective": "Test objective",
    })
    
    assert result.success
    assert result.task_id == "test-1"
    assert result.confidence > 0


@pytest.mark.asyncio
async def test_agent_reflection():
    agent = CEOAgent("Test-CEO")
    
    reflection = await agent.reflect()
    assert "agent_name" in reflection
    assert reflection["agent_name"] == "Test-CEO"
    assert "performance" in reflection


@pytest.mark.asyncio
async def test_agent_status():
    agent = CEOAgent("Status-Agent")
    summary = agent.get_status_summary()
    
    assert summary["role"] == "ceo"
    assert summary["status"] == "idle"
    assert summary["tasks_completed"] == 0


@pytest.mark.asyncio
async def test_agent_factory():
    factory = AgentFactory()
    agent = factory.create_agent(AgentRole.CODING)
    
    assert agent is not None
    assert agent.role == AgentRole.CODING


@pytest.mark.asyncio
async def test_agent_factory_create_all():
    factory = AgentFactory()
    agents = factory.create_all_agents()
    
    assert len(agents) > 0
    assert len(agents) == len(AgentRole)


@pytest.mark.asyncio
async def test_agent_performance_tracking():
    agent = CEOAgent("Perf-Agent")
    
    await agent.execute({"id": "t1", "type": "strategic_planning", "objective": "Task 1"})
    await agent.execute({"id": "t2", "type": "strategic_planning", "objective": "Task 2"})
    
    summary = agent.get_status_summary()
    assert summary["tasks_completed"] == 2
    assert summary["performance"] > 0