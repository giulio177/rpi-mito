# Purpose
This directory houses the frontend application of the MITO Infotainment System, built using Vue 3, Vite, TypeScript, and Tailwind CSS. It is optimized for Raspberry Pi touchscreen displays.

# Ownership
- Frontend Developer Agent

# Local Contracts
- **Display Target:** Fixed layout locked to exactly `1024x600`. Uses CSS scaling to match different screens.
- **Styling:** VisionOS Glassmorphism design language (translucent background blurs, ambient glows, harmonious dark palettes).
- **Offline First:** All fonts, icons, and static assets must be bundled locally. No external web CDN loads are permitted.
- **Input Methods:** Must support virtual keyboard inputs for touchscreens.
- **State Management:** Pinia stores for sync with backend endpoints (`audio`, `bluetooth`, `wifi`).
- **Volume Control:** The bottom navigation bar controls the global system volume and implements a 2-second long-press toggle on the volume down button for muting/unmuting.
- **OTA Update Flow:** The system update sequence is divided into multiple sequential steps shown dynamically to the user: Git pull, installation script execution (only if `install_rpi-mito.sh` has changed), and a confirmation popup asking the user before rebooting the system or restarting the application.
- **Persistence UI:** Display saved Wi-Fi networks and paired Bluetooth devices, letting the user disconnect or "forget" them from memory via interactive context dropdown menus.

# Work Guidance
- Use the VirtualKeyboard component for inputs to ensure usability on a Pi touchscreen.
- Verify that backdrop-filter blurs run smoothly on low-power hardware. If performance degrades, provide fallback styling.
- All styles should match the defined aesthetic tokens in `frontend/src/style.css` and the Tailwind config.

# Verification
- Run the dev server with `npm run dev` inside `frontend/`.
- Ensure build compatibility using `npm run build`.

# Child DOX Index
This directory does not have further nested indices.
