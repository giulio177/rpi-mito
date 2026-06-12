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
            # 1. Discover sinks
            proc = await asyncio.create_subprocess_exec(
                "pactl", "list", "sinks", "short",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode != 0:
                print(f"[RealAudio] Failed to list sinks: {stderr.decode().strip()}")
                return
            
            sinks_output = stdout.decode().strip()
            target_sink = None
            
            # Look for any sink containing "analog-stereo" or "headphones" or "headphone" or "jack"
            # Typical RPi onboard jack is: alsa_output.platform-bcm2835_audio.analog-stereo
            for line in sinks_output.splitlines():
                parts = line.split()
                if len(parts) >= 2:
                    sink_name = parts[1]
                    if any(term in sink_name.lower() for term in ["analog-stereo", "headphones", "headphone", "jack"]):
                        target_sink = sink_name
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