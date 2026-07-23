"""
Dependency Injection Container
===============================
Service location and dependency injection with lifecycle management
"""

import inspect
import logging
from typing import Any, Callable, Dict, Optional, Set, Type, TypeVar, Union

logger = logging.getLogger(__name__)

T = TypeVar("T")


class Lifecycle:
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"


class DIContainer:
    """
    Advanced DI container with auto-wiring and lifecycle management
    """
    
    def __init__(self):
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._lifecycles: Dict[str, str] = {}
        self._scoped_instances: Dict[str, Dict[str, Any]] = {}
        self._lock = False
    
    def register(
        self,
        interface: Union[Type, str],
        implementation: Any = None,
        factory: Optional[Callable] = None,
        lifecycle: str = Lifecycle.SINGLETON,
    ):
        """Register a service"""
        name = interface if isinstance(interface, str) else interface.__name__
        
        if factory:
            self._factories[name] = factory
            self._lifecycles[name] = lifecycle
            logger.debug(f"Registered factory for {name} ({lifecycle})")
        elif implementation:
            self._services[name] = implementation
            self._lifecycles[name] = Lifecycle.SINGLETON
            logger.debug(f"Registered singleton: {name}")
        else:
            raise ValueError(f"Must provide implementation or factory for {name}")
    
    def register_singleton(self, interface: Union[Type, str], implementation: Any):
        """Register a singleton instance"""
        self.register(interface, implementation, lifecycle=Lifecycle.SINGLETON)
    
    def register_transient(self, interface: Union[Type, str], factory: Callable):
        """Register a transient factory"""
        self.register(interface, factory=factory, lifecycle=Lifecycle.TRANSIENT)
    
    def resolve(self, interface: Union[Type, str]) -> Any:
        """Resolve a service"""
        name = interface if isinstance(interface, str) else interface.__name__
        
        # Check registered singletons
        if name in self._services:
            return self._services[name]
        
        # Check factories
        if name in self._factories:
            lifecycle = self._lifecycles[name]
            if lifecycle == Lifecycle.SINGLETON:
                instance = self._factories[name]()
                self._services[name] = instance
                return instance
            elif lifecycle == Lifecycle.TRANSIENT:
                return self._factories[name]()
        
        # Try auto-wiring
        if isinstance(interface, type):
            return self._auto_wire(interface)
        
        raise KeyError(f"Service '{name}' not registered")
    
    def _auto_wire(self, cls: Type) -> Any:
        """Auto-wire a class by resolving its constructor dependencies"""
        try:
            sig = inspect.signature(cls.__init__)
            params = {}
            for param_name, param in sig.parameters.items():
                if param_name == "self":
                    continue
                if param.annotation != inspect.Parameter.empty:
                    try:
                        params[param_name] = self.resolve(param.annotation)
                    except KeyError:
                        if param.default != inspect.Parameter.empty:
                            params[param_name] = param.default
                        else:
                            raise
                elif param.default != inspect.Parameter.empty:
                    params[param_name] = param.default
            
            return cls(**params)
        except Exception as e:
            logger.error(f"Auto-wiring failed for {cls.__name__}: {e}")
            raise
    
    def begin_scope(self, scope_id: str):
        """Begin a new scope"""
        self._scoped_instances[scope_id] = {}
    
    def end_scope(self, scope_id: str):
        """End a scope and clear scoped instances"""
        if scope_id in self._scoped_instances:
            del self._scoped_instances[scope_id]
    
    def has_service(self, interface: Union[Type, str]) -> bool:
        name = interface if isinstance(interface, str) else interface.__name__
        return name in self._services or name in self._factories


# Global container
global_container = DIContainer()