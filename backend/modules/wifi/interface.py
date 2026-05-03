from abc import abstractmethod
from typing import Dict, Any, List, Optional

from modules.base import BaseModule, ModuleState


class WiFiState(ModuleState):
    connected: bool = False
    ssid: Optional[str] = None
    ip_address: Optional[str] = None
    signal_strength: int = 0
    available_networks: List[Dict[str, str]] = []


class WiFiModuleInterface(BaseModule):
    """Interface for WiFi module implementations"""
    
    @abstractmethod
    def get_current_connection(self) -> Optional[Dict[str, str]]:
        """Get current WiFi connection info"""
        pass
    
    @abstractmethod
    def scan_networks(self) -> List[Dict[str, str]]:
        """Scan for available networks"""
        pass
    
    @abstractmethod
    def connect(self, ssid: str, password: Optional[str] = None) -> bool:
        """Connect to a network"""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """Disconnect from current network"""
        pass
    
    @abstractmethod
    def get_signal_strength(self) -> int:
        """Get signal strength (0-100)"""
        pass