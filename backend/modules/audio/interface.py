from abc import abstractmethod
from typing import Dict, Any, Optional

from modules.base import BaseModule, ModuleState


class AudioState(ModuleState):
    volume: int = 50
    muted: bool = False
    current_source: Optional[str] = None
    current_track: Optional[Dict[str, str]] = None
    playback_status: str = "stopped"


class AudioModuleInterface(BaseModule):
    """Interface for audio module implementations"""
    
    @abstractmethod
    def set_volume(self, level: int) -> bool:
        """Set volume level (0-100)"""
        pass
    
    @abstractmethod
    def get_volume(self) -> int:
        """Get current volume level"""
        pass
    
    @abstractmethod
    def set_muted(self, muted: bool) -> bool:
        """Set mute state"""
        pass
    
    @abstractmethod
    def get_muted(self) -> bool:
        """Get mute state"""
        pass
    
    @abstractmethod
    def get_current_track(self) -> Optional[Dict[str, str]]:
        """Get info about currently playing track"""
        pass
    
    @abstractmethod
    def get_playback_status(self) -> str:
        """Get playback status: 'playing', 'paused', 'stopped'"""
        pass