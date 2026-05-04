import asyncio
from typing import Dict, List, Optional, Any
from modules.wifi.interface import WiFiModuleInterface, WiFiState

class RealWiFiModule(WiFiModuleInterface):
    def __init__(self):
        super().__init__()
        self._state = self._create_initial_state()

    def _create_initial_state(self) -> WiFiState:
        return WiFiState(
            enabled=True,
            status="ready",
            connected=False,
            ssid=None,
            ip_address=None,
            signal_strength=0,
            available_networks=[]
        )

    def initialize(self) -> bool:
        self.update_state(enabled=True, status="ready")
        return True

    def shutdown(self) -> bool:
        self.update_state(enabled=False, status="shutdown")
        return True

    def get_status(self) -> Dict[str, Any]:
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
                "ssid": self._state.ssid or "",
                "ip_address": self._state.ip_address or "",
                "signal": str(self._state.signal_strength),
            }
        return None

    async def scan_networks(self) -> List[Dict[str, Any]]:
        try:
            proc = await asyncio.create_subprocess_shell(
                "nmcli -t -f SSID,SIGNAL,SECURITY dev wifi list",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode != 0:
                print(f"[RealWiFi] Error scanning networks: {stderr.decode()}")
                return []
            
            output = stdout.decode().strip()
            networks = {}
            for line in output.split('\\n'):
                if not line:
                    continue
                # nmcli output format: SSID:SIGNAL:SECURITY
                parts = line.split(':')
                if len(parts) >= 3:
                    ssid = parts[0].strip()
                    if not ssid:
                        continue
                    try:
                        signal = int(parts[1])
                    except ValueError:
                        signal = 0
                    security = parts[2].strip()
                    is_secure = security != "" and security != "--"
                    
                    if ssid not in networks or networks[ssid]['signal'] < signal:
                        networks[ssid] = {
                            "ssid": ssid,
                            "signal": signal,
                            "security": security,
                            "is_secure": is_secure
                        }
            
            self._state.available_networks = list(networks.values())
            return self._state.available_networks
        except Exception as e:
            print(f"[RealWiFi] Exception during scan: {e}")
            return []

    async def connect(self, ssid: str, password: Optional[str] = None) -> bool:
        try:
            cmd = f'nmcli dev wifi connect "{ssid}"'
            if password:
                cmd += f' password "{password}"'
                
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                self._state.connected = True
                self._state.ssid = ssid
                return True
            print(f"[RealWiFi] Connection failed: {stderr.decode()}")
            return False
        except Exception as e:
            print(f"[RealWiFi] Exception connecting to wifi: {e}")
            return False

    async def disconnect(self) -> bool:
        try:
            if not self._state.ssid:
                return True
            proc = await asyncio.create_subprocess_shell(
                f'nmcli connection delete "{self._state.ssid}"',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            if proc.returncode == 0:
                self._state.connected = False
                self._state.ssid = None
                return True
            return False
        except Exception as e:
            print(f"[RealWiFi] Exception disconnecting: {e}")
            return False

    def get_signal_strength(self) -> int:
        return self._state.signal_strength
