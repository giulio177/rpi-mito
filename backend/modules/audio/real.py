import subprocess
import re
from typing import Dict, Optional

from modules.audio.interface import AudioModuleInterface, AudioState
from core.config import get_settings


class RealAudioModule(AudioModuleInterface):
    """Real implementation for Raspberry Pi using amixer"""
    
    def __init__(self):
        super().__init__()
        self._state = self._create_initial_state()
        settings = get_settings()
        self.mixer_control = settings.audio_mixer_control
    
    def _create_initial_state(self) -> AudioState:
        return AudioState(enabled=True, status="ready")
    
    def _run_amixer(self, args: list) -> Optional[str]:
        """Run amixer command"""
        try:
            result = subprocess.check_output(
                ["amixer"] + args,
                stderr=subprocess.DEVNULL,
                text=True,
                timeout=3
            )
            return result
        except Exception as e:
            print(f"amixer error: {e}")
            return None
    
    def initialize(self) -> bool:
        self.update_state(enabled=True, status="ready")
        return True
    
    def shutdown(self) -> bool:
        self.update_state(enabled=False, status="shutdown")
        return True
    
    def get_status(self) -> Dict[str, any]:
        return {
            "volume": self.get_volume(),
            "muted": self.get_muted(),
            "playback_status": self.get_playback_status(),
            "current_track": self.get_current_track(),
            "source": self._state.current_source,
        }
    
    def set_volume(self, level: int) -> bool:
        level = max(0, min(100, level))
        result = self._run_amixer(["sset", self.mixer_control, f"{level}%"])
        if result is not None:
            self._state.volume = level
            return True
        return False
    
    def get_volume(self) -> int:
        result = self._run_amixer(["sget", self.mixer_control])
        if result:
            match = re.search(r"\[(\d+)%\]", result)
            if match:
                return int(match.group(1))
        return self._state.volume
    
    def set_muted(self, muted: bool) -> bool:
        state = "mute" if muted else "unmute"
        result = self._run_amixer(["sset", self.mixer_control, state])
        if result is not None:
            self._state.muted = muted
            return True
        return False
    
    def get_muted(self) -> bool:
        result = self._run_amixer(["sget", self.mixer_control])
        if result:
            match = re.search(r"\[(on|off)\]", result)
            if match:
                return match.group(1) == "off"
        return self._state.muted
    
    def get_current_track(self) -> Optional[Dict[str, str]]:
        return self._state.current_track
    
    def get_playback_status(self) -> str:
        return self._state.playback_status