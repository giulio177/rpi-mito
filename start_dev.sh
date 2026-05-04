#!/bin/bash

echo "🚗 Avvio MITO Infotainment Dev Server..."

# Memorizza la directory root
ROOT_DIR=$(cd "$(dirname "$0")" && pwd)

# 1. Avvia Backend in background
echo "⏳ Avvio Backend FastAPI..."
cd "$ROOT_DIR/backend"
source venv/bin/activate
PYTHONPATH=. python main.py &
BACKEND_PID=$!

# 2. Attendi 2 secondi per far avviare il backend
sleep 2

# 3. Avvia Frontend in foreground
echo "🎨 Avvio Frontend Vue/Vite..."
cd "$ROOT_DIR/frontend"

npm run dev -- --open

# 4. Funzione per chiudere tutto in modo pulito
cleanup() {
    echo ""
    echo "🛑 Chiusura dei server in corso..."
    kill $BACKEND_PID 2>/dev/null
    echo "✅ Chiusura completata. A presto!"
    exit
}

# Cattura i segnali (CTRL+C)
# trap cleanup SIGINT SIGTERM EXIT

# Mantieni lo script in esecuzione 
# wait