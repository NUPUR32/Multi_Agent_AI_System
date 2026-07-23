"""
Model Configuration & Registry
================================
Multi-model support with automatic routing, cost optimization, and fallback
"""

import logging
from typing import Any, Callable, Dict, List, Optional, Type
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class ModelProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    XAI = "xai"
    DEEPSEEK = "deepseek"
    MISTRAL = "mistral"
    GROQ = "groq"
    TOGETHER = "together"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    LOCAL = "local"


class ModelCapability(Enum):
    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    REASONING = "reasoning"
    ANALYSIS = "analysis"
    CREATIVE = "creative"
    VISION = "vision"
    EMBEDDING = "embedding"
    CLASSIFICATION = "classification"
    SUMMARIZATION = "summarization"
    TRANSLATION = "translation"


@dataclass
class ModelConfig:
    """Configuration for a specific model"""
    name: str
    provider: ModelProvider
    model_id: str
    capabilities: List[ModelCapability] = field(default_factory=list)
    max_tokens: int = 4096
    temperature: float = 0.7
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    latency_p95_ms: float = 2000
    is_default: bool = False
    is_fallback: bool = False
    requires_api_key: bool = True
    supports_streaming: bool = True
    supports_functions: bool = True
    supports_vision: bool = False
    
    def estimate_cost(self, input_tokens: int, output_tokens: int) -> float:
        return (input_tokens / 1000 * self.cost_per_1k_input +
                output_tokens / 1000 * self.cost_per_1k_output)


class ModelRegistry:
    """
    Central model registry with intelligent routing
    """
    
    def __init__(self):
        self._models: Dict[str, ModelConfig] = {}
        self._provider_models: Dict[str, List[str]] = {}
        self._capability_models: Dict[str, List[str]] = {}
        self._initialized = False
        logger.info("ModelRegistry initialized")
    
    def register(self, config: ModelConfig):
        """Register a model"""
        self._models[config.name] = config
        
        # Index by provider
        provider_key = config.provider.value
        if provider_key not in self._provider_models:
            self._provider_models[provider_key] = []
        self._provider_models[provider_key].append(config.name)
        
        # Index by capability
        for cap in config.capabilities:
            cap_key = cap.value
            if cap_key not in self._capability_models:
                self._capability_models[cap_key] = []
            self._capability_models[cap_key].append(config.name)
        
        logger.debug(f"Registered model: {config.name} ({config.provider.value})")
    
    def initialize_defaults(self):
        """Register default model configurations"""
        if self._initialized:
            return
        
        # OpenAI Models
        self.register(ModelConfig(
            name="gpt-4o", provider=ModelProvider.OPENAI, model_id="gpt-4o",
            capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.REASONING, 
                         ModelCapability.CODE_GENERATION, ModelCapability.VISION],
            max_tokens=128000, cost_per_1k_input=0.01, cost_per_1k_output=0.03,
            is_default=True, supports_vision=True,
        ))
        self.register(ModelConfig(
            name="gpt-4o-mini", provider=ModelProvider.OPENAI, model_id="gpt-4o-mini",
            capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.REASONING, ModelCapability.CODE_GENERATION],
            max_tokens=128000, cost_per_1k_input=0.0015, cost_per_1k_output=0.006,
        ))
        self.register(ModelConfig(
            name="o1-preview", provider=ModelProvider.OPENAI, model_id="o1-preview",
            capabilities=[ModelCapability.REASONING, ModelCapability.ANALYSIS],
            max_tokens=128000, cost_per_1k_input=0.015, cost_per_1k_output=0.06,
        ))
        self.register(ModelConfig(
            name="text-embedding-3-large", provider=ModelProvider.OPENAI, model_id="text-embedding-3-large",
            capabilities=[ModelCapability.EMBEDDING], max_tokens=8192, cost_per_1k_input=0.00013,
        ))
        
        # Anthropic Models
        self.register(ModelConfig(
            name="claude-3.5-sonnet", provider=ModelProvider.ANTHROPIC, model_id="claude-3-5-sonnet-20241022",
            capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.REASONING, 
                         ModelCapability.CODE_GENERATION, ModelCapability.ANALYSIS, ModelCapability.VISION],
            max_tokens=200000, cost_per_1k_input=0.003, cost_per_1k_output=0.015,
            is_fallback=True, supports_vision=True,
        ))
        self.register(ModelConfig(
            name="claude-3-opus", provider=ModelProvider.ANTHROPIC, model_id="claude-3-opus-20240229",
            capabilities=[ModelCapability.REASONING, ModelCapability.ANALYSIS, ModelCapability.CREATIVE],
            max_tokens=200000, cost_per_1k_input=0.015, cost_per_1k_output=0.075,
        ))
        
        # Google Models
        self.register(ModelConfig(
            name="gemini-1.5-pro", provider=ModelProvider.GOOGLE, model_id="gemini-1.5-pro",
            capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.REASONING, 
                         ModelCapability.CODE_GENERATION, ModelCapability.VISION],
            max_tokens=1000000, cost_per_1k_input=0.00125, cost_per_1k_output=0.005,
            supports_vision=True,
        ))
        
        # XAI (Grok) Models
        self.register(ModelConfig(
            name="grok-3", provider=ModelProvider.XAI, model_id="grok-3",
            capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.REASONING, 
                         ModelCapability.CODE_GENERATION, ModelCapability.ANALYSIS],
            max_tokens=131072, supports_streaming=True,
        ))
        
        # DeepSeek Models
        self.register(ModelConfig(
            name="deepseek-v3", provider=ModelProvider.DEEPSEEK, model_id="deepseek-chat",
            capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.REASONING, 
                         ModelCapability.CODE_GENERATION],
            max_tokens=65536, cost_per_1k_input=0.00027, cost_per_1k_output=0.0011,
        ))
        self.register(ModelConfig(
            name="deepseek-r1", provider=ModelProvider.DEEPSEEK, model_id="deepseek-reasoner",
            capabilities=[ModelCapability.REASONING, ModelCapability.ANALYSIS],
            max_tokens=65536, cost_per_1k_input=0.00055, cost_per_1k_output=0.00219,
        ))
        
        # Local Models
        self.register(ModelConfig(
            name="local-llama", provider=ModelProvider.OLLAMA, model_id="llama3.2",
            capabilities=[ModelCapability.TEXT_GENERATION, ModelCapability.CODE_GENERATION],
            max_tokens=8192, requires_api_key=False, latency_p95_ms=5000,
        ))
        
        self._initialized = True
        logger.info(f"Registered {len(self._models)} default models")
    
    def get_model(self, name: str) -> Optional[ModelConfig]:
        return self._models.get(name)
    
    def get_default(self) -> ModelConfig:
        """Get default model"""
        for model in self._models.values():
            if model.is_default:
                return model
        return list(self._models.values())[0]
    
    def get_fallback(self) -> ModelConfig:
        """Get fallback model"""
        for model in self._models.values():
            if model.is_fallback:
                return model
        return self.get_default()
    
    def select_for_capability(
        self,
        capability: ModelCapability,
        prefer_cost: bool = False,
        prefer_speed: bool = False,
    ) -> Optional[ModelConfig]:
        """Select best model for a capability"""
        cap_key = capability.value
        model_names = self._capability_models.get(cap_key, [])
        if not model_names:
            logger.warning(f"No models found for capability: {capability.value}")
            return None
        
        models = [self._models[n] for n in model_names if n in self._models]
        if not models:
            return None
        
        # Sort by criteria
        if prefer_cost:
            models.sort(key=lambda m: m.cost_per_1k_input + m.cost_per_1k_output)
        elif prefer_speed:
            models.sort(key=lambda m: m.latency_p95_ms)
        else:
            # Default: prefer capable models
            models.sort(key=lambda m: len(m.capabilities), reverse=True)
        
        return models[0]
    
    def select_best_model(
        self,
        task_type: str,
        required_capabilities: List[ModelCapability],
        prefer_cost: bool = False,
        prefer_speed: bool = False,
    ) -> ModelConfig:
        """Select the best model for a given task"""
        for cap in required_capabilities:
            model = self.select_for_capability(cap, prefer_cost, prefer_speed)
            if model:
                return model
        
        return self.get_default()
    
    def get_all_models(self) -> List[ModelConfig]:
        return list(self._models.values())
    
    def get_models_by_provider(self, provider: ModelProvider) -> List[ModelConfig]:
        provider_key = provider.value
        return [self._models[n] for n in self._provider_models.get(provider_key, [])
                if n in self._models]


# Global registry
global_model_registry = ModelRegistry()