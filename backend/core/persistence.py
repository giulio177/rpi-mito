import os
import json
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# Resolve path to backend/saved_connections.json
CORE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.dirname(CORE_DIR)
PERSISTENCE_FILE = os.path.join(BACKEND_DIR, "saved_connections.json")

def load_data() -> Dict[str, Any]:
    """Load persistent data from JSON file."""
    if not os.path.exists(PERSISTENCE_FILE):
        return {"wifi": {}, "bluetooth": []}
    try:
        with open(PERSISTENCE_FILE, "r") as f:
            data = json.load(f)
            # Ensure proper structure
            if "wifi" not in data:
                data["wifi"] = {}
            if "bluetooth" not in data:
                data["bluetooth"] = []
            return data
    except Exception as e:
        logger.error(f"[Persistence] Error loading data: {e}")
        return {"wifi": {}, "bluetooth": []}

def save_data(data: Dict[str, Any]) -> None:
    """Save persistent data to JSON file."""
    try:
        with open(PERSISTENCE_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"[Persistence] Error saving data: {e}")

def get_saved_wifi() -> Dict[str, str]:
    """Get all saved wifi networks and passwords."""
    data = load_data()
    return data.get("wifi", {})

def save_wifi(ssid: str, password: Optional[str]) -> None:
    """Save a wifi network SSID and password."""
    data = load_data()
    data["wifi"][ssid] = password or ""
    save_data(data)
    logger.info(f"[Persistence] Wi-Fi network saved: {ssid}")

def delete_wifi(ssid: str) -> None:
    """Delete a saved wifi network."""
    data = load_data()
    if ssid in data["wifi"]:
        del data["wifi"][ssid]
        save_data(data)
        logger.info(f"[Persistence] Wi-Fi network deleted: {ssid}")

def get_remembered_bluetooth() -> List[str]:
    """Get all remembered/paired Bluetooth device MAC addresses."""
    data = load_data()
    return data.get("bluetooth", [])

def add_remembered_bluetooth(address: str) -> None:
    """Add a Bluetooth device address to remembered list."""
    address = address.upper()
    data = load_data()
    if address not in data["bluetooth"]:
        data["bluetooth"].append(address)
        save_data(data)
        logger.info(f"[Persistence] Bluetooth device remembered: {address}")

def remove_remembered_bluetooth(address: str) -> None:
    """Remove a Bluetooth device address from remembered list."""
    address = address.upper()
    data = load_data()
    if address in data["bluetooth"]:
        data["bluetooth"].remove(address)
        save_data(data)
        logger.info(f"[Persistence] Bluetooth device forgotten: {address}")
