from typing import Dict, Optional, List

from modules.bluetooth.interface import BluetoothModuleInterface, BluetoothState


class MockBluetoothModule(BluetoothModuleInterface):
    """Mock implementation for development on macOS"""
    
    def __init__(self):
        super().__init__()
        self._state = self._create_initial_state()
    
    def _create_initial_state(self) -> BluetoothState:
        return BluetoothState(
            enabled=True,
            status="mock_ready",
            connected=True,
            device_name="iPhone di Giulio",
            device_address="AA:BB:CC:DD:EE:FF",
            battery_level=85,
            available_devices=[
                {"name": "iPhone di Giulio", "address": "AA:BB:CC:DD:EE:FF"},
                {"name": "Pixel Work", "address": "11:22:33:44:55:66"},
            ]
        )
    
    def initialize(self) -> bool:
        print("[MockBluetooth] Initialized")
        self.update_state(enabled=True, status="mock_ready")
        return True
    
    def shutdown(self) -> bool:
        print("[MockBluetooth] Shutdown")
        self.update_state(enabled=False, status="shutdown")
        return True
    
    def get_status(self) -> Dict[str, any]:
        return {
            "connected": self._state.connected,
            "device_name": self._state.device_name,
            "device_address": self._state.device_address,
            "battery_level": self._state.battery_level,
            "available_devices": self._state.available_devices,
        }
    
    def get_connected_device(self) -> Optional[Dict[str, str]]:
        if self._state.connected:
            return {
                "name": self._state.device_name,
                "address": self._state.device_address
            }
        return None
    
    def scan_devices(self) -> List[Dict[str, str]]:
        print("[MockBluetooth] Scanning devices...")
        return self._state.available_devices
    
    def connect(self, address: str) -> bool:
        print(f"[MockBluetooth] Connecting to {address}")
        self._state.connected = True
        self._state.device_address = address
        for dev in self._state.available_devices:
            if dev["address"] == address:
                self._state.device_name = dev["name"]
                break
        return True
    
    def disconnect(self) -> bool:
        print("[MockBluetooth] Disconnecting")
        self._state.connected = False
        return True
    
    def get_battery_level(self) -> Optional[int]:
        return self._state.battery_level