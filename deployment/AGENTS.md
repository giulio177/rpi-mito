# Purpose
This directory contains deployment scripts and systemd unit service files to run the MITO Infotainment System in production on Raspberry Pi hardware (using a kiosk-mode display and automatic backend daemon).

# Ownership
- DevOps / Deployment Agent

# Local Contracts
- Services must run as systemd services:
  - `mito-backend.service`: Runs the FastAPI server.
  - `mito-kiosk.service`: Runs the Chromium kiosk window pointing to the local server.
- Installation scripts must handle dependency configuration, hardware settings (e.g. system volume, Bluetooth, network interfaces), and daemon setup.

# Work Guidance
- Deployment scripts should handle updating via git cleanly, supporting OTA updates.
- Ensure scripts fail-safe and log errors clearly to journalctl.

# Verification
- Manual verification on target hardware by running install scripts.

# Child DOX Index
This directory does not have further nested indices.
