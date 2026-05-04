# MITO Infotainment System 🏎️✨

A next-generation, ultra-premium Infotainment System interface designed specifically for Raspberry Pi touchscreens (1024x600). Built with modern web technologies, it features a fluid, hardware-accelerated "VisionOS/Glassmorphism" aesthetic, ensuring offline robustness and high-performance routing.

## 🌟 Key Features

- **Dynamic Hardware Scaling:** The UI is hard-locked to exactly `1024x600` and uses CSS `transform: scale()` to dynamically shrink or grow perfectly.
- **VisionOS Glassmorphism:** Deep translucent blurs, subtle border highlights, and rich ambient glows.
- **Offline-Ready First:** All primary assets, icons, and fonts are stored locally.
- **Dynamic Media Player:** lyrics mode, standard mode, and fixed action bars.
- **OTA Updates:** Integrated update system directly from GitHub.

## 🚀 Installazione su Raspberry Pi

```bash
sudo apt update && sudo apt install git -y
cd ~
git clone https://github.com/giulio177/rpi-mito.git
cd rpi-mito
chmod +x install_rpi-mito.sh
sudo ./install_rpi-mito.sh
sudo reboot
```

## 📋 Diagnostica e Debug (SSH)

Se riscontri problemi, usa questi comandi via SSH per capire cosa succede:

### Vedere i Log in tempo reale
*   **Backend (API/Hardware):** `sudo journalctl -u mito-backend.service -f`
*   **Frontend (Browser/Kiosk):** `sudo journalctl -u mito-kiosk.service -f`

### Gestione Aggiornamenti Manuali
Se l'aggiornamento dall'app fallisce o ci sono conflitti Git:
```bash
cd ~/rpi-mito
git reset --hard origin/main
sudo ./update.sh
```

### Comandi Rapidi di Servizio
*   **Riavvia solo l'App:** `sudo systemctl restart mito-backend.service`
*   **Riavvia lo Schermo:** `sudo systemctl restart mito-kiosk.service`
*   **Pulizia Cache Python:** `find . -name "*.pyc" -delete`

## 📂 Struttura Progetto

```text
frontend/        # Vue 3 + Vite (Interfaccia)
backend/         # FastAPI + Python (Logica Hardware)
install_...sh    # Script di installazione automatica
update.sh        # Script per aggiornamenti OTA
```

---
