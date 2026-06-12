from typing import Dict, Optional, List, Any

from modules.bluetooth.interface import BluetoothModuleInterface, BluetoothState


class MockBluetoothModule(BluetoothModuleInterface):
    """Mock implementation for development on macOS"""
    
    def __init__(self):
        super().__init__()
        self._paired_addresses = {"AA:BB:CC:DD:EE:FF"}
        self._state = self._create_initial_state()
        self._shuffle = "off"
        self._repeat = "off"
    
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
        devices = []
        for dev in self._state.available_devices:
            is_connected = self._state.connected and dev["address"] == self._state.device_address
            is_paired = dev["address"] in self._paired_addresses
            devices.append({
                "address": dev["address"],
                "name": dev["name"],
                "isConnected": is_connected,
                "isPaired": is_paired
            })
        return {
            "connected": self._state.connected,
            "device_name": self._state.device_name,
            "device_address": self._state.device_address,
            "battery_level": self._state.battery_level,
            "available_devices": devices,
        }
    
    def get_connected_device(self) -> Optional[Dict[str, str]]:
        if self._state.connected:
            return {
                "name": self._state.device_name,
                "address": self._state.device_address
            }
        return None
    
    def scan_devices(self) -> List[Dict[str, Any]]:
        print("[MockBluetooth] Scanning devices...")
        devices = []
        for dev in self._state.available_devices:
            is_connected = self._state.connected and dev["address"] == self._state.device_address
            is_paired = dev["address"] in self._paired_addresses
            devices.append({
                "address": dev["address"],
                "name": dev["name"],
                "isConnected": is_connected,
                "isPaired": is_paired
            })
        return devices
    
    def connect(self, address: str) -> bool:
        print(f"[MockBluetooth] Connecting to {address}")
        self._state.connected = True
        self._state.device_address = address
        self._paired_addresses.add(address)
        for dev in self._state.available_devices:
            if dev["address"] == address:
                self._state.device_name = dev["name"]
                break
        return True
    
    def disconnect(self) -> bool:
        print("[MockBluetooth] Disconnecting")
        self._state.connected = False
        self._state.device_address = None
        self._state.device_name = None
        return True
    
    def unpair(self, address: str) -> bool:
        print(f"[MockBluetooth] Unpairing {address}")
        if address in self._paired_addresses:
            self._paired_addresses.remove(address)
        if self._state.device_address == address:
            self._state.connected = False
            self._state.device_address = None
            self._state.device_name = None
        return True
    
    def get_battery_level(self) -> Optional[int]:
        return self._state.battery_level
 
    def get_media_status(self) -> Dict[str, Any]:
        return {
            "playback_status": "playing" if self._state.connected else "stopped",
            "shuffle": self._shuffle,
            "repeat": self._repeat,
            "current_track": {
                "title": "Mock Bluetooth Track",
                "artist": "Mock Artist",
                "album": "Mock Album",
                "duration": 180,
                "position": 45,
                "cover_art": "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='100' height='100' viewBox='0 0 100 100'><rect width='100' height='100' fill='%236366f1'/><text x='50%' y='50%' dominant-baseline='middle' text-anchor='middle' font-family='sans-serif' font-size='12' fill='white'>Mock Cover</text></svg>"
            } if self._state.connected else None
        }

    def player_play(self) -> bool:
        print("[MockBluetooth] Player Play")
        return True

    def player_pause(self) -> bool:
        print("[MockBluetooth] Player Pause")
        return True

    def player_next(self) -> bool:
        print("[MockBluetooth] Player Next")
        return True

    def player_previous(self) -> bool:
        print("[MockBluetooth] Player Previous")
        return True

    def player_shuffle(self, mode: str) -> bool:
        print(f"[MockBluetooth] Player Shuffle: {mode}")
        self._shuffle = mode
        return True

    def player_repeat(self, mode: str) -> bool:
        print(f"[MockBluetooth] Player Repeat: {mode}")
        self._repeat = mode
        return True