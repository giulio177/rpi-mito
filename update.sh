#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_DIR/backend"
FRONTEND_DIR="$PROJECT_DIR/frontend"
LOG_PREFIX="[MITO Update]"

echo "$LOG_PREFIX Avvio aggiornamento OTA..."

cd "$PROJECT_DIR"
git fetch origin main
LOCAL_HASH=$(git rev-parse HEAD)
REMOTE_HASH=$(git rev-parse origin/main)

if [ "$LOCAL_HASH" = "$REMOTE_HASH" ]; then
    echo "$LOG_PREFIX Nessun aggiornamento disponibile."
    exit 0
fi

# Vediamo cosa cambierà per decidere cosa aggiornare
CHANGES=$(git diff --name-only $LOCAL_HASH $REMOTE_HASH)

git pull origin main
echo "$LOG_PREFIX Codice aggiornato."

# 1. Pulizia cache Python (Sempre sicura e veloce)
find "$PROJECT_DIR" -name '*.pyc' -delete
find "$PROJECT_DIR" -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true

# 2. Aggiornamento dipendenze Python (Solo se requirements.txt è cambiato)
if echo "$CHANGES" | grep -q "backend/requirements.txt"; then
    echo "$LOG_PREFIX Rilevato cambio requirements.txt. Aggiornamento pip..."
    cd "$BACKEND_DIR"
    venv/bin/pip install -q -r requirements.txt
else
    echo "$LOG_PREFIX Dipendenze Python invariate. Skip."
fi

# 3. Build Frontend (Solo se file frontend sono cambiati)
if echo "$CHANGES" | grep -qE "^frontend/src/|^frontend/index.html|^frontend/package"; then
    echo "$LOG_PREFIX Rilevato cambio frontend. Compilazione in corso..."
    cd "$FRONTEND_DIR"
    npm install --silent
    npm run build
    echo "$LOG_PREFIX Frontend compilato."
else
    echo "$LOG_PREFIX Frontend invariato. Skip build."
fi

# 4. Riavvio Servizi (Differito di 2 secondi per permettere al backend di rispondere alla UI)
echo "$LOG_PREFIX Riavvio servizi programmato tra 2 secondi..."
(sleep 2 && systemctl restart mito-backend.service && systemctl restart mito-kiosk.service) &

echo "$LOG_PREFIX Aggiornamento completato. Il sistema si riavvierà tra pochi istanti."

