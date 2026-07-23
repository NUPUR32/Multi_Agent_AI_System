"""
System Settings - Central Configuration
========================================
Environment-based configuration with validation
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, field
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()


@dataclass
class DatabaseConfig:
    postgres_url: str = field(default_factory=lambda: os.getenv("POSTGRES_URL", "postgresql://localhost:5432/nupur32"))
    mongodb_url: str = field(default_factory=lambda: os.getenv("MONGODB_URL", "mongodb://localhost:27017/nupur32"))
    redis_url: str = field(default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379"))
    neo4j_url: str = field(default_factory=lambda: os.getenv("NEO4J_URL", "bolt://localhost:7687"))
    elasticsearch_url: str = field(default_factory=lambda: os.getenv("ELASTICSEARCH_URL", "http://localhost:9200"))
    vector_db_url: str = field(default_factory=lambda: os.getenv("VECTOR_DB_URL", "http://localhost:6333"))
    sqlite_path: str = field(default_factory=lambda: os.getenv("SQLITE_PATH", "data/nupur32.db"))


@dataclass
class ModelProviderConfig:
    openai_api_key: Optional[str] = field(default_factory=lambda: os.getenv("OPENAI_API_KEY"))
    anthropic_api_key: Optional[str] = field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY"))
    google_api_key: Optional[str] = field(default_factory=lambda: os.getenv("GOOGLE_API_KEY"))
    xai_api_key: Optional[str] = field(default_factory=lambda: os.getenv("XAI_API_KEY"))
    deepseek_api_key: Optional[str] = field(default_factory=lambda: os.getenv("DEEPSEEK_API_KEY"))
    groq_api_key: Optional[str] = field(default_factory=lambda: os.getenv("GROQ_API_KEY"))
    together_api_key: Optional[str] = field(default_factory=lambda: os.getenv("TOGETHER_API_KEY"))
    huggingface_token: Optional[str] = field(default_factory=lambda: os.getenv("HUGGINGFACE_TOKEN"))
    
    default_model: str = field(default_factory=lambda: os.getenv("DEFAULT_MODEL", "gpt-4"))
    fallback_model: str = field(default_factory=lambda: os.getenv("FALLBACK_MODEL", "claude-3-opus"))
    embedding_model: str = field(default_factory=lambda: os.getenv("EMBEDDING_MODEL", "text-embedding-3-large"))


@dataclass
class SecurityConfig:
    master_key: Optional[str] = field(default_factory=lambda: os.getenv("NUPUR32_MASTER_KEY"))
    jwt_secret: Optional[str] = field(default_factory=lambda: os.getenv("JWT_SECRET"))
    encryption_enabled: bool = field(default_factory=lambda: os.getenv("ENCRYPTION_ENABLED", "true").lower() == "true")
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    max_request_size_mb: int = int(os.getenv("MAX_REQUEST_SIZE_MB", "100"))
    enable_audit_log: bool = field(default_factory=lambda: os.getenv("ENABLE_AUDIT_LOG", "true").lower() == "true")
    enable_prompt_injection_protection: bool = field(default_factory=lambda: os.getenv("PROMPT_INJECTION_PROTECTION", "true").lower() == "true")


@dataclass
class AgentSettings:
    max_concurrent_agents: int = 50
    agent_timeout_seconds: int = 300
    enable_heartbeat: bool = True
    heartbeat_interval: int = 30
    enable_reflection: bool = True
    enable_self_improvement: bool = True
    enable_learning: bool = True
    max_retries: int = 3
    enable_voting: bool = True
    enable_consensus: bool = True
    enable_delegation: bool = True


@dataclass
class MemorySettings:
    vector_dimension: int = 1536
    max_working_memory: int = 100
    max_short_term_memory: int = 1000
    max_long_term_memory: int = 100000
    memory_consolidation_interval: int = 3600
    memory_forgetting_threshold: float = 0.1
    enable_memory_compression: bool = True
    enable_memory_ranking: bool = True
    enable_memory_summarization: bool = True


@dataclass
class KnowledgeSettings:
    enable_rag: bool = True
    enable_knowledge_graph: bool = True
    enable_entity_linking: bool = True
    enable_citation: bool = True
    chunk_size: int = 512
    chunk_overlap: int = 64
    top_k_retrieval: int = 5
    similarity_threshold: float = 0.7
    enable_hybrid_search: bool = True
    enable_knowledge_verification: bool = True
    enable_automatic_update: bool = True


@dataclass
class WorkflowSettings:
    max_parallel_tasks: int = 10
    enable_dynamic_workflows: bool = True
    enable_workflow_persistence: bool = True
    enable_workflow_recovery: bool = True
    enable_workflow_optimization: bool = True
    max_workflow_depth: int = 10


@dataclass
class MonitoringSettings:
    enable_metrics: bool = True
    enable_tracing: bool = True
    enable_logging: bool = True
    metrics_port: int = 9090
    tracing_endpoint: Optional[str] = field(default_factory=lambda: os.getenv("TRACING_ENDPOINT"))
    enable_gpu_monitoring: bool = True
    enable_model_monitoring: bool = True
    enable_agent_monitoring: bool = True
    enable_alerts: bool = True


@dataclass
class SystemSettings:
    """Complete system configuration"""
    project_name: str = "NUPUR32 AI OS"
    version: str = "2035.0.0"
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")
    
    # Sub-configs
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    models: ModelProviderConfig = field(default_factory=ModelProviderConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    agents: AgentSettings = field(default_factory=AgentSettings)
    memory: MemorySettings = field(default_factory=MemorySettings)
    knowledge: KnowledgeSettings = field(default_factory=KnowledgeSettings)
    workflow: WorkflowSettings = field(default_factory=WorkflowSettings)
    monitoring: MonitoringSettings = field(default_factory=MonitoringSettings)
    
    # Paths
    data_dir: str = "data"
    logs_dir: str = "logs"
    output_dir: str = "output"
    plugins_dir: str = "plugins"
    models_dir: str = "models"
    
    def __post_init__(self):
        # Create directories
        for d in [self.data_dir, self.logs_dir, self.output_dir, self.plugins_dir, self.models_dir]:
            Path(d).mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        level = logging.DEBUG if self.debug else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            handlers=[
                logging.FileHandler(f"{self.logs_dir}/system.log", encoding="utf-8"),
                logging.StreamHandler()
            ]
        )
        logger.info(f"{self.project_name} v{self.version} initialized ({self.environment})")


# Global settings instance
_settings_instance: Optional[SystemSettings] = None


def load_settings() -> SystemSettings:
    """Load and cache system settings"""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = SystemSettings()
    return _settings_instance


def get_settings() -> SystemSettings:
    """Get current settings"""
    return load_settings()