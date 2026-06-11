import asyncio
import re
from typing import Dict, Optional, List, Any
from modules.bluetooth.interface import BluetoothModuleInterface, BluetoothState

class RealBluetoothModule(BluetoothModuleInterface):
    def __init__(self):
        super().__init__()
        self._state = self._create_initial_state()
        self._loop_task: Optional[asyncio.Task] = None
        self._media_status = {"playback_status": "stopped", "current_track": None}

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
        asyncio.create_task(self._power_on_and_start_loop())
        return True

    async def _power_on_and_start_loop(self):
        await self._run_bluetoothctl("power on")
        self._loop_task = asyncio.create_task(self._monitor_bluetooth_loop())

    def shutdown(self) -> bool:
        self.update_state(enabled=False, status="shutdown")
        if self._loop_task:
            self._loop_task.cancel()
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

    async def _run_bluetoothctl(self, command: str) -> str:
        try:
            proc = await asyncio.create_subprocess_shell(
                f"bluetoothctl {command}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode == 0:
                return stdout.decode().strip()
            else:
                return ""
        except Exception:
            return ""

    async def _monitor_bluetooth_loop(self):
        # We run this loop every 1.5 seconds to keep track and media position updated
        while True:
            try:
                paired_output = await self._run_bluetoothctl("paired-devices")
                paired_devices = []
                any_connected = False
                conn_address = None
                conn_name = None
                
                for line in paired_output.splitlines():
                    parts = line.split(None, 2)
                    if len(parts) >= 3 and parts[0] == "Device":
                        addr = parts[1]
                        name = parts[2]
                        
                        info_output = await self._run_bluetoothctl(f"info {addr}")
                        is_connected = "Connected: yes" in info_output
                        
                        paired_devices.append({
                            "id": addr,
                            "address": addr,
                            "name": name,
                            "isConnected": is_connected,
                            "isPaired": True
                        })
                        
                        if is_connected:
                            any_connected = True
                            conn_address = addr
                            conn_name = name
                
                # Check battery level if connected
                battery = None
                if any_connected and conn_address:
                    info_output = await self._run_bluetoothctl(f"info {conn_address}")
                    battery_match = re.search(r'Battery Percentage:\s*0x[0-9a-fA-F]+\s*\((\d+)\)', info_output)
                    if not battery_match:
                        battery_match = re.search(r'Battery Percentage:\s*(\d+)', info_output)
                    if battery_match:
                        battery = int(battery_match.group(1))
                
                # Update state
                self._state.connected = any_connected
                self._state.device_address = conn_address
                self._state.device_name = conn_name
                self._state.battery_level = battery
                
                # Merge paired devices with current available_devices to preserve discovery info
                updated_available = []
                seen_addrs = set()
                for d in paired_devices:
                    updated_available.append(d)
                    seen_addrs.add(d["address"])
                for d in self._state.available_devices:
                    if d["address"] not in seen_addrs:
                        updated_available.append(d)
                
                self._state.available_devices = updated_available
                
                # Update media status cache
                if any_connected and conn_address:
                    self._media_status = await self._query_media_status(conn_address)
                else:
                    self._media_status = {"playback_status": "stopped", "current_track": None}
                
            except Exception as e:
                print(f"[RealBluetooth] Exception in monitor loop: {e}")
                
            await asyncio.sleep(1.5)

    async def get_paired_devices(self) -> List[Dict[str, Any]]:
        return [d for d in self._state.available_devices if d.get("isPaired")]

    async def scan_devices(self) -> List[Dict[str, Any]]:
        try:
            proc = await asyncio.create_subprocess_shell(
                "bluetoothctl --timeout 5 scan on",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
        except Exception as e:
            print(f"[RealBluetooth] Scan shell error: {e}")
        
        try:
            all_output = await self._run_bluetoothctl("devices")
            paired_output = await self._run_bluetoothctl("paired-devices")
            
            paired_addrs = set()
            for line in paired_output.splitlines():
                parts = line.split(None, 2)
                if len(parts) >= 2 and parts[0] == "Device":
                    paired_addrs.add(parts[1])
            
            devices = []
            for line in all_output.splitlines():
                parts = line.split(None, 2)
                if len(parts) >= 3 and parts[0] == "Device":
                    addr = parts[1]
                    name = parts[2]
                    
                    info_output = await self._run_bluetoothctl(f"info {addr}")
                    is_connected = "Connected: yes" in info_output
                    is_paired = addr in paired_addrs
                    
                    devices.append({
                        "id": addr,
                        "address": addr,
                        "name": name,
                        "isConnected": is_connected,
                        "isPaired": is_paired
                    })
            
            self._state.available_devices = devices
            return devices
        except Exception as e:
            print(f"[RealBluetooth] Error getting devices after scan: {e}")
            return self._state.available_devices

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
            await self._run_bluetoothctl("discoverable off")
        except:
            pass

    async def set_discoverable(self, state: bool) -> bool:
        action = "on" if state else "off"
        try:
            await self._run_bluetoothctl(f"discoverable {action}")
            await self._run_bluetoothctl(f"pairable {action}")
            return True
        except Exception as e:
            print(f"[RealBluetooth] Exception setting discoverable: {e}")
            return False

    def get_battery_level(self) -> Optional[int]:
        return self._state.battery_level

    # --- AVRCP Media Player Controls & Status ---

    def get_media_status(self) -> Dict[str, Any]:
        return self._media_status

    async def _query_media_status(self, device_address: str) -> Dict[str, Any]:
        addr_underscore = device_address.replace(":", "_")
        for p in ["player0", "player1"]:
            player_path = f"/org/bluez/hci0/dev_{addr_underscore}/{p}"
            try:
                cmd = f"dbus-send --system --print-reply --dest=org.bluez {player_path} org.freedesktop.DBus.Properties.GetAll string:org.bluez.MediaPlayer1"
                proc = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await proc.communicate()
                
                if proc.returncode == 0:
                    output = stdout.decode()
                    return self._parse_dbus_properties(output)
            except Exception:
                pass
        return {"playback_status": "stopped", "current_track": None}

    def _parse_dbus_properties(self, output: str) -> Dict[str, Any]:
        status = "stopped"
        title = "Unknown Track"
        artist = "Unknown Artist"
        duration = 0
        position = 0
        
        status_match = re.search(r'string "Status"\s*\n\s*variant\s*string "([^"]+)"', output)
        if status_match:
            status = status_match.group(1).lower()
            
        position_match = re.search(r'string "Position"\s*\n\s*variant\s*uint32 (\d+)', output)
        if position_match:
            position = int(position_match.group(1)) // 1000  # convert ms to seconds
            
        track_block_match = re.search(r'string "Track"\s*\n\s*variant\s*array\s*\[\s*(.*?)\s*\]\s*\n\s*(\]|dict entry)', output, re.DOTALL)
        if track_block_match:
            track_block = track_block_match.group(1)
            
            title_match = re.search(r'string "Title"\s*\n\s*variant\s*string "([^"]+)"', track_block)
            if title_match:
                title = title_match.group(1)
                
            artist_match = re.search(r'string "Artist"\s*\n\s*variant\s*string "([^"]+)"', track_block)
            if artist_match:
                artist = artist_match.group(1)
                
            duration_match = re.search(r'string "Duration"\s*\n\s*variant\s*uint32 (\d+)', track_block)
            if not duration_match:
                duration_match = re.search(r'string "Duration"\s*\n\s*variant\s*uint64 (\d+)', track_block)
            if duration_match:
                duration = int(duration_match.group(1)) // 1000  # convert ms to seconds
                
        current_track = None
        if title and title != "Unknown Track":
            current_track = {
                "title": title,
                "artist": artist,
                "duration": duration,
                "position": position,
            }
            
        return {
            "playback_status": status,
            "current_track": current_track
        }

    async def player_play(self) -> bool:
        return await self._send_player_cmd("Play")

    async def player_pause(self) -> bool:
        return await self._send_player_cmd("Pause")

    async def player_next(self) -> bool:
        return await self._send_player_cmd("Next")

    async def player_previous(self) -> bool:
        return await self._send_player_cmd("Previous")

    async def _send_player_cmd(self, action: str) -> bool:
        if not self._state.connected or not self._state.device_address:
            return False
        addr_underscore = self._state.device_address.replace(":", "_")
        for p in ["player0", "player1"]:
            player_path = f"/org/bluez/hci0/dev_{addr_underscore}/{p}"
            try:
                cmd = f"dbus-send --system --print-reply --dest=org.bluez {player_path} org.bluez.MediaPlayer1.{action}"
                proc = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await proc.communicate()
                if proc.returncode == 0:
                    return True
            except Exception as e:
                print(f"[RealBluetooth] Error sending {action} to {p}: {e}")
        return False
