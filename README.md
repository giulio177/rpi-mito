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


## 🚀 Installazione su Raspberry Pi (Headless Setup)

Questa guida presuppone che tu abbia già flashato **Raspberry Pi OS Lite (64-bit)** sulla tua scheda SD e che tu sia connesso al Raspberry Pi tramite SSH.

### 1. Aggiorna il sistema e installa Git
Per prima cosa, assicurati che la lista dei pacchetti sia aggiornata e installa `git` (necessario per scaricare il codice sorgente):
```bash
sudo apt update && sudo apt install git -y
```
2. Clona il Repository
Scarica il progetto direttamente nella cartella Home (~) del tuo utente:

```bash
cd ~
git clone [https://github.com/giulio177/rpi-mito.git](https://github.com/giulio177/rpi-mito.git)
```

3. Avvia lo Script di Installazione Automatico
Entra nella cartella appena clonata e rendi eseguibile lo script di installazione. Questo script si occuperà di configurare Kiosk mode, Bluetooth, PulseAudio, l'ambiente Python e i servizi di sistema:

```bash
cd MITO-fr
chmod +x install_mito.sh
sudo ./install_mito.sh
```
☕ Mettiti comodo: Lo script impiegherà alcuni minuti per scaricare tutte le dipendenze, compilare l'ambiente virtuale e configurare l'hardware dell'auto.

4. Riavvio Finale
Quando lo script avrà terminato con successo, ti chiederà di riavviare il sistema. Esegui:

```bash
sudo reboot
```
Al riavvio, il Raspberry Pi farà partire automaticamente il server backend (FastAPI) e l'interfaccia grafica a tutto schermo (tramite Chromium in Kiosk Mode) collegata allo schermo fisico!

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
