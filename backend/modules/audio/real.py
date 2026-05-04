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
        self.update_state(enabled=True, status="ready")
        return True

    def shutdown(self) -> bool:
        self.update_state(enabled=False, status="shutdown")
        return True

    def get_status(self) -> Dict[str, Any]:
        return {
            "volume": self._state.volume,
            "muted": self._state.muted,
            "playback_status": self._state.playback_status,
            "current_track": self._state.current_track,
            "source": self._state.current_source,
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