# Purpose
This directory contains automated tests for both the Python FastAPI backend and the frontend application (including e2e tests).

# Ownership
- Test Engineer / QA Agent

# Local Contracts
- Tests are divided into `backend` tests and `e2e` tests.
- Backend tests should test api routes, HAL factory registry logic, and module mock outputs.
- E2E tests should test UI routing, dashboard components, and mock websocket integration.

# Work Guidance
- Ensure tests run cleanly against mock configurations so they can run in CI pipelines without requiring Raspberry Pi hardware.

# Verification
- Command to run backend tests (once tests are implemented): e.g., `pytest` from the root or `backend` folder.

# Child DOX Index
This directory does not have further nested indices.
