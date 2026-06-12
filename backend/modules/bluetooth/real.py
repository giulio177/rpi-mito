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
            # We run bluetoothctl and write the command to stdin (works on all versions and avoids CLI constraints)
            proc = await asyncio.create_subprocess_exec(
                "bluetoothctl",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate(input=f"{command}\nexit\n".encode())
            if proc.returncode == 0:
                return stdout.decode().strip()
            else:
                err_msg = stderr.decode().strip()
                print(f"[RealBluetooth] Command 'bluetoothctl {command}' failed (code {proc.returncode}): {err_msg}")
                return ""
        except Exception as e:
            print(f"[RealBluetooth] Exception running 'bluetoothctl {command}': {e}")
            return ""

    async def _monitor_bluetooth_loop(self):
        # Keep track of loaded loopback state to prevent duplicate modules
        self._loopback_loaded = False
        
        while True:
            try:
                # 1. Query connected devices from bluetoothctl directly (very reliable)
                bt_output = await self._run_bluetoothctl("devices Connected")
                
                conn_address = None
                conn_name = None
                any_connected = False
                
                for line in bt_output.splitlines():
                    if not line:
                        continue
                    parts = line.split(None, 2)
                    if len(parts) >= 3 and parts[0] == "Device":
                        conn_address = parts[1].upper()
                        conn_name = parts[2]
                        any_connected = True
                        break  # Infotainment currently focuses on the main connected device
                
                # 2. Check PulseAudio cards as a fallback
                pactl_output = ""
                try:
                    proc_pactl = await asyncio.create_subprocess_exec(
                        "pactl", "list", "cards", "short",
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout_pactl, stderr_pactl = await proc_pactl.communicate()
                    if proc_pactl.returncode == 0:
                        pactl_output = stdout_pactl.decode()
                    else:
                        print(f"[RealBluetooth] pactl list cards failed: {stderr_pactl.decode().strip()}")
                except Exception as pe:
                    print(f"[RealBluetooth] Exception listing cards: {pe}")
                
                card_match = re.search(r'bluez_card\.([0-9a-fA-F_]+)', pactl_output)
                card_ready_in_pulse = bool(card_match)
                
                if card_ready_in_pulse and not any_connected:
                    addr_underscore = card_match.group(1)
                    conn_address = addr_underscore.replace("_", ":").upper()
                    any_connected = True
                    info_output = await self._run_bluetoothctl(f"info {conn_address}")
                    name_match = re.search(r'Name:\s*(.*)', info_output)
                    conn_name = name_match.group(1).strip() if name_match else "Connected Device"
                
                # Auto-trust connected device so connection is saved/trusted
                if any_connected and conn_address:
                    await self._run_bluetoothctl(f"trust {conn_address}")

                # 3. Get all paired devices
                paired_output = await self._run_bluetoothctl("paired-devices")
                paired_devices = []
                
                for line in paired_output.splitlines():
                    parts = line.split(None, 2)
                    if len(parts) >= 3 and parts[0] == "Device":
                        addr = parts[1].upper()
                        name = parts[2]
                        is_this_connected = (conn_address is not None and addr == conn_address)
                        paired_devices.append({
                            "id": addr,
                            "address": addr,
                            "name": name,
                            "isConnected": is_this_connected,
                            "isPaired": True
                        })
                
                # If connected device is not in paired_devices list
                if any_connected and conn_address:
                    if not any(d["address"] == conn_address for d in paired_devices):
                        paired_devices.append({
                            "id": conn_address,
                            "address": conn_address,
                            "name": conn_name or conn_address,
                            "isConnected": True,
                            "isPaired": False
                        })
                
                # Query battery if connected
                battery = None
                if any_connected and conn_address:
                    info_output = await self._run_bluetoothctl(f"info {conn_address}")
                    battery_match = re.search(r'Battery Percentage:\s*0x[0-9a-fA-F]+\s*\((\d+)\)', info_output)
                    if not battery_match:
                        battery_match = re.search(r'Battery Percentage:\s*(\d+)', info_output)
                    if battery_match:
                        battery = int(battery_match.group(1))
                
                # Manage module-loopback based on PulseAudio card presence
                if card_ready_in_pulse and not self._loopback_loaded:
                    await asyncio.sleep(1.0)  # Wait for PulseAudio source to register
                    addr_underscore = conn_address.replace(":", "_")
                    
                    # Discover the exact bluetooth source name dynamically
                    source_name = f"bluez_source.{addr_underscore}.a2dp_source"
                    try:
                        proc_src = await asyncio.create_subprocess_exec(
                            "pactl", "list", "sources", "short",
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE
                        )
                        stdout_src, _ = await proc_src.communicate()
                        src_output = stdout_src.decode()
                        match_src = re.search(fr'(bluez_source\.{addr_underscore}\S*)', src_output)
                        if match_src:
                            source_name = match_src.group(1)
                    except Exception as se:
                        print(f"[RealBluetooth] Exception listing sources: {se}")
                    
                    # Unload any existing loopback first to avoid duplicates
                    try:
                        proc_un = await asyncio.create_subprocess_exec(
                            "pactl", "unload-module", "module-loopback",
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE
                        )
                        await proc_un.communicate()
                    except:
                        pass
                    
                    print(f"[RealBluetooth] Loading loopback for source: {source_name}")
                    try:
                        proc_load = await asyncio.create_subprocess_exec(
                            "pactl", "load-module", "module-loopback", f"source={source_name}", "latency_msec=200",
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE
                        )
                        stdout_load, stderr_load = await proc_load.communicate()
                        if proc_load.returncode == 0:
                            self._loopback_loaded = True
                            print(f"[RealBluetooth] Loaded module-loopback successfully for source {source_name}")
                        else:
                            print(f"[RealBluetooth] Failed to load module-loopback: {stderr_load.decode().strip()}")
                    except Exception as le:
                        print(f"[RealBluetooth] Exception loading loopback: {le}")
                        
                elif not card_ready_in_pulse and self._loopback_loaded:
                    print("[RealBluetooth] Card no longer ready, unloading loopback")
                    try:
                        proc_un = await asyncio.create_subprocess_exec(
                            "pactl", "unload-module", "module-loopback",
                            stdout=asyncio.subprocess.PIPE,
                            stderr=asyncio.subprocess.PIPE
                        )
                        await proc_un.communicate()
                        print("[RealBluetooth] Unloaded all module-loopback instances")
                    except Exception as ue:
                        print(f"[RealBluetooth] Exception unloading loopback: {ue}")
                    self._loopback_loaded = False
                
                # Update state
                self._state.connected = any_connected
                self._state.device_address = conn_address
                self._state.device_name = conn_name
                self._state.battery_level = battery
                
                # Merge lists
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
            proc = await asyncio.create_subprocess_exec(
                "bluetoothctl", "--timeout", "5", "scan", "on",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
        except Exception as e:
            print(f"[RealBluetooth] Scan exec error: {e}")
        
        try:
            all_output = await self._run_bluetoothctl("devices")
            paired_output = await self._run_bluetoothctl("paired-devices")
            
            paired_addrs = set()
            for line in paired_output.splitlines():
                parts = line.split(None, 2)
                if len(parts) >= 2 and parts[0] == "Device":
                    paired_addrs.add(parts[1].upper())
            
            devices = []
            for line in all_output.splitlines():
                parts = line.split(None, 2)
                if len(parts) >= 3 and parts[0] == "Device":
                    addr = parts[1].upper()
                    name = parts[2]
                    
                    is_this_connected = (self._state.device_address is not None and addr == self._state.device_address.upper())
                    is_paired = addr in paired_addrs
                    
                    devices.append({
                        "id": addr,
                        "address": addr,
                        "name": name,
                        "isConnected": is_this_connected,
                        "isPaired": is_paired
                    })
            
            self._state.available_devices = devices
            return devices
        except Exception as e:
            print(f"[RealBluetooth] Error getting devices after scan: {e}")
            return self._state.available_devices

    async def toggle_connection(self, mac_address: str, connect: bool) -> bool:
        mac_address = mac_address.upper()
        cmd_action = "connect" if connect else "disconnect"
        try:
            if connect:
                # First trust and pair, then connect to save the connection permanently
                await self._run_bluetoothctl(f"trust {mac_address}")
                try:
                    proc_pair = await asyncio.create_subprocess_exec(
                        "bluetoothctl", "pair", mac_address,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    await asyncio.wait_for(proc_pair.communicate(), timeout=8.0)
                except asyncio.TimeoutError:
                    print(f"[RealBluetooth] Timeout pairing with {mac_address}, terminating...")
                    try:
                        proc_pair.terminate()
                    except:
                        pass
                except Exception as pe:
                    print(f"[RealBluetooth] Exception during pairing: {pe}")

            proc = await asyncio.create_subprocess_exec(
                "bluetoothctl", cmd_action, mac_address,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode == 0:
                if not connect and self._state.device_address and self._state.device_address.upper() == mac_address:
                    self._state.connected = False
                    self._state.device_address = None
                    self._state.device_name = None
                return True
            else:
                print(f"[RealBluetooth] Connection toggle failed: {stderr.decode()} | {stdout.decode()}")
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
        for p in ["player0", "player1", "player2", "player3"]:
            player_path = f"/org/bluez/hci0/dev_{addr_underscore}/{p}"
            try:
                proc = await asyncio.create_subprocess_exec(
                    "dbus-send", "--system", "--print-reply", "--dest=org.bluez",
                    player_path, "org.freedesktop.DBus.Properties.GetAll", "string:org.bluez.MediaPlayer1",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await proc.communicate()
                
                if proc.returncode == 0:
                    output = stdout.decode()
                    return self._parse_dbus_properties(output)
            except Exception as e:
                print(f"[RealBluetooth] Error querying media status on {p}: {e}")
        return {"playback_status": "stopped", "current_track": None}

    def _parse_dbus_properties(self, output: str) -> Dict[str, Any]:
        status = "stopped"
        title = "Unknown Track"
        artist = "Unknown Artist"
        album = "Unknown Album"
        duration = 0
        position = 0
        
        status_match = re.search(r'string "Status"\s*\n\s*variant\s*string "([^"]+)"', output)
        if status_match:
            status = status_match.group(1).lower()
            
        position_match = re.search(r'string "Position"\s*\n\s*variant\s*uint32 (\d+)', output)
        if position_match:
            position = int(position_match.group(1)) // 1000  # convert ms to seconds
            
        # Extract Track array using robust bracket matching
        track_block = ""
        track_start = output.find('string "Track"')
        if track_start != -1:
            array_start = output.find('array [', track_start)
            if array_start != -1:
                bracket_count = 1
                idx = array_start + 7
                while idx < len(output) and bracket_count > 0:
                    if output[idx] == '[':
                        bracket_count += 1
                    elif output[idx] == ']':
                        bracket_count -= 1
                    idx += 1
                if bracket_count == 0:
                    track_block = output[array_start + 7 : idx - 1]

        if track_block:
            title_match = re.search(r'string "Title"\s*\n\s*variant\s*string "([^"]*)"', track_block)
            if title_match:
                title = title_match.group(1)
                
            artist_match = re.search(r'string "Artist"\s*\n\s*variant\s*string "([^"]*)"', track_block)
            if artist_match:
                artist = artist_match.group(1)
                
            album_match = re.search(r'string "Album"\s*\n\s*variant\s*string "([^"]*)"', track_block)
            if album_match:
                album = album_match.group(1)

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
                "album": album,
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
        for p in ["player0", "player1", "player2", "player3"]:
            player_path = f"/org/bluez/hci0/dev_{addr_underscore}/{p}"
            try:
                proc = await asyncio.create_subprocess_exec(
                    "dbus-send", "--system", "--print-reply", "--dest=org.bluez",
                    player_path, f"org.bluez.MediaPlayer1.{action}",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                await proc.communicate()
                if proc.returncode == 0:
                    return True
            except Exception as e:
                print(f"[RealBluetooth] Error sending {action} to {p}: {e}")
        return False
