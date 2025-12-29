#!/bin/bash
# Start both backend and frontend servers for local development
# Usage: ./scripts/start-servers.sh

set -e

# Get repository root (one level up from scripts directory)
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "🚀 Starting SpecBot Servers..."
echo ""

# Check if backend virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "❌ Backend virtual environment not found!"
    echo "   Run: cd backend && python -m venv venv && venv/bin/pip install -r requirements.txt"
    exit 1
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "❌ Frontend dependencies not installed!"
    echo "   Run: cd frontend && npm install"
    exit 1
fi

# Check if frontend .env exists
if [ ! -f "frontend/.env" ]; then
    echo "⚠️  Frontend .env not found, creating from .env.example..."
    cp frontend/.env.example frontend/.env
fi

echo "✅ Prerequisites check passed"
echo ""
echo "📡 Starting backend server (port 8000)..."
echo "   Logs: backend/server.log"
echo ""

# Start backend in background
cd backend
PYTHONPATH="${REPO_ROOT}/backend" venv/bin/python main.py > server.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to be ready..."
sleep 3

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ Backend failed to start! Check backend/server.log"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo "✅ Backend running on http://localhost:8000"
echo "   API docs: http://localhost:8000/docs"
echo ""
echo "🎨 Starting frontend server (port 5173)..."
echo ""

# Start frontend (this will run in foreground)
cd frontend
npm run dev

# Cleanup on exit
trap "echo ''; echo '🛑 Shutting down servers...'; kill $BACKEND_PID 2>/dev/null || true; exit 0" EXIT INT TERM
