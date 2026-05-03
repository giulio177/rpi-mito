from typing import Dict, Any

from modules.base import BaseModule, ModuleState


class OBDPlaceholder(BaseModule):
    """Placeholder for OBD module - to be implemented later"""
    
    def _create_initial_state(self) -> ModuleState:
        return ModuleState(enabled=False, status="placeholder")
    
    def initialize(self) -> bool:
        print("[OBD] Placeholder - not implemented yet")
        self.update_state(enabled=False, status="placeholder")
        return True
    
    def shutdown(self) -> bool:
        return True
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "status": "placeholder",
            "message": "OBD module not implemented yet",
        }