#!/bin/bash
# BrainOS Development Startup Script
# Run this to start both frontend and backend together.

set -e

BACKEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/backend" && pwd)"
FRONTEND_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/frontend" && pwd)"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " BrainOS Dev Environment"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Kill any existing processes on our ports
echo "→ Clearing ports 3000 and 8000..."
lsof -ti :8000 | xargs kill -9 2>/dev/null || true
lsof -ti :3000 | xargs kill -9 2>/dev/null || true
sleep 1

# ── Start Backend ──────────────────────────────────────────────
echo "→ Starting FastAPI backend on http://127.0.0.1:8000 ..."
cd "$BACKEND_DIR"
if [ ! -d "venv" ]; then
  echo "  ERROR: venv not found in $BACKEND_DIR"
  echo "  Run: python3 -m venv venv && ./venv/bin/pip install -r requirements.txt"
  exit 1
fi
./venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!
echo "  Backend PID: $BACKEND_PID"

# Wait for backend to come up
echo "  Waiting for backend to be ready..."
for i in {1..20}; do
  if curl -sf http://127.0.0.1:8000/ > /dev/null 2>&1; then
    echo "  ✅ Backend is ready!"
    break
  fi
  sleep 0.5
done

# ── Start Frontend ─────────────────────────────────────────────
echo "→ Starting Next.js frontend on http://localhost:3000 ..."
cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
  echo "  Running npm install first..."
  npm install
fi
npm run dev &
FRONTEND_PID=$!
echo "  Frontend PID: $FRONTEND_PID"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " ✅ BrainOS is starting up!"
echo ""
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://127.0.0.1:8000"
echo "   API Docs: http://127.0.0.1:8000/docs"
echo ""
echo " Press Ctrl+C to stop all servers."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Trap Ctrl+C to cleanly kill both
cleanup() {
  echo ""
  echo "→ Stopping servers..."
  kill $BACKEND_PID 2>/dev/null || true
  kill $FRONTEND_PID 2>/dev/null || true
  lsof -ti :8000 | xargs kill -9 2>/dev/null || true
  lsof -ti :3000 | xargs kill -9 2>/dev/null || true
  echo "Done."
  exit 0
}
trap cleanup SIGINT SIGTERM

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
