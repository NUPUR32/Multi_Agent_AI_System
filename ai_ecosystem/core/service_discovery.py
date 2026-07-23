"""
Service Discovery & Agent Registry
===================================
Dynamic service registration, health checking, and discovery
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Set
from enum import Enum
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    STARTING = "starting"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    STOPPED = "stopped"


class ServiceType(Enum):
    AGENT = "agent"
    MEMORY = "memory"
    KNOWLEDGE = "knowledge"
    REASONING = "reasoning"
    TOOL = "tool"
    WORKFLOW = "workflow"
    MODEL = "model"
    DATABASE = "database"
    API = "api"
    MONITORING = "monitoring"
    SECURITY = "security"
    CORE = "core"


@dataclass
class ServiceInstance:
    """Represents a registered service instance"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    service_type: ServiceType = ServiceType.CORE
    version: str = "1.0.0"
    host: str = "localhost"
    port: int = 0
    status: ServiceStatus = ServiceStatus.STARTING
    metadata: Dict[str, Any] = field(default_factory=dict)
    capabilities: List[str] = field(default_factory=list)
    health_check_fn: Optional[Callable] = None
    registered_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    last_heartbeat: Optional[str] = None
    ttl_seconds: int = 60
    
    def is_expired(self) -> bool:
        if not self.last_heartbeat:
            return True
        last = datetime.fromisoformat(self.last_heartbeat)
        return (datetime.utcnow() - last) > timedelta(seconds=self.ttl_seconds)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "type": self.service_type.value,
            "version": self.version,
            "host": self.host,
            "port": self.port,
            "status": self.status.value,
            "metadata": self.metadata,
            "capabilities": self.capabilities,
            "registered_at": self.registered_at,
            "last_heartbeat": self.last_heartbeat,
        }


class ServiceRegistry:
    """
    Distributed service registry with health checking
    Supports dynamic registration, discovery, and load balancing
    """
    
    def __init__(self):
        self._services: Dict[str, ServiceInstance] = {}
        self._services_by_type: Dict[str, List[str]] = {}
        self._services_by_capability: Dict[str, List[str]] = {}
        self._lock = asyncio.Lock()
        self._health_check_task: Optional[asyncio.Task] = None
        self._event_bus = None
        logger.info("ServiceRegistry initialized")
    
    async def register(
        self,
        name: str,
        service_type: ServiceType,
        version: str = "1.0.0",
        host: str = "localhost",
        port: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
        capabilities: Optional[List[str]] = None,
        health_check_fn: Optional[Callable] = None,
        ttl_seconds: int = 60,
    ) -> ServiceInstance:
        """Register a new service instance"""
        instance = ServiceInstance(
            name=name,
            service_type=service_type,
            version=version,
            host=host,
            port=port,
            metadata=metadata or {},
            capabilities=capabilities or [],
            health_check_fn=health_check_fn,
            ttl_seconds=ttl_seconds,
            status=ServiceStatus.HEALTHY,
            last_heartbeat=datetime.utcnow().isoformat(),
        )
        
        async with self._lock:
            self._services[instance.id] = instance
            
            # Index by type
            type_key = service_type.value
            if type_key not in self._services_by_type:
                self._services_by_type[type_key] = []
            self._services_by_type[type_key].append(instance.id)
            
            # Index by capability
            for cap in instance.capabilities:
                if cap not in self._services_by_capability:
                    self._services_by_capability[cap] = []
                self._services_by_capability[cap].append(instance.id)
        
        logger.info(f"Registered service: {name} ({service_type.value}) as {instance.id}")
        
        # Publish event if event bus available
        if self._event_bus:
            from .event_bus import Event, EventType
            await self._event_bus.publish(Event(
                type=EventType.AGENT_REGISTERED,
                type_name="service.registered",
                source="ServiceRegistry",
                payload=instance.to_dict(),
            ))
        
        return instance
    
    async def deregister(self, service_id: str) -> bool:
        """Remove a service from registry"""
        async with self._lock:
            if service_id not in self._services:
                return False
            
            instance = self._services.pop(service_id)
            
            # Remove from type index
            type_key = instance.service_type.value
            if type_key in self._services_by_type:
                self._services_by_type[type_key] = [
                    sid for sid in self._services_by_type[type_key] if sid != service_id
                ]
            
            # Remove from capability index
            for cap in instance.capabilities:
                if cap in self._services_by_capability:
                    self._services_by_capability[cap] = [
                        sid for sid in self._services_by_capability[cap] if sid != service_id
                    ]
        
        logger.info(f"Deregistered service: {instance.name}")
        return True
    
    async def heartbeat(self, service_id: str) -> bool:
        """Update service heartbeat timestamp"""
        async with self._lock:
            if service_id not in self._services:
                return False
            self._services[service_id].last_heartbeat = datetime.utcnow().isoformat()
            self._services[service_id].status = ServiceStatus.HEALTHY
        return True
    
    async def update_status(self, service_id: str, status: ServiceStatus) -> bool:
        """Update service status"""
        async with self._lock:
            if service_id not in self._services:
                return False
            self._services[service_id].status = status
        return True
    
    def discover(
        self,
        service_type: Optional[str] = None,
        capability: Optional[str] = None,
        status: Optional[ServiceStatus] = None,
    ) -> List[ServiceInstance]:
        """Discover services matching criteria"""
        results = []
        
        if service_type:
            service_ids = self._services_by_type.get(service_type, [])
        elif capability:
            service_ids = self._services_by_capability.get(capability, [])
        else:
            service_ids = list(self._services.keys())
        
        for sid in service_ids:
            instance = self._services.get(sid)
            if instance:
                if status and instance.status != status:
                    continue
                if not instance.is_expired():
                    results.append(instance)
        
        return results
    
    def get_service(self, service_id: str) -> Optional[ServiceInstance]:
        return self._services.get(service_id)
    
    def discover_one(
        self,
        service_type: Optional[str] = None,
        capability: Optional[str] = None,
    ) -> Optional[ServiceInstance]:
        """Discover a single service (round-robin simplification)"""
        services = self.discover(service_type=service_type, capability=capability)
        return services[0] if services else None
    
    def get_all_services(self) -> List[ServiceInstance]:
        return list(self._services.values())
    
    def get_services_by_type(self) -> Dict[str, List[ServiceInstance]]:
        result = {}
        for type_key, ids in self._services_by_type.items():
            result[type_key] = [self._services[sid] for sid in ids if sid in self._services]
        return result
    
    async def start_health_checks(self, interval: int = 30):
        """Start background health check loop"""
        if self._health_check_task:
            return
        
        async def _health_loop():
            while True:
                await asyncio.sleep(interval)
                await self._run_health_checks()
        
        self._health_check_task = asyncio.create_task(_health_loop())
        logger.info(f"Health check loop started (interval={interval}s)")
    
    async def _run_health_checks(self):
        """Run health checks on all registered services"""
        expired = []
        for sid, instance in self._services.items():
            # Check TTL
            if instance.is_expired():
                instance.status = ServiceStatus.UNHEALTHY
                expired.append(sid)
                logger.warning(f"Service {instance.name} ({sid}) heartbeat expired")
            
            # Run custom health check
            if instance.health_check_fn:
                try:
                    healthy = await instance.health_check_fn() if asyncio.iscoroutinefunction(instance.health_check_fn) else instance.health_check_fn()
                    instance.status = ServiceStatus.HEALTHY if healthy else ServiceStatus.UNHEALTHY
                except Exception as e:
                    instance.status = ServiceStatus.UNHEALTHY
                    logger.error(f"Health check failed for {instance.name}: {e}")
        
        # Auto-deregister expired services
        for sid in expired:
            if sid in self._services and self._services[sid].is_expired():
                await self.deregister(sid)
    
    def set_event_bus(self, event_bus):
        """Set event bus reference for event publishing"""
        self._event_bus = event_bus
    
    def get_stats(self) -> Dict[str, Any]:
        services = self.get_all_services()
        return {
            "total_services": len(services),
            "by_type": {k: len(v) for k, v in self.get_services_by_type().items()},
            "healthy": sum(1 for s in services if s.status == ServiceStatus.HEALTHY),
            "degraded": sum(1 for s in services if s.status == ServiceStatus.DEGRADED),
            "unhealthy": sum(1 for s in services if s.status == ServiceStatus.UNHEALTHY),
        }


# Global singleton
global_service_registry = ServiceRegistry()