#!/usr/bin/env bash
set -euo pipefail

###############################################################################
# MITO-fr Car Infotainment Installer (Vue.js + FastAPI)
# Raspberry Pi OS Lite (Bookworm / Bullseye)
###############################################################################

if [[ "$EUID" -ne 0 ]]; then
  echo "Questo script va eseguito con sudo o da root."
  exit 1
fi

USER_NAME="${SUDO_USER:-pi}"
USER_UID="$(id -u "$USER_NAME")"
USER_HOME="$(getent passwd "$USER_NAME" | cut -d: -f6)"
PROJECT_DIR="$USER_HOME/rpi-mito" # Assicurati che la cartella si chiami così

if [[ ! -d "$PROJECT_DIR" ]]; then
  echo "Directory progetto non trovata: $PROJECT_DIR"
  echo "Clona prima il repository in $USER_HOME."
  exit 1
fi

echo "=========================================="
echo " Inizio Setup MITO-fr Infotainment"
echo " Utente: $USER_NAME"
echo " Directory: $PROJECT_DIR"
echo "=========================================="
echo

###############################################################################
# 1) Individua la partizione di boot
###############################################################################
if [[ -f /boot/firmware/cmdline.txt ]]; then
  BOOT_DIR="/boot/firmware"
elif [[ -f /boot/cmdline.txt ]]; then
  BOOT_DIR="/boot"
else
  echo "Impossibile trovare cmdline.txt."
  exit 1
fi

CMDLINE_FILE="$BOOT_DIR/cmdline.txt"
CONFIG_FILE="$BOOT_DIR/config.txt"

###############################################################################
# 2) Aggiornamento sistema e Pacchetti (Aggiunto Cage e Chromium)
###############################################################################
echo ">>> Aggiornamento sistema e installazione dipendenze..."
apt update && apt full-upgrade -y

apt install -y \
  git python3-venv python3-pip \
  ffmpeg \
  pulseaudio pulseaudio-module-bluetooth alsa-utils \
  bluez bluez-tools pi-bluetooth bluez-firmware \
  libdbus-1-dev libglib2.0-dev python3-dev \
  build-essential pkg-config \
  cage chromium \
  seatd nodejs npm # <-- Kiosk + Wayland seat + Node per build frontend

echo ">>> Pacchetti installati."
echo

###############################################################################
# 3) Configurazione Boot & HDMI 1024x600 (Mantenuto)
###############################################################################
echo ">>> Configurazione Boot e HDMI..."

EXTRA_CMDLINE="logo.nologo quiet loglevel=3 vt.global_cursor_default=0"
if ! grep -q "logo.nologo" "$CMDLINE_FILE"; then
  sed -i "1s|\$| ${EXTRA_CMDLINE}|" "$CMDLINE_FILE"
fi

# Abilita FKMS
if grep -q "dtoverlay=vc4-kms-v3d" "$CONFIG_FILE"; then
  sed -i 's/dtoverlay=vc4-kms-v3d/dtoverlay=vc4-fkms-v3d/' "$CONFIG_FILE"
elif ! grep -q "dtoverlay=vc4-fkms-v3d" "$CONFIG_FILE"; then
  echo "dtoverlay=vc4-fkms-v3d" >> "$CONFIG_FILE"
fi

# Risoluzione Custom 1024x600
if ! grep -q "hdmi_cvt=1024 600 60 6 0 0 0" "$CONFIG_FILE"; then
cat >> "$CONFIG_FILE" << 'EOF'
# MITO-fr Display
hdmi_force_hotplug=1
hdmi_group=2
hdmi_mode=87
hdmi_cvt=1024 600 60 6 0 0 0
EOF
fi

# Audio
if grep -q '^dtparam=audio=' "$CONFIG_FILE"; then
  sed -i 's/^dtparam=audio=.*/dtparam=audio=on/' "$CONFIG_FILE"
else
  echo 'dtparam=audio=on' >> "$CONFIG_FILE"
fi

###############################################################################
# 4) Configurazione Bluetooth HW & SW (Mantenuto - Cruciale)
###############################################################################
echo ">>> Configurazione Bluetooth e PulseAudio..."

# Fix Hardware
sed -i '/dtoverlay=disable-bt/d' "$CONFIG_FILE"
if ! grep -q "enable_uart=1" "$CONFIG_FILE"; then echo "enable_uart=1" >> "$CONFIG_FILE"; fi
command -v rfkill &> /dev/null && rfkill unblock bluetooth || true
systemctl enable hciuart || true

# Configurazione PulseAudio BT
cat >/etc/pulse/default.pa <<'EOF'
load-module module-bluetooth-policy
load-module module-bluetooth-discover
EOF

# Configurazione BlueZ (main.conf)
if [[ ! -f /etc/bluetooth/main.conf ]]; then echo "[General]" > /etc/bluetooth/main.conf; fi
sed -i '/^\[General\]/a Class = 0x200420\nDiscoverableTimeout = 30\nPairableTimeout = 0\nJustWorksRepairing = always\nAutoEnable = true\nControllerMode = bredr\nName = MITO-Infotainment' /etc/bluetooth/main.conf

# Agente BlueZ (Auto-pairing)
cat >/etc/systemd/system/bt-auto-pair.service <<EOF
[Unit]
Description=Bluetooth Auto-Accept Agent
After=bluetooth.service
Requires=bluetooth.service

[Service]
Type=simple
ExecStart=/usr/bin/bt-agent -c NoInputNoOutput
Restart=always
RestartSec=2

[Install]
WantedBy=multi-user.target
EOF
systemctl enable --now bt-auto-pair.service

###############################################################################
# 5) Gruppi, Seatd, Virtual Environment e Build Frontend
###############################################################################
# Aggiungi l'utente ai gruppi necessari per Wayland/Cage
usermod -aG video,input,audio,bluetooth,tty,render "$USER_NAME" || true

# Abilita seatd per i permessi del compositor Wayland
systemctl enable --now seatd || true
# Aggiungi l'utente al gruppo seat (necessario per cage)
gpasswd -a "$USER_NAME" seat || true

# --- 5.1 Pulizia cache Python (evita errori "bad magic number" da file .pyc del Mac) ---
echo ">>> Pulizia cache Python..."
find "$PROJECT_DIR" -name '*.pyc' -delete
find "$PROJECT_DIR" -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
echo ">>> Cache Python rimossa."

# --- 5.2 Build del Frontend ---
echo ">>> Build Frontend (npm install && npm run build)..."
sudo -u "$USER_NAME" bash -lc "
  set -e
  cd '$PROJECT_DIR/frontend'
  npm install
  npm run build
"
echo ">>> Frontend compilato in frontend/dist."

# --- 5.3 Setup Virtual Environment Python ---
echo ">>> Setup Virtual Environment Python..."
sudo -u "$USER_NAME" bash -lc "
  set -e
  cd '$PROJECT_DIR/backend'
  python3 -m venv venv
  source venv/bin/activate
  pip install --upgrade pip
  if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
"

###############################################################################
# 6) Creazione Servizi Systemd (NOVITÀ: Split Backend / Frontend)
###############################################################################
echo ">>> Creazione Servizi Systemd..."

# --- 6.1 BACKEND SERVICE (FastAPI) ---
cat >/etc/systemd/system/mito-backend.service <<EOF
[Unit]
Description=MITO-fr FastAPI Backend
After=network.target bluetooth.service pulseaudio.service

[Service]
Type=simple
User=$USER_NAME
Group=$USER_NAME
# WorkingDirectory punta a backend/ così uvicorn trova main:app senza prefissi
WorkingDirectory=$PROJECT_DIR/backend
Environment=PYTHONUNBUFFERED=1
Environment=DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$USER_UID/bus

ExecStart=$PROJECT_DIR/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# --- 6.2 FRONTEND KIOSK SERVICE (Cage + Chromium) ---
cat >/etc/systemd/system/mito-kiosk.service <<EOF
[Unit]
Description=MITO-fr Web UI Kiosk
After=mito-backend.service seatd.service network.target
Wants=mito-backend.service

[Service]
Type=simple
User=$USER_NAME
Group=$USER_NAME
WorkingDirectory=$PROJECT_DIR
Environment=WLR_LIBINPUT_NO_DEVICES=1
Environment=XDG_RUNTIME_DIR=/run/user/1000
Environment=HOME=/home/$USER_NAME

# Avvia Chromium in kiosk mode senza popup traduttore
ExecStart=/usr/bin/cage -- /usr/bin/chromium \
  --kiosk \
  --no-sandbox \
  --disable-infobars \
  --start-maximized \
  --overscroll-history-navigation=0 \
  --disable-translate \
  --disable-features=Translate \
  http://localhost:8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable mito-backend.service
systemctl enable mito-kiosk.service

###############################################################################
# 6.3) Chromium Policy (disabilita popup traduttore e altre UI indesiderate)
###############################################################################
mkdir -p /etc/chromium/policies/managed
cat >/etc/chromium/policies/managed/mito_kiosk.json <<'EOF'
{
  "TranslateEnabled": false,
  "BrowserSignin": 0,
  "SyncDisabled": true,
  "MetricsReportingEnabled": false,
  "DefaultBrowserSettingEnabled": false
}
EOF
echo ">>> Policy Chromium configurata."

###############################################################################
# 7) Secure Shutdown & Cleanup
###############################################################################
if ! grep -q "disable_splash=1" "$CONFIG_FILE"; then echo "disable_splash=1" >> "$CONFIG_FILE"; fi
if ! grep -q "boot_delay=0" "$CONFIG_FILE"; then echo "boot_delay=0" >> "$CONFIG_FILE"; fi
if ! grep -q "gpio-poweroff" "$CONFIG_FILE"; then
    echo "dtoverlay=gpio-poweroff,gpiopin=17,active_low=1" >> "$CONFIG_FILE"
fi

###############################################################################
# 8) Permessi Sudo per il Backend (Update, Spegnimento, Riavvio)
###############################################################################
echo ">>> Configurazione permessi sudo per $USER_NAME..."

# Rendi eseguibile lo script di update
chmod +x "$PROJECT_DIR/update.sh"

cat >/etc/sudoers.d/mito_permissions <<EOF
# MITO-fr: permessi per operazioni di sistema senza password
$USER_NAME ALL=(ALL) NOPASSWD: $PROJECT_DIR/update.sh
$USER_NAME ALL=(ALL) NOPASSWD: /sbin/poweroff
$USER_NAME ALL=(ALL) NOPASSWD: /sbin/reboot
$USER_NAME ALL=(ALL) NOPASSWD: /bin/systemctl restart mito-kiosk.service
$USER_NAME ALL=(ALL) NOPASSWD: /bin/systemctl restart mito-backend.service
EOF
chmod 0440 /etc/sudoers.d/mito_permissions
echo "Permessi sudo configurati."


echo ">>> INSTALLAZIONE COMPLETATA."
echo "I servizi 'mito-backend' e 'mito-kiosk' sono installati."
echo "Ora esegui: sudo reboot"