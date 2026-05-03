from typing import Dict, Any

from modules.base import BaseModule, ModuleState


class MapPlaceholder(BaseModule):
    """Placeholder for Map module - to be implemented later"""
    
    def _create_initial_state(self) -> ModuleState:
        return ModuleState(enabled=False, status="placeholder")
    
    def initialize(self) -> bool:
        print("[Map] Placeholder - not implemented yet")
        self.update_state(enabled=False, status="placeholder")
        return True
    
    def shutdown(self) -> bool:
        return True
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "status": "placeholder",
            "message": "Map module not implemented yet",
        }