from typing import Dict, List, Optional

from modules.wifi.interface import WiFiModuleInterface, WiFiState


class MockWiFiModule(WiFiModuleInterface):
    """Mock implementation for development on macOS"""
    
    def __init__(self):
        super().__init__()
        self._state = self._create_initial_state()
    
    def _create_initial_state(self) -> WiFiState:
        return WiFiState(
            enabled=True,
            status="mock_ready",
            connected=True,
            ssid="Casa_Mio",
            ip_address="192.168.1.100",
            signal_strength=75,
            available_networks=[
                {"ssid": "Casa_Mio", "signal": 75, "security": "WPA2"},
                {"ssid": "Guest_Network", "signal": 60, "security": "WPA2"},
                {"ssid": "Vodafone-1234", "signal": 45, "security": "WPA2"},
            ]
        )
    
    def initialize(self) -> bool:
        print("[MockWiFi] Initialized")
        self.update_state(enabled=True, status="mock_ready")
        return True
    
    def shutdown(self) -> bool:
        print("[MockWiFi] Shutdown")
        self.update_state(enabled=False, status="shutdown")
        return True
    
    def get_status(self) -> Dict[str, any]:
        return {
            "connected": self._state.connected,
            "ssid": self._state.ssid,
            "ip_address": self._state.ip_address,
            "signal_strength": self._state.signal_strength,
            "available_networks": self._state.available_networks,
        }
    
    def get_current_connection(self) -> Optional[Dict[str, str]]:
        if self._state.connected:
            return {
                "ssid": self._state.ssid,
                "ip_address": self._state.ip_address,
                "signal": self._state.signal_strength,
            }
        return None
    
    def scan_networks(self) -> List[Dict[str, str]]:
        print("[MockWiFi] Scanning networks...")
        return self._state.available_networks
    
    def connect(self, ssid: str, password: Optional[str] = None) -> bool:
        print(f"[MockWiFi] Connecting to {ssid}")
        self._state.connected = True
        self._state.ssid = ssid
        self._state.ip_address = "192.168.1.100"
        return True
    
    def disconnect(self) -> bool:
        print("[MockWiFi] Disconnecting")
        self._state.connected = False
        self._state.ssid = None
        self._state.ip_address = None
        return True
    
    def get_signal_strength(self) -> int:
        return self._state.signal_strength
