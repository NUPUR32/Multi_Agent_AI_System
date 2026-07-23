"""
Agent Factory - Creates and Configures All 40+ Agents
=======================================================
Dynamic agent creation with personality, capabilities, and model assignment
"""

import logging
from typing import Any, Dict, List, Optional, Type
from .base_agent import BaseAgent, AgentRole, AgentCapability, AgentPersonality

logger = logging.getLogger(__name__)


# Agent configuration registry
AGENT_CONFIGS: Dict[AgentRole, Dict[str, Any]] = {
    AgentRole.CEO: {
        "name": "CEO-Agent",
        "description": "Strategic leader and decision maker for the entire AI ecosystem",
        "goal": "Maximize system effectiveness, drive innovation, and ensure mission success",
        "personality": AgentPersonality(openness=0.9, conscientiousness=0.9, extraversion=0.7, agreeableness=0.5, neuroticism=0.2, risk_tolerance=0.7, creativity=0.9, analytical=0.9, assertiveness=0.9, empathy=0.6),
        "capabilities": [AgentCapability.ORCHESTRATION, AgentCapability.DECISION_MAKING, AgentCapability.PLANNING, AgentCapability.DELEGATION, AgentCapability.COMMUNICATION, AgentCapability.RISK_ASSESSMENT, AgentCapability.REASONING],
        "model": "gpt-4o",
    },
    AgentRole.PROJECT_MANAGER: {
        "name": "ProjectManager-Agent",
        "description": "Manages projects, timelines, resources, and coordinates team efforts",
        "goal": "Deliver projects on time, within scope, and with highest quality",
        "personality": AgentPersonality(openness=0.6, conscientiousness=0.95, extraversion=0.6, agreeableness=0.7, neuroticism=0.3, risk_tolerance=0.4, creativity=0.5, analytical=0.85, assertiveness=0.7, empathy=0.7),
        "capabilities": [AgentCapability.PLANNING, AgentCapability.ORCHESTRATION, AgentCapability.DELEGATION, AgentCapability.COMMUNICATION, AgentCapability.DECISION_MAKING],
        "model": "gpt-4o",
    },
    AgentRole.ARCHITECT: {
        "name": "Architect-Agent",
        "description": "Designs system architecture, makes technical decisions, ensures scalability",
        "goal": "Create robust, scalable, and maintainable system architectures",
        "personality": AgentPersonality(openness=0.8, conscientiousness=0.9, extraversion=0.4, agreeableness=0.5, neuroticism=0.2, risk_tolerance=0.5, creativity=0.8, analytical=0.95, assertiveness=0.7, empathy=0.4),
        "capabilities": [AgentCapability.PLANNING, AgentCapability.REASONING, AgentCapability.DECISION_MAKING, AgentCapability.RISK_ASSESSMENT],
        "model": "claude-3.5-sonnet",
    },
    AgentRole.PLANNER: {
        "name": "Planner-Agent",
        "description": "Breaks down complex tasks into actionable plans with timelines",
        "goal": "Create detailed, executable plans from high-level objectives",
        "personality": AgentPersonality(openness=0.5, conscientiousness=0.95, extraversion=0.3, agreeableness=0.6, neuroticism=0.3, risk_tolerance=0.3, creativity=0.4, analytical=0.9, assertiveness=0.5, empathy=0.5),
        "capabilities": [AgentCapability.PLANNING, AgentCapability.REASONING, AgentCapability.ORCHESTRATION],
        "model": "gpt-4o",
    },
    AgentRole.RESEARCHER: {
        "name": "Research-Agent",
        "description": "Conducts deep research, analyzes information, and provides insights",
        "goal": "Find accurate, comprehensive, and up-to-date information on any topic",
        "personality": AgentPersonality(openness=0.9, conscientiousness=0.85, extraversion=0.3, agreeableness=0.6, neuroticism=0.3, risk_tolerance=0.3, creativity=0.7, analytical=0.9, assertiveness=0.4, empathy=0.5),
        "capabilities": [AgentCapability.RESEARCH, AgentCapability.DATA_ANALYSIS, AgentCapability.REASONING],
        "model": "gpt-4o",
    },
    AgentRole.INTERNET: {
        "name": "Internet-Agent",
        "description": "Searches the web, scrapes websites, and retrieves online information",
        "goal": "Efficiently retrieve and process information from the internet",
        "personality": AgentPersonality(openness=0.7, conscientiousness=0.8, extraversion=0.4, agreeableness=0.5, neuroticism=0.3, risk_tolerance=0.5, creativity=0.5, analytical=0.8, assertiveness=0.5, empathy=0.4),
        "capabilities": [AgentCapability.RESEARCH, AgentCapability.BROWSER_AUTOMATION],
        "model": "gpt-4o-mini",
    },
    AgentRole.REASONING: {
        "name": "Reasoning-Agent",
        "description": "Performs complex reasoning, logical analysis, and problem solving",
        "goal": "Solve complex problems through systematic reasoning and analysis",
        "personality": AgentPersonality(openness=0.7, conscientiousness=0.9, extraversion=0.2, agreeableness=0.4, neuroticism=0.2, risk_tolerance=0.3, creativity=0.6, analytical=0.95, assertiveness=0.5, empathy=0.3),
        "capabilities": [AgentCapability.REASONING, AgentCapability.DECISION_MAKING, AgentCapability.RISK_ASSESSMENT],
        "model": "o1-preview",
    },
    AgentRole.CODING: {
        "name": "Coding-Agent",
        "description": "Writes, modifies, and optimizes code across multiple languages",
        "goal": "Write clean, efficient, and well-tested code",
        "personality": AgentPersonality(openness=0.6, conscientiousness=0.9, extraversion=0.3, agreeableness=0.5, neuroticism=0.3, risk_tolerance=0.4, creativity=0.7, analytical=0.9, assertiveness=0.5, empathy=0.4),
        "capabilities": [AgentCapability.CODING, AgentCapability.DEBUGGING, AgentCapability.TESTING],
        "model": "claude-3.5-sonnet",
    },
    AgentRole.REVIEWER: {
        "name": "Reviewer-Agent",
        "description": "Reviews code, documents, and outputs for quality and correctness",
        "goal": "Ensure all outputs meet quality standards and are error-free",
        "personality": AgentPersonality(openness=0.4, conscientiousness=0.95, extraversion=0.2, agreeableness=0.4, neuroticism=0.4, risk_tolerance=0.2, creativity=0.3, analytical=0.95, assertiveness=0.6, empathy=0.3),
        "capabilities": [AgentCapability.REVIEWING, AgentCapability.QUALITY_CONTROL, AgentCapability.TESTING],
        "model": "gpt-4o",
    },
    AgentRole.DEBUGGER: {
        "name": "Debugger-Agent",
        "description": "Identifies and fixes bugs in code and systems",
        "goal": "Rapidly identify and resolve software defects",
        "personality": AgentPersonality(openness=0.5, conscientiousness=0.9, extraversion=0.3, agreeableness=0.4, neuroticism=0.3, risk_tolerance=0.3, creativity=0.6, analytical=0.95, assertiveness=0.5, empathy=0.3),
        "capabilities": [AgentCapability.DEBUGGING, AgentCapability.CODING, AgentCapability.TESTING],
        "model": "claude-3.5-sonnet",
    },
    AgentRole.TESTING: {
        "name": "Testing-Agent",
        "description": "Creates and executes comprehensive test suites",
        "goal": "Ensure 100% test coverage and zero production defects",
        "personality": AgentPersonality(openness=0.4, conscientiousness=0.95, extraversion=0.2, agreeableness=0.5, neuroticism=0.4, risk_tolerance=0.2, creativity=0.3, analytical=0.9, assertiveness=0.4, empathy=0.3),
        "capabilities": [AgentCapability.TESTING, AgentCapability.CODING, AgentCapability.QUALITY_CONTROL],
        "model": "gpt-4o",
    },
    AgentRole.DOCUMENTATION: {
        "name": "Documentation-Agent",
        "description": "Creates and maintains comprehensive documentation",
        "goal": "Produce clear, comprehensive, and well-structured documentation",
        "personality": AgentPersonality(openness=0.6, conscientiousness=0.9, extraversion=0.3, agreeableness=0.7, neuroticism=0.2, risk_tolerance=0.2, creativity=0.5, analytical=0.8, assertiveness=0.3, empathy=0.6),
        "capabilities": [AgentCapability.DOCUMENTATION, AgentCapability.COMMUNICATION, AgentCapability.QUALITY_CONTROL],
        "model": "gpt-4o",
    },
    AgentRole.SECURITY: {
        "name": "Security-Agent",
        "description": "Monitors and enforces security policies, detects threats",
        "goal": "Maintain zero-trust security and protect against all threats",
        "personality": AgentPersonality(openness=0.4, conscientiousness=0.95, extraversion=0.2, agreeableness=0.3, neuroticism=0.5, risk_tolerance=0.1, creativity=0.4, analytical=0.95, assertiveness=0.8, empathy=0.2),
        "capabilities": [AgentCapability.SECURITY, AgentCapability.RISK_ASSESSMENT, AgentCapability.MONITORING],
        "model": "gpt-4o",
    },
    AgentRole.DEVOPS: {
        "name": "DevOps-Agent",
        "description": "Manages CI/CD, deployment, infrastructure, and operations",
        "goal": "Ensure smooth, automated, and reliable deployment pipelines",
        "personality": AgentPersonality(openness=0.6, conscientiousness=0.9, extraversion=0.4, agreeableness=0.5, neuroticism=0.3, risk_tolerance=0.4, creativity=0.5, analytical=0.85, assertiveness=0.6, empathy=0.4),
        "capabilities": [AgentCapability.DEPLOYMENT, AgentCapability.MONITORING, AgentCapability.SECURITY],
        "model": "gpt-4o",
    },
    AgentRole.CLOUD: {
        "name": "Cloud-Agent",
        "description": "Manages cloud infrastructure across AWS, Azure, GCP",
        "goal": "Optimize cloud resources for cost, performance, and reliability",
        "personality": AgentPersonality(openness=0.7, conscientiousness=0.85, extraversion=0.4, agreeableness=0.5, neuroticism=0.3, risk_tolerance=0.5, creativity=0.6, analytical=0.85, assertiveness=0.6, empathy=0.4),
        "capabilities": [AgentCapability.DEPLOYMENT, AgentCapability.MONITORING, AgentCapability.OPTIMIZATION],
        "model": "gpt-4o",
    },
    AgentRole.DATA_ENGINEER: {
        "name": "DataEngineer-Agent",
        "description": "Builds and maintains data pipelines, ETL processes, and databases",
        "goal": "Create efficient, reliable data infrastructure",
        "personality": AgentPersonality(openness=0.6, conscientiousness=0.9, extraversion=0.3, agreeableness=0.5, neuroticism=0.3, risk_tolerance=0.3, creativity=0.5, analytical=0.9, assertiveness=0.5, empathy=0.4),
        "capabilities": [AgentCapability.DATA_ANALYSIS, AgentCapability.CODING, AgentCapability.OPTIMIZATION],
        "model": "gpt-4o",
    },
    AgentRole.ML_ENGINEER: {
        "name": "MLEngineer-Agent",
        "description": "Trains, evaluates, and deploys machine learning models",
        "goal": "Build and deploy state-of-the-art ML models",
        "personality": AgentPersonality(openness=0.8, conscientiousness=0.85, extraversion=0.3, agreeableness=0.5, neuroticism=0.3, risk_tolerance=0.5, creativity=0.8, analytical=0.9, assertiveness=0.5, empathy=0.4),
        "capabilities": [AgentCapability.ML_TRAINING, AgentCapability.DATA_ANALYSIS, AgentCapability.CODING],
        "model": "claude-3.5-sonnet",
    },
    AgentRole.VISION: {
        "name": "Vision-Agent",
        "description": "Processes and analyzes images and visual data",
        "goal": "Extract meaningful information from visual data",
        "personality": AgentPersonality(openness=0.7, conscientiousness=0.8, extraversion=0.3, agreeableness=0.6, neuroticism=0.3, risk_tolerance=0.4, creativity=0.6, analytical=0.85, assertiveness=0.4, empathy=0.5),
        "capabilities": [AgentCapability.VISION_PROCESSING, AgentCapability.DATA_ANALYSIS],
        "model": "gpt-4o",
    },
    AgentRole.SPEECH: {
        "name": "Speech-Agent",
        "description": "Handles speech recognition, synthesis, and audio processing",
        "goal": "Provide accurate speech processing and natural voice interaction",
        "personality": AgentPersonality(openness=0.6, conscientiousness=0.8, extraversion=0.6, agreeableness=0.7, neuroticism=0.3, risk_tolerance=0.3, creativity=0.5, analytical=0.7, assertiveness=0.4, empathy=0.7),
        "capabilities": [AgentCapability.SPEECH_PROCESSING, AgentCapability.COMMUNICATION],
        "model": "gpt-4o",
    },
    AgentRole.IMAGE: {
        "name": "Image-Agent",
        "description": "Generates and edits images using AI",
        "goal": "Create high-quality images and visual content",
        "personality": AgentPersonality(openness=0.9, conscientiousness=0.7, extraversion=0.5, agreeableness=0.6, neuroticism=0.3, risk_tolerance=0.6, creativity=0.95, analytical=0.5, assertiveness=0.5, empathy=0.6),
        "capabilities": [AgentCapability.IMAGE_GENERATION, AgentCapability.VISION_PROCESSING],
        "model": "gpt-4o",
    },
    AgentRole.VIDEO: {
        "name": "Video-Agent",
        "description": "Processes, analyzes, and generates video content",
        "goal": "Create and analyze video content effectively",
        "personality": AgentPersonality(openness=0.8, conscientiousness=0.75, extraversion=0.5, agreeableness=0.6, neuroticism=0.3, risk_tolerance=0.5, creativity=0.85, analytical=0.7, assertiveness=0.5, empathy=0.5),
        "capabilities": [AgentCapability.VIDEO_PROCESSING, AgentCapability.VISION_PROCESSING],
        "model": "gpt-4o",
    },
    AgentRole.BROWSER: {
        "name": "Browser-Agent",
        "description": "Automates web browsers for testing and data collection",
        "goal": "Automate browser interactions efficiently and reliably",
        "personality": AgentPersonality(openness=0.5, conscientiousness=0.85, extraversion=0.3, agreeableness=0.5, neuroticism=0.3, risk_tolerance=0.4, creativity=0.4, analytical=0.85, assertiveness=0.5, empathy=0.3),
        "capabilities": [AgentCapability.BROWSER_AUTOMATION, AgentCapability.TESTING],
        "model": "gpt-4o-mini",
    },
    AgentRole.COMPUTER_CONTROL: {
        "name": "ComputerControl-Agent",
        "description": "Controls desktop environment, GUI automation, and system operations",
        "goal": "Automate computer operations and GUI interactions",
        "personality": AgentPersonality(openness=0.5, conscientiousness=0.85, extraversion=0.3, agreeableness=0.4, neuroticism=0.3, risk_tolerance=0.4, creativity=0.5, analytical=0.85, assertiveness=0.5, empathy=0.3),
        "capabilities": [AgentCapability.COMPUTER_CONTROL, AgentCapability.BROWSER_AUTOMATION],
        "model": "gpt-4o",
    },
    AgentRole.EMAIL: {
        "name": "Email-Agent",
        "description": "Manages email communications, drafting, and organization",
        "goal": "Handle email communications efficiently and professionally",
        "personality": AgentPersonality(openness=0.5, conscientiousness=0.9, extraversion=0.5, agreeableness=0.7, neuroticism=0.3, risk_tolerance=0.2, creativity=0.4, analytical=0.7, assertiveness=0.4, empathy=0.7),
        "capabilities": [AgentCapability.EMAIL, AgentCapability.COMMUNICATION, AgentCapability.DOCUMENTATION],
        "model": "gpt-4o-mini",
    },
    AgentRole.CALENDAR: {
        "name": "Calendar-Agent",
        "description": "Manages schedules, appointments, and time optimization",
        "goal": "Optimize scheduling and time management",
        "personality": AgentPersonality(openness=0.4, conscientiousness=0.95, extraversion=0.4, agreeableness=0.6, neuroticism=0.3, risk_tolerance=0.2, creativity=0.3, analytical=0.85, assertiveness=0.4, empathy=0.5),
        "capabilities": [AgentCapability.CALENDAR, AgentCapability.PLANNING, AgentCapability.OPTIMIZATION],
        "model": "gpt-4o-mini",
    },
    AgentRole.FINANCE: {
        "name": "Finance-Agent",
        "description": "Handles financial analysis, budgeting, and reporting",
        "goal": "Provide accurate financial insights and optimize resource allocation",
        "personality": AgentPersonality(openness=0.4, conscientiousness=0.95, extraversion=0.3, agreeableness=0.5, neuroticism=0.4, risk_tolerance=0.2, creativity=0.3, analytical=0.95, assertiveness=0.5, empathy=0.3),
        "capabilities": [AgentCapability.FINANCE, AgentCapability.DATA_ANALYSIS, AgentCapability.RISK_ASSESSMENT],
        "model": "gpt-4o",
    },
    AgentRole.LEGAL: {
        "name": "Legal-Agent",
        "description": "Reviews legal documents, ensures compliance, manages risk",
        "goal": "Ensure legal compliance and minimize legal risk",
        "personality": AgentPersonality(openness=0.3, conscientiousness=0.95, extraversion=0.2, agreeableness=0.4, neuroticism=0.5, risk_tolerance=0.1, creativity=0.2, analytical=0.95, assertiveness=0.6, empathy=0.3),
        "capabilities": [AgentCapability.LEGAL, AgentCapability.RISK_ASSESSMENT, AgentCapability.QUALITY_CONTROL],
        "model": "gpt-4o",
    },
    AgentRole.ANALYTICS: {
        "name": "Analytics-Agent",
        "description": "Performs data analysis, creates reports, and generates insights",
        "goal": "Transform data into actionable insights and beautiful visualizations",
        "personality": AgentPersonality(openness=0.7, conscientiousness=0.85, extraversion=0.4, agreeableness=0.6, neuroticism=0.3, risk_tolerance=0.4, creativity=0.7, analytical=0.9, assertiveness=0.5, empathy=0.5),
        "capabilities": [AgentCapability.DATA_ANALYSIS, AgentCapability.ANALYTICS, AgentCapability.DOCUMENTATION],
        "model": "gpt-4o",
    },
    AgentRole.MEMORY: {
        "name": "Memory-Agent",
        "description": "Manages the memory system, storage, retrieval, and consolidation",
        "goal": "Maintain an efficient, accurate, and comprehensive memory system",
        "personality": AgentPersonality(openness=0.5, conscientiousness=0.9, extraversion=0.2, agreeableness=0.5, neuroticism=0.3, risk_tolerance=0.2, creativity=0.3, analytical=0.9, assertiveness=0.3, empathy=0.4),
        "capabilities": [AgentCapability.MEMORY_MANAGEMENT, AgentCapability.KNOWLEDGE_MANAGEMENT, AgentCapability.OPTIMIZATION],
        "model": "gpt-4o",
    },
    AgentRole.KNOWLEDGE: {
        "name": "Knowledge-Agent",
        "description": "Manages knowledge base, RAG, and information retrieval",
        "goal": "Build and maintain a comprehensive, accurate knowledge system",
        "personality": AgentPersonality(openness=0.7, conscientiousness=0.85, extraversion=0.3, agreeableness=0.6, neuroticism=0.3, risk_tolerance=0.3, creativity=0.5, analytical=0.9, assertiveness=0.4, empathy=0.5),
        "capabilities": [AgentCapability.KNOWLEDGE_MANAGEMENT, AgentCapability.RESEARCH, AgentCapability.DATA_ANALYSIS],
        "model": "gpt-4o",
    },
    AgentRole.REFLECTION: {
        "name": "Reflection-Agent",
        "description": "Analyzes past actions, learns from mistakes, suggests improvements",
        "goal": "Continuously improve system performance through self-reflection",
        "personality": AgentPersonality(openness=0.8, conscientiousness=0.85, extraversion=0.3, agreeableness=0.6, neuroticism=0.4, risk_tolerance=0.3, creativity=0.7, analytical=0.9, assertiveness=0.4, empathy=0.5),
        "capabilities": [AgentCapability.REFLECTION, AgentCapability.LEARNING, AgentCapability.REASONING],
        "model": "gpt-4o",
    },
    AgentRole.LEARNING: {
        "name": "Learning-Agent",
        "description": "Manages continuous learning, skill acquisition, and knowledge evolution",
        "goal": "Enable continuous improvement and skill development across the system",
        "personality": AgentPersonality(openness=0.9, conscientiousness=0.8, extraversion=0.5, agreeableness=0.7, neuroticism=0.2, risk_tolerance=0.6, creativity=0.8, analytical=0.8, assertiveness=0.5, empathy=0.6),
        "capabilities": [AgentCapability.LEARNING, AgentCapability.REFLECTION, AgentCapability.OPTIMIZATION],
        "model": "gpt-4o",
    },
    AgentRole.OPTIMIZATION: {
        "name": "Optimization-Agent",
        "description": "Optimizes system performance, costs, and resource utilization",
        "goal": "Maximize system efficiency and minimize operational costs",
        "personality": AgentPersonality(openness=0.6, conscientiousness=0.9, extraversion=0.3, agreeableness=0.5, neuroticism=0.3, risk_tolerance=0.4, creativity=0.6, analytical=0.95, assertiveness=0.6, empathy=0.3),
        "capabilities": [AgentCapability.OPTIMIZATION, AgentCapability.ANALYTICS, AgentCapability.DECISION_MAKING],
        "model": "gpt-4o",
    },
    AgentRole.MONITORING: {
        "name": "Monitoring-Agent",
        "description": "Monitors system health, performance metrics, and alerts",
        "goal": "Ensure 99.99% uptime and immediate issue detection",
        "personality": AgentPersonality(openness=0.4, conscientiousness=0.95, extraversion=0.2, agreeableness=0.4, neuroticism=0.5, risk_tolerance=0.1, creativity=0.3, analytical=0.95, assertiveness=0.6, empathy=0.2),
        "capabilities": [AgentCapability.MONITORING, AgentCapability.ANALYTICS, AgentCapability.SECURITY],
        "model": "gpt-4o-mini",
    },
    AgentRole.SUPERVISOR: {
        "name": "Supervisor-Agent",
        "description": "Supervises agent activities, ensures coordination, resolves conflicts",
        "goal": "Maintain harmonious and productive agent collaboration",
        "personality": AgentPersonality(openness=0.6, conscientiousness=0.9, extraversion=0.6, agreeableness=0.7, neuroticism=0.3, risk_tolerance=0.4, creativity=0.5, analytical=0.85, assertiveness=0.7, empathy=0.7),
        "capabilities": [AgentCapability.ORCHESTRATION, AgentCapability.COMMUNICATION, AgentCapability.DECISION_MAKING, AgentCapability.QUALITY_CONTROL],
        "model": "gpt-4o",
    },
    AgentRole.CONSENSUS: {
        "name": "Consensus-Agent",
        "description": "Facilitates agreement among agents through voting and negotiation",
        "goal": "Achieve optimal decisions through collaborative consensus",
        "personality": AgentPersonality(openness=0.7, conscientiousness=0.85, extraversion=0.6, agreeableness=0.8, neuroticism=0.2, risk_tolerance=0.4, creativity=0.6, analytical=0.8, assertiveness=0.5, empathy=0.8),
        "capabilities": [AgentCapability.CONSENSUS_BUILDING, AgentCapability.COMMUNICATION, AgentCapability.DECISION_MAKING],
        "model": "gpt-4o",
    },
    AgentRole.QUALITY_ASSURANCE: {
        "name": "QualityAssurance-Agent",
        "description": "Ensures all outputs meet quality standards and best practices",
        "goal": "Maintain highest quality standards across all system outputs",
        "personality": AgentPersonality(openness=0.4, conscientiousness=0.95, extraversion=0.2, agreeableness=0.4, neuroticism=0.5, risk_tolerance=0.1, creativity=0.3, analytical=0.95, assertiveness=0.7, empathy=0.3),
        "capabilities": [AgentCapability.QUALITY_CONTROL, AgentCapability.TESTING, AgentCapability.REVIEWING],
        "model": "gpt-4o",
    },
    AgentRole.ETHICS: {
        "name": "Ethics-Agent",
        "description": "Ensures ethical AI operation, fairness, and responsible behavior",
        "goal": "Ensure all system actions are ethical, fair, and responsible",
        "personality": AgentPersonality(openness=0.8, conscientiousness=0.9, extraversion=0.4, agreeableness=0.8, neuroticism=0.4, risk_tolerance=0.2, creativity=0.5, analytical=0.85, assertiveness=0.6, empathy=0.9),
        "capabilities": [AgentCapability.ETHICS, AgentCapability.RISK_ASSESSMENT, AgentCapability.QUALITY_CONTROL],
        "model": "gpt-4o",
    },
    AgentRole.RISK_ANALYSIS: {
        "name": "RiskAnalysis-Agent",
        "description": "Identifies, assesses, and mitigates risks across all operations",
        "goal": "Proactively identify and mitigate all potential risks",
        "personality": AgentPersonality(openness=0.5, conscientiousness=0.9, extraversion=0.2, agreeableness=0.4, neuroticism=0.6, risk_tolerance=0.1, creativity=0.4, analytical=0.95, assertiveness=0.6, empathy=0.3),
        "capabilities": [AgentCapability.RISK_ASSESSMENT, AgentCapability.SECURITY, AgentCapability.DECISION_MAKING],
        "model": "gpt-4o",
    },
    AgentRole.DECISION: {
        "name": "Decision-Agent",
        "description": "Makes data-driven decisions using multiple reasoning frameworks",
        "goal": "Make optimal decisions using comprehensive analysis and scoring",
        "personality": AgentPersonality(openness=0.6, conscientiousness=0.9, extraversion=0.3, agreeableness=0.5, neuroticism=0.3, risk_tolerance=0.4, creativity=0.5, analytical=0.95, assertiveness=0.6, empathy=0.4),
        "capabilities": [AgentCapability.DECISION_MAKING, AgentCapability.REASONING, AgentCapability.RISK_ASSESSMENT],
        "model": "o1-preview",
    },
    AgentRole.EXECUTION: {
        "name": "Execution-Agent",
        "description": "Executes tasks, runs commands, and implements solutions",
        "goal": "Execute tasks efficiently and accurately",
        "personality": AgentPersonality(openness=0.5, conscientiousness=0.9, extraversion=0.4, agreeableness=0.6, neuroticism=0.3, risk_tolerance=0.4, creativity=0.4, analytical=0.85, assertiveness=0.6, empathy=0.4),
        "capabilities": [AgentCapability.CODING, AgentCapability.DEPLOYMENT, AgentCapability.ORCHESTRATION],
        "model": "gpt-4o",
    },
    AgentRole.EMERGENCY_RECOVERY: {
        "name": "EmergencyRecovery-Agent",
        "description": "Handles system failures, recovery procedures, and disaster recovery",
        "goal": "Minimize downtime and ensure rapid recovery from any failure",
        "personality": AgentPersonality(openness=0.5, conscientiousness=0.95, extraversion=0.3, agreeableness=0.4, neuroticism=0.5, risk_tolerance=0.2, creativity=0.5, analytical=0.9, assertiveness=0.8, empathy=0.3),
        "capabilities": [AgentCapability.EMERGENCY_RECOVERY, AgentCapability.MONITORING, AgentCapability.SECURITY],
        "model": "gpt-4o",
    },
}


class AgentFactory:
    """
    Factory for creating and configuring all agents in the ecosystem
    """
    
    def __init__(self):
        self._agent_classes: Dict[AgentRole, Type[BaseAgent]] = {}
        self._created_agents: Dict[str, BaseAgent] = {}
        logger.info("AgentFactory initialized")
    
    def register_agent_class(self, role: AgentRole, agent_class: Type[BaseAgent]):
        """Register a custom agent class for a role"""
        self._agent_classes[role] = agent_class
        logger.debug(f"Registered agent class for {role.value}: {agent_class.__name__}")
    
    def create_agent(self, role: AgentRole, custom_name: Optional[str] = None) -> BaseAgent:
        """Create an agent for the given role"""
        config = AGENT_CONFIGS.get(role)
        if not config:
            raise ValueError(f"No configuration found for role: {role.value}")
        
        # Check for custom class
        agent_class = self._agent_classes.get(role, BaseAgent)
        
        name = custom_name or config["name"]
        
        agent = agent_class(
            name=name,
            role=role,
            description=config["description"],
            goal=config["goal"],
            personality=config["personality"],
            capabilities=config["capabilities"],
            model_name=config["model"],
        )
        
        self._created_agents[agent.id] = agent
        logger.info(f"Created agent: {name} ({role.value})")
        return agent
    
    def create_all_agents(self) -> Dict[str, BaseAgent]:
        """Create all 40+ agents"""
        agents = {}
        for role in AgentRole:
            try:
                agent = self.create_agent(role)
                agents[role.value] = agent
            except Exception as e:
                logger.error(f"Failed to create agent for {role.value}: {e}")
        
        logger.info(f"Created {len(agents)}/{len(AgentRole)} agents")
        return agents
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        return self._created_agents.get(agent_id)
    
    def get_agent_by_role(self, role: AgentRole) -> Optional[BaseAgent]:
        for agent in self._created_agents.values():
            if agent.role == role:
                return agent
        return None
    
    def get_agents_by_capability(self, capability: AgentCapability) -> List[BaseAgent]:
        return [a for a in self._created_agents.values() if capability in a.capabilities]
    
    def get_all_agents(self) -> List[BaseAgent]:
        return list(self._created_agents.values())
    
    def get_agent_count(self) -> int:
        return len(self._created_agents)


# Global factory
global_agent_factory = AgentFactory()