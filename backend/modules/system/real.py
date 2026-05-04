import asyncio
import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Path to the project root (two levels up from this file)
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
FRONTEND_PACKAGE_JSON = os.path.join(PROJECT_DIR, "frontend", "package.json")
KIOSK_SERVICE = "mito-kiosk.service"
BACKEND_SERVICE = "mito-backend.service"


async def _run(cmd: str) -> tuple[bool, str, str]:
    """Run a shell command asynchronously. Returns (success, stdout, stderr)."""
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=PROJECT_DIR
    )
    stdout, stderr = await proc.communicate()
    return proc.returncode == 0, stdout.decode().strip(), stderr.decode().strip()


class RealSystemModule:
    """Manages OTA updates and system power state via subprocess commands."""

    def initialize(self) -> bool:
        logger.info("[System] Initialized")
        return True

    def shutdown(self) -> bool:
        return True

    def get_version(self) -> str:
        """Read version from frontend/package.json, fallback to '0.0.0'."""
        try:
            with open(FRONTEND_PACKAGE_JSON, "r") as f:
                data = json.load(f)
                return data.get("version", "0.0.0")
        except Exception as e:
            logger.warning(f"[System] Could not read version: {e}")
            return "0.0.0"

    async def get_git_info(self) -> Dict[str, Any]:
        """Return current git commit hash and branch."""
        try:
            ok_hash, commit, _ = await _run("git rev-parse --short HEAD")
            ok_branch, branch, _ = await _run("git rev-parse --abbrev-ref HEAD")
            return {
                "commit": commit if ok_hash else "unknown",
                "branch": branch if ok_branch else "unknown",
            }
        except Exception as e:
            logger.error(f"[System] git info error: {e}")
            return {"commit": "unknown", "branch": "unknown"}

    async def update_app(self) -> Dict[str, Any]:
        """Pull latest changes from origin and restart the kiosk service."""
        try:
            ok, stdout, stderr = await _run("git pull origin main")
            if not ok:
                logger.error(f"[System] git pull failed: {stderr}")
                return {"success": False, "message": stderr}

            # Restart the kiosk (frontend) service so the new build is served
            ok_svc, _, svc_err = await _run(f"sudo systemctl restart {KIOSK_SERVICE}")
            if not ok_svc:
                logger.warning(f"[System] kiosk restart failed: {svc_err}")

            return {"success": True, "message": stdout}
        except Exception as e:
            logger.error(f"[System] update_app error: {e}")
            return {"success": False, "message": str(e)}

    async def reboot_app(self) -> Dict[str, Any]:
        """Restart only the kiosk service (soft reload)."""
        try:
            ok, _, stderr = await _run(f"sudo systemctl restart {KIOSK_SERVICE}")
            if not ok:
                logger.error(f"[System] reboot_app failed: {stderr}")
                return {"success": False, "message": stderr}
            return {"success": True, "message": "Kiosk service restarted"}
        except Exception as e:
            logger.error(f"[System] reboot_app error: {e}")
            return {"success": False, "message": str(e)}

    async def reboot_system(self) -> Dict[str, Any]:
        """Schedule a full system reboot (non-blocking)."""
        try:
            # Fire and forget — reboot will happen in ~2 s so we can still respond
            asyncio.create_task(_run("sudo reboot"))
            return {"success": True, "message": "System reboot initiated"}
        except Exception as e:
            logger.error(f"[System] reboot_system error: {e}")
            return {"success": False, "message": str(e)}

    async def shutdown_system(self) -> Dict[str, Any]:
        """Schedule a full system poweroff (non-blocking)."""
        try:
            asyncio.create_task(_run("sudo poweroff"))
            return {"success": True, "message": "System shutdown initiated"}
        except Exception as e:
            logger.error(f"[System] shutdown_system error: {e}")
            return {"success": False, "message": str(e)}
