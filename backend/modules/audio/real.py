import asyncio
import re
from typing import Dict, Any, Optional
from modules.audio.interface import AudioModuleInterface, AudioState

class RealAudioModule(AudioModuleInterface):
    def __init__(self):
        super().__init__()
        self._state = self._create_initial_state()

    def _create_initial_state(self) -> AudioState:
        return AudioState(
            enabled=True,
            status="ready",
            volume=50,
            muted=False,
            current_source="system",
            current_track=None,
            playback_status="stopped"
        )
    
    def initialize(self) -> bool:
        # Load current volume in the background
        asyncio.create_task(self._sync_volume())
        # Dynamically routing all audio to the analog headphone jack
        asyncio.create_task(self._initialize_routing())
        self.update_state(enabled=True, status="ready")
        return True

    async def _initialize_routing(self):
        """Discovers the headphone jack/analog output sink and sets it as the default sink in PulseAudio."""
        print("[RealAudio] Initializing default audio routing...")
        # Give PulseAudio server a moment to start / settle
        await asyncio.sleep(2.0)
        
        try:
            target_sink = None
            short_output = ""
            
            # 1. Query verbose list of sinks to check card/driver properties (like bcm2835 Headphones)
            proc = await asyncio.create_subprocess_exec(
                "pactl", "list", "sinks",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode == 0:
                output = stdout.decode()
                sinks = output.split("Sink #")
                for sink_block in sinks[1:]:
                    name_match = re.search(r'^\s*Name:\s*(\S+)', sink_block, re.MULTILINE)
                    if not name_match:
                        continue
                    sink_name = name_match.group(1)
                    
                    block_lower = sink_block.lower()
                    if any(term in block_lower for term in ["headphones", "headphone", "analog-stereo", "bcm2835 headphones"]):
                        target_sink = sink_name
                        break
            else:
                print(f"[RealAudio] Verbose pactl list sinks failed: {stderr.decode().strip()}")

            # 2. Fallback 1: check pactl list sinks short for standard keywords
            if not target_sink:
                proc_short = await asyncio.create_subprocess_exec(
                    "pactl", "list", "sinks", "short",
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout_short, _ = await proc_short.communicate()
                short_output = stdout_short.decode().strip()
                for line in short_output.splitlines():
                    parts = line.split()
                    if len(parts) >= 2:
                        name = parts[1]
                        if any(term in name.lower() for term in ["analog-stereo", "headphones", "headphone", "jack"]):
                            target_sink = name
                            break

            # 3. Fallback 2: if there is any sink ending with .2 (typically analog headphones on mailbox VC4 drivers)
            if not target_sink:
                if not short_output:
                    proc_short = await asyncio.create_subprocess_exec(
                        "pactl", "list", "sinks", "short",
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout_short, _ = await proc_short.communicate()
                    short_output = stdout_short.decode().strip()
                
                for line in short_output.splitlines():
                    parts = line.split()
                    if len(parts) >= 2:
                        name = parts[1]
                        if "mailbox" in name and name.endswith(".2"):
                            target_sink = name
                            break

            if target_sink:
                print(f"[RealAudio] Found analog output sink: {target_sink}")
                # Set as default sink
                proc_set = await asyncio.create_subprocess_exec(
                    "pactl", "set-default-sink", target_sink,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout_set, stderr_set = await proc_set.communicate()
                if proc_set.returncode == 0:
                    print(f"[RealAudio] Default sink successfully set to {target_sink}")
                else:
                    print(f"[RealAudio] Failed to set default sink: {stderr_set.decode().strip()}")
            else:
                print("[RealAudio] No analog output/headphone jack sink found in PulseAudio.")
                
        except Exception as e:
            print(f"[RealAudio] Error during audio routing initialization: {e}")

    def shutdown(self) -> bool:
        self.update_state(enabled=False, status="shutdown")
        return True

    def get_status(self) -> Dict[str, Any]:
        from core.hal import HALFactory
        
        current_source = "system"
        current_track = None
        playback_status = "stopped"
        
        try:
            bt = HALFactory.get_module("bluetooth")
            if bt and bt.get_status().get("connected"):
                bt_media = bt.get_media_status()
                if bt_media.get("current_track"):
                    current_source = "bluetooth"
                    current_track = bt_media.get("current_track")
                    playback_status = bt_media.get("playback_status", "stopped")
        except Exception as e:
            print(f"[RealAudio] Error checking Bluetooth status: {e}")

        return {
            "volume": self._state.volume,
            "muted": self._state.muted,
            "playback_status": playback_status,
            "current_track": current_track,
            "source": current_source,
            "current_source": current_source,
        }

    async def _sync_volume(self):
        try:
            proc = await asyncio.create_subprocess_shell(
                "pactl get-sink-volume @DEFAULT_SINK@",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode == 0:
                output = stdout.decode()
                match = re.search(r'(\d+)%', output)
                if match:
                    self._state.volume = int(match.group(1))
        except Exception as e:
            print(f"[RealAudio] Error syncing volume: {e}")

    async def set_volume(self, level: int) -> bool:
        level = max(0, min(100, level))
        try:
            proc = await asyncio.create_subprocess_shell(
                f"pactl set-sink-volume @DEFAULT_SINK@ {level}%",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            if proc.returncode == 0:
                self._state.volume = level
                return True
            return False
        except Exception as e:
            print(f"[RealAudio] Error setting volume: {e}")
            return False

    def get_volume(self) -> int:
        return self._state.volume

    async def set_muted(self, muted: bool) -> bool:
        state_str = "on" if muted else "off"
        try:
            proc = await asyncio.create_subprocess_shell(
                f"pactl set-sink-mute @DEFAULT_SINK@ {state_str}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await proc.communicate()
            if proc.returncode == 0:
                self._state.muted = muted
                return True
            return False
        except Exception as e:
            print(f"[RealAudio] Error setting mute: {e}")
            return False

    def get_muted(self) -> bool:
        return self._state.muted

    def get_current_track(self) -> Optional[Dict[str, str]]:
        return self._state.current_track

    def get_playback_status(self) -> str:
        return self._state.playback_status