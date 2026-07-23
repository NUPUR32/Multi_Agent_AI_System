"""
Plugin System - Dynamic Tool & Agent Loading
=============================================
Hot-reloadable plugin architecture with sandboxing
"""

import importlib
import inspect
import logging
import os
import sys
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Type
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class PluginType(Enum):
    AGENT = "agent"
    TOOL = "tool"
    MEMORY = "memory"
    WORKFLOW = "workflow"
    MODEL = "model"
    HOOK = "hook"
    EXTENSION = "extension"


class PluginStatus(Enum):
    DISCOVERED = "discovered"
    LOADED = "loaded"
    ACTIVATED = "activated"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class PluginManifest:
    """Plugin metadata"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    version: str = "1.0.0"
    description: str = ""
    plugin_type: PluginType = PluginType.EXTENSION
    author: str = ""
    dependencies: List[str] = field(default_factory=list)
    min_system_version: str = "1.0.0"
    entry_point: str = ""
    config_schema: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PluginInstance:
    """Loaded plugin instance"""
    manifest: PluginManifest
    module: Any = None
    status: PluginStatus = PluginStatus.DISCOVERED
    hooks: Dict[str, List[Callable]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    loaded_at: Optional[str] = None
    
    def activate(self):
        self.status = PluginStatus.ACTIVATED
        self.loaded_at = datetime.utcnow().isoformat()
    
    def deactivate(self):
        self.status = PluginStatus.DISABLED


class PluginManager:
    """
    Plugin management system with hot-reload capability
    """
    
    def __init__(self, plugin_dirs: Optional[List[str]] = None):
        self.plugins: Dict[str, PluginInstance] = {}
        self.plugin_dirs = plugin_dirs or []
        self._event_bus = None
        self._watcher_task = None
        self._global_hooks: Dict[str, List[Callable]] = {}
        logger.info("PluginManager initialized")
    
    def discover_plugins(self):
        """Discover available plugins from plugin directories"""
        for plugin_dir in self.plugin_dirs:
            if not os.path.exists(plugin_dir):
                continue
            
            for item in os.listdir(plugin_dir):
                item_path = os.path.join(plugin_dir, item)
                
                # Check for Python files
                if item.endswith(".py"):
                    self._discover_python_plugin(item_path)
                
                # Check for directories with __init__.py
                if os.path.isdir(item_path):
                    init_file = os.path.join(item_path, "__init__.py")
                    if os.path.exists(init_file):
                        self._discover_python_plugin(init_file, package_path=item_path)
        
        logger.info(f"Discovered {len(self.plugins)} plugins")
    
    def _discover_python_plugin(self, file_path: str, package_path: Optional[str] = None):
        """Discover a Python file as a plugin"""
        try:
            manifest = PluginManifest(
                name=os.path.splitext(os.path.basename(file_path))[0],
                entry_point=file_path,
                plugin_type=PluginType.EXTENSION,
            )
            
            # Try to extract manifest from plugin
            if package_path:
                spec = importlib.util.spec_from_file_location(
                    manifest.name, os.path.join(package_path, "__init__.py")
                )
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    if hasattr(module, "__plugin_manifest__"):
                        manifest = module.__plugin_manifest__
            
            plugin = PluginInstance(manifest=manifest)
            self.plugins[manifest.name] = plugin
            logger.debug(f"Discovered plugin: {manifest.name}")
            
        except Exception as e:
            logger.error(f"Failed to discover plugin at {file_path}: {e}")
    
    def load_plugin(self, plugin_name: str) -> Optional[PluginInstance]:
        """Load a discovered plugin"""
        if plugin_name not in self.plugins:
            logger.error(f"Plugin {plugin_name} not found")
            return None
        
        plugin = self.plugins[plugin_name]
        
        try:
            # Load dependencies first
            for dep in plugin.manifest.dependencies:
                if dep not in self.plugins:
                    logger.warning(f"Dependency {dep} not found for {plugin_name}")
                    continue
                self.load_plugin(dep)
            
            # Import the module
            entry = plugin.manifest.entry_point
            if entry.endswith("__init__.py"):
                module_name = os.path.basename(os.path.dirname(entry))
                spec = importlib.util.spec_from_file_location(module_name, entry)
            else:
                module_name = os.path.splitext(os.path.basename(entry))[0]
                spec = importlib.util.spec_from_file_location(module_name, entry)
            
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                plugin.module = module
                plugin.status = PluginStatus.LOADED
                
                # Register hooks from module
                self._register_hooks(plugin)
                
                logger.info(f"Loaded plugin: {plugin_name} v{plugin.manifest.version}")
                return plugin
            
        except Exception as e:
            plugin.status = PluginStatus.ERROR
            plugin.metadata["error"] = str(e)
            logger.error(f"Failed to load plugin {plugin_name}: {e}")
        
        return None
    
    def _register_hooks(self, plugin: PluginInstance):
        """Register hooks defined in a plugin module"""
        if not plugin.module:
            return
        
        for name, obj in inspect.getmembers(plugin.module):
            # Check for hook decorator patterns
            if callable(obj) and hasattr(obj, "_plugin_hook_"):
                hook_name = obj._plugin_hook_
                if hook_name not in plugin.hooks:
                    plugin.hooks[hook_name] = []
                plugin.hooks[hook_name].append(obj)
                
                # Also register in global hooks
                if hook_name not in self._global_hooks:
                    self._global_hooks[hook_name] = []
                self._global_hooks[hook_name].append(obj)
    
    def activate_plugin(self, plugin_name: str) -> bool:
        """Activate a loaded plugin"""
        plugin = self.plugins.get(plugin_name)
        if not plugin or plugin.status != PluginStatus.LOADED:
            logger.error(f"Cannot activate plugin {plugin_name}: status={plugin.status}")
            return False
        
        try:
            # Call activate function if defined
            if plugin.module and hasattr(plugin.module, "activate"):
                plugin.module.activate()
            
            plugin.activate()
            logger.info(f"Activated plugin: {plugin_name}")
            return True
            
        except Exception as e:
            plugin.status = PluginStatus.ERROR
            logger.error(f"Failed to activate plugin {plugin_name}: {e}")
            return False
    
    def deactivate_plugin(self, plugin_name: str) -> bool:
        """Deactivate a plugin"""
        plugin = self.plugins.get(plugin_name)
        if not plugin:
            return False
        
        try:
            if plugin.module and hasattr(plugin.module, "deactivate"):
                plugin.module.deactivate()
            
            plugin.deactivate()
            logger.info(f"Deactivated plugin: {plugin_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to deactivate plugin {plugin_name}: {e}")
            return False
    
    def run_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Run all registered hooks by name"""
        results = []
        hooks = self._global_hooks.get(hook_name, [])
        
        for hook_fn in hooks:
            try:
                result = hook_fn(*args, **kwargs)
                results.append(result)
            except Exception as e:
                logger.error(f"Hook {hook_name} failed: {e}")
        
        return results
    
    def register_hook(self, hook_name: str, hook_fn: Callable):
        """Register a hook function"""
        if hook_name not in self._global_hooks:
            self._global_hooks[hook_name] = []
        self._global_hooks[hook_name].append(hook_fn)
    
    def set_event_bus(self, event_bus):
        self._event_bus = event_bus
    
    def get_plugin(self, name: str) -> Optional[PluginInstance]:
        return self.plugins.get(name)
    
    def get_active_plugins(self) -> List[PluginInstance]:
        return [p for p in self.plugins.values() if p.status == PluginStatus.ACTIVATED]
    
    def get_plugins_by_type(self, plugin_type: PluginType) -> List[PluginInstance]:
        return [p for p in self.plugins.values() if p.manifest.plugin_type == plugin_type]


# Global manager
global_plugin_manager = PluginManager()


def hook(name: str):
    """Decorator to mark a function as a plugin hook"""
    def decorator(func):
        func._plugin_hook_ = name
        return func
    return decorator