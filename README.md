# MITO Infotainment System 🚗✨

A next-generation, ultra-premium Infotainment System interface designed specifically for Raspberry Pi touchscreens (1024x600). Built with modern web technologies, it features a fluid, hardware-accelerated "VisionOS/Glassmorphism" aesthetic, ensuring offline robustness and high-performance routing.

## 🌟 Key Features

- **Dynamic Hardware Scaling:** The UI is hard-locked to exactly `1024x600` (native RPi display aspect ratio) and uses CSS `transform: scale()` to dynamically shrink or grow perfectly on any browser window without breaking the grid.
- **VisionOS Glassmorphism:** Deep translucent blurs (`backdrop-blur-2xl`), subtle border highlights (`border-white/10`), and rich ambient glows mimicking high-end car displays.
- **Offline-Ready First:** All primary assets, icons (Material Symbols), and placeholder images (`song-placeholder.png`) are stored locally. CSS gradients replace heavy external images where possible to ensure instant load times without internet dependency.
- **Interactive Dock Navigation:** A fluid bottom dock with active routing indicators, reactive volume slider, and haptic-ready UI buttons.
- **Dynamic Media Player (`MusicView`):**
  - **Standard Mode:** Large gorgeous album art with full playback controls.
  - **Lyrics Mode:** Split-screen layout displaying active lyrics alongside a compact, carefully balanced mini-player.
  - **Fixed Action Bar:** Top-right utility buttons remain rigidly absolute to build "muscle memory" for the driver.
- **OBD Telemetry Ready:** Interface structure built to instantly accept WebSocket data for real-time KM/H and sensor tracking.

## 🛠 Tech Stack

- **Framework:** [Vue 3](https://vuejs.org/) (Composition API) + [Vite 6](https://vitejs.dev/)
- **Styling:** [Tailwind CSS v4](https://tailwindcss.com/)
- **Language:** [TypeScript](https://www.typescriptlang.org/)
- **Routing:** Vue Router
- **Typography & Icons:** Space Grotesk, Inter, and Google Material Symbols.

## 🚀 Getting Started

### Prerequisites
Make sure you have [Node.js](https://nodejs.org/) installed on your machine.

### Installation

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```
   *Alternatively, run `./start_dev.sh` from the project root to spin up both the backend and frontend simultaneously.*

## 📂 Project Structure

```text
frontend/
├── src/
│   ├── assets/          # Local offline images (e.g., song-placeholder.png)
│   ├── components/
│   │   ├── common/      # Reusable UI (TopBar, BottomNav)
│   │   ├── layout/      # Main layout engine (MainLayout.vue with 1024x600 scaler)
│   │   └── views/       # Application views (Home, Music, Library, OBD, Maps, Settings)
│   ├── router/          # Vue Router configuration
│   ├── App.vue          # Root Vue component
│   ├── main.ts          # Application entry point
│   └── style.css        # Global Tailwind v4 config & Custom CSS
├── index.html           # HTML template with Font/Icon imports
├── tailwind.config.js   # Tailwind rules & content paths
└── package.json         # Dependencies & scripts
```

## 🎨 Design Philosophy

The MITO interface avoids flat, generic MVP designs. It prioritizes a **"wow" factor** by leveraging:
- Carefully tailored color palettes (deep purples `#490080`, soft lilacs `#ddb7ff`, pitch blacks `#0e0e0e`).
- `mask-image` for smooth fading text gradients (used heavily in Lyrics mode).
- Complete uncoupling of components from the main wrapper to allow ambient background layers to shine through transparently.

## 🤝 Next Steps (Hardware Integration)
- Connect `wsManager` WebSockets to bind real `audio/status` and `obd/status` backends.
- Replace mock data in `TopBar.vue` (Clock, Wi-Fi, Bluetooth) with live Raspberry Pi system states.
