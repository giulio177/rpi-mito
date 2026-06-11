# Purpose
This directory contains the FastAPI-based backend application which serves REST and WebSocket APIs for the MITO Infotainment System. It acts as the orchestration layer between the frontend UI and the low-level hardware modules.

# Ownership
- Backend Developer / HAL Orchestrator Agent

# Local Contracts
- **Framework:** FastAPI with Uvicorn.
- **Data Schemas:** All request and response structures must use Pydantic models for validation.
- **Portability:** The server must launch and function in both mock mode (for macOS/Windows development) and real mode (on Raspberry Pi/Linux).
- **Communication:** Uses standard HTTP endpoints and a main WebSocket endpoint (`/ws`) for broadcasting system status updates (audio, Bluetooth, WiFi).

# Work Guidance
- When adding new modules or backend logic, register them in `backend/core/hal.py` so they are instantiated properly across different environments.
- Ensure all asynchronous calls are handled correctly within routes, and use mock interfaces to prevent system/hardware calls from blocking development on non-Linux devices.

# Verification
- Run tests via `tests/` directory once tests are defined.
- Run code quality/linters when applicable.

# Child DOX Index
- [modules/AGENTS.md](file:///Users/giulio/Desktop/Cursor/MITO-fr/backend/modules/AGENTS.md): Hardware Abstraction Layer (HAL) modules and peripheral implementations.
