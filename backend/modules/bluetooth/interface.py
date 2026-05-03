from abc import abstractmethod
from typing import Dict, Any, List, Optional

from modules.base import BaseModule, ModuleState


class BluetoothState(ModuleState):
    connected: bool = False
    device_name: Optional[str] = None
    device_address: Optional[str] = None
    battery_level: Optional[int] = None
    available_devices: List[Dict[str, str]] = []


class BluetoothModuleInterface(BaseModule):
    """Interface for bluetooth module implementations"""
    
    @abstractmethod
    def get_connected_device(self) -> Optional[Dict[str, str]]:
        """Get currently connected device info"""
        pass
    
    @abstractmethod
    def scan_devices(self) -> List[Dict[str, str]]:
        """Scan for available devices"""
        pass
    
    @abstractmethod
    def connect(self, address: str) -> bool:
        """Connect to a device by address"""
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """Disconnect current device"""
        pass
    
    @abstractmethod
    def get_battery_level(self) -> Optional[int]:
        """Get battery level of connected device"""
        pass