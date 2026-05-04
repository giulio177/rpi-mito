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

RESTART_BACKEND=false
RESTART_KIOSK=false

# 1. Pulizia cache Python
find "$PROJECT_DIR" -name '*.pyc' -delete
find "$PROJECT_DIR" -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true

# 2. Aggiornamento dipendenze Python
if echo "$CHANGES" | grep -qE "backend/requirements.txt|backend/main.py|backend/modules/|backend/core/"; then
    echo "$LOG_PREFIX Rilevato cambio backend."
    RESTART_BACKEND=true
    if echo "$CHANGES" | grep -q "backend/requirements.txt"; then
        cd "$BACKEND_DIR"
        venv/bin/pip install -q -r requirements.txt
    fi
fi

# 3. Build Frontend
if echo "$CHANGES" | grep -qE "^frontend/src/|^frontend/index.html|^frontend/package"; then
    echo "$LOG_PREFIX Rilevato cambio frontend."
    RESTART_KIOSK=true
    cd "$FRONTEND_DIR"
    npm install --silent
    npm run build
fi

# 4. Scriviamo il manifesto per l'app
cat > "$PROJECT_DIR/update_manifest.json" <<EOF
{
  "restart_backend": $RESTART_BACKEND,
  "restart_kiosk": $RESTART_KIOSK,
  "changes": "$(echo "$CHANGES" | tr '\n' ' ' | cut -c1-100)..."
}
EOF

echo "$LOG_PREFIX Aggiornamento scaricato. Manifesto creato."


