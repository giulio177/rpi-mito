from typing import Dict, Optional

from modules.audio.interface import AudioModuleInterface, AudioState


class MockAudioModule(AudioModuleInterface):
    """Mock implementation for development on macOS"""
    
    def __init__(self):
        super().__init__()
        self._state = self._create_initial_state()
    
    def _create_initial_state(self) -> AudioState:
        return AudioState(
            enabled=True,
            status="mock_ready",
            volume=50,
            muted=False,
            current_source="mock_bt",
            current_track={
                "title": "Mock Track",
                "artist": "Mock Artist",
                "album": "Mock Album"
            },
            playback_status="playing"
        )
    
    def initialize(self) -> bool:
        print("[MockAudio] Initialized")
        self.update_state(enabled=True, status="mock_ready")
        return True
    
    def shutdown(self) -> bool:
        print("[MockAudio] Shutdown")
        self.update_state(enabled=False, status="shutdown")
        return True
    
    def get_status(self) -> Dict[str, any]:
        from core.hal import HALFactory
        shuffle = "off"
        repeat = "off"
        current_track = self._state.current_track
        
        try:
            bt = HALFactory.get_module("bluetooth")
            if bt and bt.get_status().get("connected"):
                bt_media = bt.get_media_status()
                shuffle = bt_media.get("shuffle", "off")
                repeat = bt_media.get("repeat", "off")
                if bt_media.get("current_track"):
                    current_track = bt_media.get("current_track")
        except Exception as e:
            print(f"[MockAudio] Error checking Bluetooth status: {e}")

        return {
            "volume": self._state.volume,
            "muted": self._state.muted,
            "playback_status": self._state.playback_status,
            "current_track": current_track,
            "source": self._state.current_source,
            "current_source": self._state.current_source,
            "shuffle": shuffle,
            "repeat": repeat,
        }
    
    def set_volume(self, level: int) -> bool:
        level = max(0, min(100, level))
        self._state.volume = level
        print(f"[MockAudio] Volume set to {level}")
        return True
    
    def get_volume(self) -> int:
        return self._state.volume
    
    def set_muted(self, muted: bool) -> bool:
        self._state.muted = muted
        print(f"[MockAudio] Muted: {muted}")
        return True
    
    def get_muted(self) -> bool:
        return self._state.muted
    
    def get_current_track(self) -> Optional[Dict[str, str]]:
        return self._state.current_track
    
    def get_playback_status(self) -> str:
        return self._state.playback_status