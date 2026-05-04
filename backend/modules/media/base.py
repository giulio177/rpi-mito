from typing import Any, Dict, List
from modules.base import BaseModule, ModuleState

class BaseMediaModule(BaseModule):
    """Abstract base class for media/library module"""
    
    def _create_initial_state(self) -> ModuleState:
        return ModuleState(
            enabled=True,
            status="idle"
        )
    
    async def get_all_songs(self) -> List[Dict[str, Any]]:
        """Retrieve all songs from the library"""
        raise NotImplementedError
