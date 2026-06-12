"""Mock SystemModule for local development (macOS/Windows)."""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class MockSystemModule:
    def initialize(self) -> bool:
        logger.info("[MockSystem] Initialized")
        return True

    def shutdown(self) -> bool:
        return True

    def get_version(self) -> str:
        return "0.0.0-dev"

    async def get_git_info(self) -> Dict[str, Any]:
        return {"commit": "mock-abc123", "branch": "main"}

    async def pull_code(self) -> Dict[str, Any]:
        logger.info("[MockSystem] pull_code called")
        return {
            "success": True,
            "changed": True,
            "install_required": True,
            "message": "Codice mock scaricato con successo. Installazione richiesta. (mock)"
        }

    async def run_install(self) -> Dict[str, Any]:
        logger.info("[MockSystem] run_install called")
        return {
            "success": True,
            "message": "Installazione mock completata con successo. (mock)"
        }

    async def reboot_app(self) -> Dict[str, Any]:
        logger.info("[MockSystem] reboot_app called (no-op in dev)")
        return {"success": True, "message": "Kiosk service restarted. (mock)"}

    async def reboot_system(self) -> Dict[str, Any]:
        logger.info("[MockSystem] reboot_system called (no-op in dev)")
        return {"success": True, "message": "System reboot initiated. (mock)"}

    async def shutdown_system(self) -> Dict[str, Any]:
        logger.info("[MockSystem] shutdown_system called (no-op in dev)")
        return {"success": True, "message": "System shutdown initiated. (mock)"}
