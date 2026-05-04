import asyncio
from typing import Dict, Optional, List, Any
from modules.bluetooth.interface import BluetoothModuleInterface, BluetoothState

class RealBluetoothModule(BluetoothModuleInterface):
    def __init__(self):
        super().__init__()
        self._state = self._create_initial_state()

    def _create_initial_state(self) -> BluetoothState:
        return BluetoothState(
            enabled=True,
            status="ready",
            connected=False,
            device_name=None,
            device_address=None,
            battery_level=None,
            available_devices=[]
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
            "device_name": self._state.device_name,
            "device_address": self._state.device_address,
            "battery_level": self._state.battery_level,
            "available_devices": self._state.available_devices,
        }

    def get_connected_device(self) -> Optional[Dict[str, str]]:
        if self._state.connected:
            return {
                "name": self._state.device_name or "",
                "address": self._state.device_address or ""
            }
        return None

    async def get_paired_devices(self) -> List[Dict[str, Any]]:
        try:
            # 1. Elenco dispositivi associati
            proc = await asyncio.create_subprocess_shell(
                "bluetoothctl paired-devices",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, _ = await proc.communicate()
            
            stdout, _ = await self._run_command("devices Paired")
            devices = []
            for line in stdout.decode().splitlines():
                # format: Device XX:XX:XX:XX:XX:XX Name
                parts = line.split(None, 2)
                if len(parts) >= 3:
                    dev_id = parts[1]
                    name = parts[2]
                    
                    # Controlla se è connesso davvero
                    info, _ = await self._run_command(f"info {dev_id}")
                    is_connected = "Connected: yes" in info.decode()
                    
                    devices.append({
                        "id": dev_id,
                        "address": dev_id,
                        "name": name,
                        "isConnected": is_connected,
                        "isPaired": True
                    })
            return devices
        except Exception as e:
            print(f"[RealBluetooth] Paired devices error: {e}")
            return []

    async def scan_devices(self) -> List[Dict[str, Any]]:
        try:
            # Avviamo una scansione reale per 5 secondi
            await asyncio.create_subprocess_shell("bluetoothctl --timeout 5 scan on")
            return await self.get_paired_devices()
        except Exception as e:
            print(f"[RealBluetooth] Scan error: {e}")
            return await self.get_paired_devices()

    async def toggle_connection(self, mac_address: str, connect: bool) -> bool:
        cmd_action = "connect" if connect else "disconnect"
        try:
            proc = await asyncio.create_subprocess_shell(
                f"bluetoothctl {cmd_action} {mac_address}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            if proc.returncode == 0:
                if not connect and self._state.device_address == mac_address:
                    self._state.connected = False
                    self._state.device_address = None
                    self._state.device_name = None
                return True
            return False
        except Exception as e:
            print(f"[RealBluetooth] Exception toggling connection: {e}")
            return False

    async def connect(self, address: str) -> bool:
        return await self.toggle_connection(address, True)

    async def disconnect(self) -> bool:
        if self._state.device_address:
            return await self.toggle_connection(self._state.device_address, False)
        return True

    async def _disable_discoverable(self):
        await asyncio.sleep(60)
        try:
            await asyncio.create_subprocess_shell(
                "bluetoothctl discoverable off",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            print("[RealBluetooth] Discoverable disabled via timer")
        except:
            pass

    async def set_discoverable(self, state: bool) -> bool:
        action = "on" if state else "off"
        try:
            # Dobbiamo attivare sia discoverable che pairable
            await asyncio.create_subprocess_shell(f"bluetoothctl discoverable {action}")
            await asyncio.create_subprocess_shell(f"bluetoothctl pairable {action}")
            return True
        except Exception as e:
            print(f"[RealBluetooth] Exception setting discoverable: {e}")
            return False


    def get_battery_level(self) -> Optional[int]:
        return self._state.battery_level
