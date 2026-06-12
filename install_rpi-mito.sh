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
  bluez bluez-tools pi-bluetooth bluez-firmware bluez-alsa-utils \
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

# Configurazione PulseAudio BT (Sink + Source)
if [[ -f /etc/pulse/default.pa ]]; then
  if ! grep -q 'module-bluetooth-discover' /etc/pulse/default.pa; then
    cat >>/etc/pulse/default.pa <<'EOF'

### Bluetooth A2DP Support
load-module module-bluetooth-policy
load-module module-bluetooth-discover
load-module module-switch-on-connect
EOF
  fi
fi

# Configurazione BlueZ (main.conf)
if [[ ! -f /etc/bluetooth/main.conf ]]; then echo "[General]" > /etc/bluetooth/main.conf; fi
# Rimuoviamo eventuali righe duplicate e aggiungiamo le nostre
sed -i '/Class =/d' /etc/bluetooth/main.conf
sed -i '/DiscoverableTimeout =/d' /etc/bluetooth/main.conf
sed -i '/Name =/d' /etc/bluetooth/main.conf
sed -i '/ControllerVersion =/d' /etc/bluetooth/main.conf
sed -i '/Experimental =/d' /etc/bluetooth/main.conf
sed -i '/^\[General\]/a Class = 0x240404\nDiscoverableTimeout = 120\nPairableTimeout = 0\nJustWorksRepairing = always\nAutoEnable = true\nControllerMode = bredr\nControllerVersion = 1.6\nExperimental = true\nName = MITO-fr' /etc/bluetooth/main.conf

# Abilita le funzionalità sperimentali di bluetoothd per AVRCP 1.6 / BIP (necessario per Cover Art)
if [[ -f /lib/systemd/system/bluetooth.service ]]; then
  sed -i 's|ExecStart=/usr/libexec/bluetooth/bluetoothd|ExecStart=/usr/libexec/bluetooth/bluetoothd -E|g' /lib/systemd/system/bluetooth.service
  sed -i 's|ExecStart=/usr/lib/bluetooth/bluetoothd|ExecStart=/usr/lib/bluetooth/bluetoothd -E|g' /lib/systemd/system/bluetooth.service
fi




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

# Configurazione PulseAudio BT (Sink + Source) e driver locali per jack audio
cat >/etc/pulse/system.pa <<'EOF'
### Ripristino volume e stati
load-module module-device-restore
load-module module-stream-restore
load-module module-card-restore

### Rilevamento schede audio locali (compreso Jack analogico)
.ifexists module-udev-detect.so
load-module module-udev-detect tsched=0
.endif

### Protocollo nativo per client unix
load-module module-native-protocol-unix auth-anonymous=1

### Supporto Bluetooth
.ifexists module-bluetooth-policy.so
load-module module-bluetooth-policy
.endif
.ifexists module-bluetooth-discover.so
load-module module-bluetooth-discover
.endif
.ifexists module-switch-on-connect.so
load-module module-switch-on-connect
.endif
EOF

# Servizio PulseAudio (necessario per audio bluetooth in background)
cat >/etc/systemd/system/pulseaudio.service <<EOF
[Unit]
Description=PulseAudio System Daemon
After=bluetooth.service
Wants=bluetooth.service

[Service]
Type=simple
ExecStart=/usr/bin/pulseaudio --system --disallow-exit --realtime --log-target=journal
Restart=always

[Install]
WantedBy=multi-user.target
EOF
systemctl enable --now pulseaudio.service

# Configurazione client PulseAudio per usare il daemon di sistema
cat >/etc/pulse/client.conf <<'EOF'
default-server = unix:/var/run/pulse/native
autospawn = no
EOF

###############################################################################
# 5) Gruppi, Seatd, Virtual Environment e Build Frontend
###############################################################################
echo ">>> Configurazione permessi hardware e gruppi..."
usermod -aG video,input,audio,bluetooth,tty,render,pulse-access,netdev "$USER_NAME" || true
# Assicura che l'utente pulse (daemon di sistema) abbia accesso ad audio e bluetooth
usermod -aG audio,bluetooth pulse || true

# Abilita seatd per i permessi del compositor Wayland
systemctl enable --now seatd || true
gpasswd -a "$USER_NAME" seat || true

# Attivazione OBEX per il trasferimento copertine
loginctl enable-linger "$USER_NAME" || true
sudo -u "$USER_NAME" XDG_RUNTIME_DIR="/run/user/$USER_UID" DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$USER_UID/bus" systemctl --user enable obex || true
sudo -u "$USER_NAME" XDG_RUNTIME_DIR="/run/user/$USER_UID" DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$USER_UID/bus" systemctl --user start obex || true

# --- 5.0 Ripristino Proprietario Progetto ---
echo ">>> Ripristino proprietario cartella di progetto..."
chown -R "$USER_NAME:$USER_NAME" "$PROJECT_DIR"

# Assicura che esista la cartella Downloads per OBEX (altrimenti obexd restituisce "Not Acceptable")
sudo -u "$USER_NAME" mkdir -p "$USER_HOME/Downloads"

# --- 5.1 Pulizia cache Python (evita errori "bad magic number" da file .pyc del Mac) ---
echo ">>> Pulizia cache Python..."
find "$PROJECT_DIR" -name '*.pyc' -delete
find "$PROJECT_DIR" -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true

# --- 5.2 Build del Frontend ---
echo ">>> Build Frontend (npm install && npm run build)..."
sudo -u "$USER_NAME" bash -lc "
  set -e
  cd '$PROJECT_DIR/frontend'
  npm install
  npm run build
"

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
# 6) Creazione Servizi Systemd
###############################################################################
echo ">>> Creazione Servizi Systemd..."

# --- 6.1 BACKEND SERVICE ---
cat >/etc/systemd/system/mito-backend.service <<EOF
[Unit]
Description=MITO-fr FastAPI Backend
After=network.target bluetooth.service pulseaudio.service

[Service]
Type=simple
User=$USER_NAME
Group=$USER_NAME
WorkingDirectory=$PROJECT_DIR/backend
Environment=PYTHONUNBUFFERED=1
Environment=DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/$USER_UID/bus
Environment=PULSE_SERVER=unix:/var/run/pulse/native
ExecStart=$PROJECT_DIR/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3
TimeoutStopSec=5s


[Install]
WantedBy=multi-user.target
EOF

# --- 6.2 FRONTEND KIOSK SERVICE ---
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
Environment=PULSE_SERVER=unix:/var/run/pulse/native
ExecStart=/usr/bin/cage -- /usr/bin/chromium \
  --kiosk --no-sandbox --disable-infobars --start-maximized \
  --overscroll-history-navigation=0 --disable-translate --disable-features=Translate \
  http://localhost:8000
Restart=always
RestartSec=5
TimeoutStopSec=5s


[Install]
WantedBy=multi-user.target
EOF

# --- 6.3 Chromium Policy (No Translate) ---
mkdir -p /etc/chromium/policies/managed
cat >/etc/chromium/policies/managed/mito_kiosk.json <<'EOF'
{
  "TranslateEnabled": false,
  "BrowserSignin": 0,
  "SyncDisabled": true,
  "MetricsReportingEnabled": false
}
EOF

systemctl daemon-reload
systemctl enable mito-backend.service mito-kiosk.service

###############################################################################
# 7) Permessi Sudo e update.sh
###############################################################################
echo ">>> Configurazione update.sh e permessi sudo..."

# Rendi eseguibile lo script di update
chmod +x "$PROJECT_DIR/update.sh"

cat >/etc/sudoers.d/mito_permissions <<EOF
# Permessi per l'infotainment senza password
$USER_NAME ALL=(ALL) NOPASSWD: $PROJECT_DIR/update.sh
$USER_NAME ALL=(ALL) NOPASSWD: $PROJECT_DIR/install_rpi-mito.sh
$USER_NAME ALL=(ALL) NOPASSWD: /usr/sbin/reboot
$USER_NAME ALL=(ALL) NOPASSWD: /usr/sbin/poweroff
$USER_NAME ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart mito-kiosk.service
$USER_NAME ALL=(ALL) NOPASSWD: /usr/bin/systemctl restart mito-backend.service
EOF
chmod 0440 /etc/sudoers.d/mito_permissions

# 8) Boot & Splash Cleanup
if ! grep -q "disable_splash=1" "$CONFIG_FILE"; then echo "disable_splash=1" >> "$CONFIG_FILE"; fi
if ! grep -q "boot_delay=0" "$CONFIG_FILE"; then echo "boot_delay=0" >> "$CONFIG_FILE"; fi

echo "=========================================="
echo " SETUP COMPLETATO CON SUCCESSO"
echo " Ora esegui: sudo reboot"
echo "=========================================="