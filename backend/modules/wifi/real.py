import asyncio
import socket
from typing import Dict, List, Optional, Any
from modules.wifi.interface import WiFiModuleInterface, WiFiState

class RealWiFiModule(WiFiModuleInterface):
    def __init__(self):
        super().__init__()
        self._state = self._create_initial_state()
        self._loop_task: Optional[asyncio.Task] = None

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
        self._loop_task = asyncio.create_task(self._monitor_wifi_loop())
        return True

    def shutdown(self) -> bool:
        self.update_state(enabled=False, status="shutdown")
        if self._loop_task:
            self._loop_task.cancel()
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

    def _parse_terse_line(self, line: str) -> List[str]:
        # Helper to split colon-separated values while handling escaped colons '\:'
        temp = line.replace('\\:', '__COLON__')
        parts = temp.split(':')
        return [p.replace('__COLON__', ':') for p in parts]

    def _get_local_ip(self) -> str:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't need to be reachable
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

    async def _get_wifi_interface(self) -> str:
        try:
            proc = await asyncio.create_subprocess_exec(
                "nmcli", "-t", "-f", "DEVICE,TYPE", "device",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            for line in stdout.decode().splitlines():
                if not line:
                    continue
                parts = line.split(":")
                if len(parts) >= 2 and parts[1] == "wifi":
                    return parts[0]
        except Exception as e:
            print(f"[RealWiFi] Error finding wifi interface: {e}")
        return "wlan0"  # fallback

    async def _monitor_wifi_loop(self):
        while True:
            try:
                proc = await asyncio.create_subprocess_exec(
                    "nmcli", "-t", "-f", "ACTIVE,SSID,SIGNAL", "dev", "wifi", "list",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, _ = await proc.communicate()
                
                active_ssid = None
                signal = 0
                
                for line in stdout.decode().splitlines():
                    if not line:
                        continue
                    parts = self._parse_terse_line(line)
                    if len(parts) >= 2 and parts[0] == "yes":
                        active_ssid = parts[1]
                        if len(parts) >= 3:
                            try:
                                signal = int(parts[2])
                            except:
                                signal = 0
                        break
                
                if active_ssid:
                    ip = self._get_local_ip()
                    self._state.connected = True
                    self._state.ssid = active_ssid
                    self._state.ip_address = ip
                    self._state.signal_strength = signal
                else:
                    self._state.connected = False
                    self._state.ssid = None
                    self._state.ip_address = None
                    self._state.signal_strength = 0
            except Exception as e:
                print(f"[RealWiFi] Exception in monitor loop: {e}")
            await asyncio.sleep(5)

    async def scan_networks(self) -> List[Dict[str, Any]]:
        try:
            proc = await asyncio.create_subprocess_exec(
                "nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY", "dev", "wifi", "list",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            
            output = stdout.decode().strip()
            networks = {}
            for line in output.split('\n'):
                if not line or ':' not in line:
                    continue
                parts = self._parse_terse_line(line)
                if len(parts) >= 3:
                    ssid = parts[0].strip()
                    if not ssid:
                        continue
                    
                    try:
                        signal = int(parts[1])
                    except:
                        signal = 0
                        
                    is_secure = "WPA" in parts[2] or "WEP" in parts[2]
                    is_connected = (ssid == self._state.ssid)
                    
                    if ssid not in networks or networks[ssid]['signal'] < signal:
                        networks[ssid] = {
                            "ssid": ssid,
                            "signal": signal,
                            "is_secure": is_secure,
                            "isConnected": is_connected
                        }
            
            self._state.available_networks = list(networks.values())
            return self._state.available_networks
        except Exception as e:
            print(f"[RealWiFi] Scan error: {e}")
            return []

    async def connect(self, ssid: str, password: Optional[str] = None) -> bool:
        try:
            # 1. Try to connect using exec (avoids shell injection/quoting issues!)
            cmd_args = ["nmcli", "device", "wifi", "connect", ssid]
            if password:
                cmd_args.extend(["password", password])
                
            proc = await asyncio.create_subprocess_exec(
                *cmd_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            if proc.returncode == 0:
                self._state.connected = True
                self._state.ssid = ssid
                self._state.ip_address = self._get_local_ip()
                await self.scan_networks()
                return True
            
            # If connect failed and we supplied a password, try deleting the profile first and retry
            # (sometimes needed if NetworkManager has cached invalid parameters)
            print(f"[RealWiFi] Direct connection failed: {stderr.decode().strip()}. Retrying after profile cleanup...")
            proc_del = await asyncio.create_subprocess_exec(
                "nmcli", "connection", "delete", ssid,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc_del.communicate()
            
            proc = await asyncio.create_subprocess_exec(
                *cmd_args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode == 0:
                self._state.connected = True
                self._state.ssid = ssid
                self._state.ip_address = self._get_local_ip()
                await self.scan_networks()
                return True
                
            print(f"[RealWiFi] Connection failed: {stderr.decode().strip()} | stdout: {stdout.decode().strip()}")
            return False
        except Exception as e:
            print(f"[RealWiFi] Exception connecting to wifi: {e}")
            return False

    async def disconnect(self) -> bool:
        try:
            if not self._state.ssid:
                return True
                
            iface = await self._get_wifi_interface()
            proc = await asyncio.create_subprocess_exec(
                "nmcli", "device", "disconnect", iface,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode == 0:
                self._state.connected = False
                self._state.ssid = None
                self._state.ip_address = None
                self._state.signal_strength = 0
                await self.scan_networks()
                return True
            print(f"[RealWiFi] Disconnect failed: {stderr.decode().strip()}")
            return False
        except Exception as e:
            print(f"[RealWiFi] Exception disconnecting: {e}")
            return False

    def get_signal_strength(self) -> int:
        return self._state.signal_strength
