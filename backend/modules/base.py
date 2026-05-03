from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel  # type: ignore[no-redef]


class ModuleState(BaseModel):
    """Base model for module state"""
    enabled: bool = False
    status: str = "unknown"
    metadata: Dict[str, Any] = {}


class BaseModule(ABC):
    """Abstract base class for all hardware modules"""
    
    def __init__(self):
        self._state = self._create_initial_state()
    
    @abstractmethod
    def _create_initial_state(self) -> ModuleState:
        """Create the initial state for this module"""
        pass
    
    @property
    def state(self) -> ModuleState:
        return self._state
    
    @abstractmethod
    def initialize(self) -> bool:
        """Initialize the module. Returns True if successful."""
        pass
    
    @abstractmethod
    def shutdown(self) -> bool:
        """Shutdown the module gracefully. Returns True if successful."""
        pass
    
    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get current status as a dictionary"""
        pass
    
    def update_state(self, **kwargs) -> None:
        """Update module state with provided parameters"""
        for key, value in kwargs.items():
            if hasattr(self._state, key):
                setattr(self._state, key, value)