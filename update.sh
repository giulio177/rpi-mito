#!/usr/bin/env bash
# =============================================================================
# MITO-fr OTA Update Script
# Eseguito da: sudo /home/pi/rpi-mito/update.sh
# Chiamato da: backend/modules/system/real.py -> update_app()
# =============================================================================
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
LOG_PREFIX="[MITO Update]"

echo "$LOG_PREFIX Avvio aggiornamento OTA..."
echo "$LOG_PREFIX Directory progetto: $PROJECT_DIR"

# --- 1. Git Pull ---
echo "$LOG_PREFIX Pulling da GitHub..."
cd "$PROJECT_DIR"
git fetch origin main
LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/main)

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "$LOG_PREFIX Nessun aggiornamento disponibile. Versione già aggiornata."
    exit 0
fi

git pull origin main
echo "$LOG_PREFIX Codice aggiornato."

# --- 2. Pulizia cache Python (evita bad magic number) ---
echo "$LOG_PREFIX Pulizia cache Python..."
find "$PROJECT_DIR" -name '*.pyc' -delete
find "$PROJECT_DIR" -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true

# --- 3. Aggiorna dipendenze Python (solo se requirements.txt è cambiato) ---
echo "$LOG_PREFIX Aggiornamento dipendenze Python..."
cd "$BACKEND_DIR"
if [ -f venv/bin/pip ]; then
    venv/bin/pip install -q -r requirements.txt
fi

# --- 4. Build Frontend (solo se i sorgenti sono cambiati) ---
echo "$LOG_PREFIX Build frontend Vue.js..."
cd "$FRONTEND_DIR"
npm install --silent
npm run build

echo "$LOG_PREFIX Frontend compilato."

# --- 5. Riavvio Servizi ---
echo "$LOG_PREFIX Riavvio servizi systemd..."
systemctl restart mito-backend.service
sleep 2
systemctl restart mito-kiosk.service

echo "$LOG_PREFIX Aggiornamento completato con successo!"
