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

    async def pull_code(self) -> Dict[str, Any]:
        """Perform a git pull (fetch & reset hard) and return if changes were found."""
        try:
            logger.info("[System] Fetching from git origin/main...")
            ok_fetch, _, fetch_err = await _run("git fetch origin main")
            if not ok_fetch:
                logger.error(f"[System] Git fetch failed: {fetch_err}")
                return {"success": False, "message": f"Errore Git fetch: {fetch_err}"}

            ok_local, local_hash, _ = await _run("git rev-parse HEAD")
            ok_remote, remote_hash, _ = await _run("git rev-parse origin/main")
            
            if ok_local and ok_remote and local_hash.strip() == remote_hash.strip():
                logger.info("[System] Git repository is already up to date.")
                return {
                    "success": True,
                    "changed": False,
                    "install_required": False,
                    "message": "Il codice del sistema è già aggiornato all'ultima versione."
                }
            
            # Check if install_rpi-mito.sh has changes before resetting
            logger.info("[System] Checking if install_rpi-mito.sh was modified...")
            diff_ok, diff_out, _ = await _run("git diff --name-only HEAD origin/main")
            install_required = False
            if diff_ok:
                changed_files = diff_out.splitlines()
                install_required = any("install_rpi-mito.sh" in f for f in changed_files)
                logger.info(f"[System] install_rpi-mito.sh changed: {install_required}")
            
            # Reset hard to origin/main to pull the updates
            logger.info("[System] Resetting repository to origin/main...")
            ok_reset, reset_out, reset_err = await _run("git reset --hard origin/main")
            if not ok_reset:
                logger.error(f"[System] Git reset hard failed: {reset_err}")
                return {"success": False, "message": f"Errore Git reset: {reset_err}"}

            return {
                "success": True,
                "changed": True,
                "install_required": install_required,
                "message": "Codice aggiornato scaricato con successo."
            }
        except Exception as e:
            logger.error(f"[System] pull_code error: {e}")
            return {"success": False, "message": str(e)}

    async def run_install(self) -> Dict[str, Any]:
        """Make the installer script executable and run it."""
        try:
            INSTALL_SCRIPT = os.path.join(PROJECT_DIR, "install_rpi-mito.sh")
            logger.info(f"[System] Setting execution permission on {INSTALL_SCRIPT}...")
            chmod_ok, _, chmod_err = await _run(f"chmod +x {INSTALL_SCRIPT}")
            if not chmod_ok:
                logger.error(f"[System] Chmod failed: {chmod_err}")
                return {"success": False, "message": f"Errore Chmod: {chmod_err}"}

            logger.info("[System] Running installer script (this might take a few minutes)...")
            proc = await asyncio.create_subprocess_shell(
                f"sudo {INSTALL_SCRIPT}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=PROJECT_DIR
            )
            
            try:
                # Allow up to 10 minutes for full install & build
                stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=600)
            except asyncio.TimeoutError:
                proc.kill()
                return {"success": False, "message": "Timeout: l'installazione ha impiegato più di 10 minuti."}

            output = stdout.decode().strip()
            if proc.returncode != 0:
                logger.error(f"[System] Installation script failed: {output}")
                return {"success": False, "message": f"Errore Installazione:\n{output}"}

            return {
                "success": True,
                "message": "Installazione completata con successo. Riavvio richiesto."
            }
        except Exception as e:
            logger.error(f"[System] run_install error: {e}")
            return {"success": False, "message": str(e)}

    async def _reboot_after_delay(self, delay: float):
        await asyncio.sleep(delay)
        logger.info("[System] Executing reboot command now.")
        await _run("sudo reboot")

    async def reboot_app(self) -> Dict[str, Any]:
        """Restart backend and kiosk services in the background (soft reload)."""
        try:
            # Schedule the service restart in a background task so we can send the HTTP response first
            asyncio.create_task(self._restart_services_task())
            return {"success": True, "message": "Riavvio dei servizi app avviato"}
        except Exception as e:
            logger.error(f"[System] reboot_app error: {e}")
            return {"success": False, "message": str(e)}

    async def _restart_services_task(self):
        logger.info("[System] Starting background application services restart...")
        await asyncio.sleep(1.0)
        # 1. Restart kiosk (Chromium)
        await _run(f"sudo systemctl restart {KIOSK_SERVICE}")
        # 2. Restart backend (this uvicorn process, which systemd will restart)
        await _run(f"sudo systemctl restart {BACKEND_SERVICE}")

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
