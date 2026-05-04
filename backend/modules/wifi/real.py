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
            # 1. Vediamo qual è la rete attiva attualmente
            proc_active = await asyncio.create_subprocess_shell(
                "nmcli -t -f ACTIVE,SSID dev wifi list | grep '^*'",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout_active, _ = await proc_active.communicate()
            active_ssid = stdout_active.decode().strip().replace("*:", "")

            # 2. Elenchiamo tutte le reti
            proc = await asyncio.create_subprocess_shell(
                "nmcli -t -f SSID,SIGNAL,SECURITY,BARS dev wifi list",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            
            output = stdout.decode().strip()
            networks = {}
            for line in output.split('\n'):
                if not line or ':' not in line:
                    continue
                parts = line.split(':')
                if len(parts) >= 3:
                    ssid = parts[0].strip()
                    if not ssid: continue
                    
                    try:
                        signal = int(parts[1])
                    except:
                        signal = 0
                        
                    is_secure = "WPA" in parts[2] or "WEP" in parts[2]
                    is_connected = (ssid == active_ssid)
                    
                    # Teniamo solo il segnale più forte per lo stesso SSID
                    if ssid not in networks or networks[ssid]['signal'] < signal:
                        networks[ssid] = {
                            "ssid": ssid,
                            "signal": signal,
                            "isSecure": is_secure,
                            "isConnected": is_connected
                        }
            
            self._state.available_networks = list(networks.values())
            # Aggiorniamo lo stato globale del modulo
            if active_ssid:
                self._state.connected = True
                self._state.ssid = active_ssid
            
            return self._state.available_networks
        except Exception as e:
            print(f"[RealWiFi] Scan error: {e}")
            return []


    async def connect(self, ssid: str, password: Optional[str] = None) -> bool:
        try:
            # 1. Pulizia: eliminiamo profili vecchi con lo stesso nome per evitare conflitti
            await asyncio.create_subprocess_shell(f'nmcli connection delete "{ssid}"')
            
            # 2. Connessione
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
