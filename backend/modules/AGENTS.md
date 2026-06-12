# Purpose
This directory contains the Hardware Abstraction Layer (HAL) modules. These modules encapsulate hardware and OS-level integrations (e.g., ALSA audio, Bluez Bluetooth, network configuration, OBD-II data) and expose unified APIs.

# Ownership
- Hardware/HAL Developer Agent

# Local Contracts
- **HAL Pattern:** Each hardware capability must implement a dual interface:
  - `mock.py`: For development on macOS or systems without direct hardware access. Returns mock data and mimics state changes.
  - `real.py`: For execution on Linux/Raspberry Pi. Utilizes native tools, sysfs, dbus, or CLI commands.
- **Base Interface:** Module actions and interfaces must extend or inherit from the defined base class (e.g., `base.py` or `interface.py`).
- **Registration:** All modules must be registered and instantiated dynamically in [hal.py](file:///Users/giulio/Desktop/Cursor/MITO-fr/backend/core/hal.py) using `HALFactory`.
- **Default Routing:** The real audio module must dynamically discover and set the analog headphone jack/stereo output as the system-wide default sink on startup.
- **OTA Updates:** The system module must expose separate endpoints for code pulling (`pull_code`) and installer execution (`run_install`), allowing the frontend to drive the steps and request reboot confirmation from the user.
- **Persistence:** Saved Wi-Fi credentials and paired Bluetooth device MAC addresses must be stored in `saved_connections.json` inside the backend directory. Real modules must use this data on startup to automatically reconnect and re-trust devices across reboots.

# Work Guidance
- Never run production Linux commands (like `amixer`, `nmcli`, `bluetoothctl`) directly without ensuring the environment is `Linux` or checked via `real.py`.
- Mock modules must provide realistic behaviors (e.g. state retention, callbacks) to enable comprehensive frontend testing.

# Verification
- Manual verification of hardware states.
- Run mock configurations locally to verify UI bindings.

# Child DOX Index
This directory does not have further nested indices.
