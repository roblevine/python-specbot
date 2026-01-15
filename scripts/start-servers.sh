#!/bin/bash
# Start both backend and frontend servers for local development
# Usage: ./scripts/start-servers.sh [options]
#
# Options:
#   --use-tmux          Start servers in tmux panes with live console output
#   --vertical          Use vertical (top/bottom) pane layout (default: horizontal/side-by-side)
#   --help              Show this help message

set -e

# Parse arguments
USE_TMUX=false
TMUX_LAYOUT="horizontal"

while [[ $# -gt 0 ]]; do
    case $1 in
        --use-tmux)
            USE_TMUX=true
            shift
            ;;
        --vertical)
            TMUX_LAYOUT="vertical"
            shift
            ;;
        --help)
            echo "Usage: ./scripts/start-servers.sh [options]"
            echo ""
            echo "Options:"
            echo "  --use-tmux    Start servers in tmux panes with live console output"
            echo "  --vertical    Use vertical (top/bottom) pane layout (default: horizontal/side-by-side)"
            echo "  --help        Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Get repository root (one level up from scripts directory)
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo "🚀 Starting SpecBot Servers..."
echo ""

# Check if backend virtual environment exists
if [ ! -d "backend/.venv" ]; then
    echo "❌ Backend virtual environment not found!"
    echo "   Run: cd backend && python -m venv .venv && .venv/bin/pip install -r requirements.txt"
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

if [ "$USE_TMUX" = true ]; then
    # Check if tmux is actually available
    if ! command -v tmux &> /dev/null; then
        echo "❌ --use-tmux specified but tmux is not installed!"
        echo "   Install tmux or run without --use-tmux flag"
        exit 1
    fi
    
    echo "📺 Starting servers in tmux session ($TMUX_LAYOUT layout)..."
    echo ""
    
    SESSION_NAME="specbot"
    
    # Kill existing session if it exists
    tmux kill-session -t "$SESSION_NAME" 2>/dev/null || true
    
    # Create new tmux session with backend pane
    tmux new-session -d -s "$SESSION_NAME" -n "servers" \
        "cd '$REPO_ROOT/backend' && echo '📡 Backend Server (port 8000)' && echo '================================' && PYTHONPATH='$REPO_ROOT/backend' .venv/bin/python main.py 2>&1 | tee server.log; echo ''; echo 'Server stopped.'; read -p 'Press Enter to exit...'"
    
    # Determine split direction
    if [ "$TMUX_LAYOUT" = "vertical" ]; then
        SPLIT_FLAG="-v"  # vertical = top/bottom stacking
    else
        SPLIT_FLAG="-h"  # horizontal = side-by-side
    fi
    
    # Split and start frontend in new pane
    tmux split-window $SPLIT_FLAG -t "$SESSION_NAME:servers" \
        "cd '$REPO_ROOT/frontend' && echo '🎨 Frontend Server (port 5173)' && echo '================================' && npm run dev; echo ''; echo 'Server stopped.'; read -p 'Press Enter to exit...'"
    
    # Set pane titles (requires tmux 2.3+)
    tmux select-pane -t "$SESSION_NAME:servers.0" -T "Backend"
    tmux select-pane -t "$SESSION_NAME:servers.1" -T "Frontend"
    
    # Enable pane border status to show titles
    tmux set-option -t "$SESSION_NAME" pane-border-status top 2>/dev/null || true
    
    echo "✅ tmux session '$SESSION_NAME' created with two panes"
    echo ""
    echo "📋 tmux commands:"
    echo "   Attach:      tmux attach -t $SESSION_NAME"
    echo "   Detach:      Ctrl+b, then d"
    echo "   Kill:        tmux kill-session -t $SESSION_NAME"
    echo "   Switch pane: Ctrl+b, then arrow keys"
    echo ""
    
    # Attach to the session
    exec tmux attach -t "$SESSION_NAME"
else
    # Default behavior: background process mode
    echo "📡 Starting backend server (port 8000)..."
    echo "   Logs: backend/server.log"
    echo ""
    
    # Start backend in background
    cd backend
    PYTHONPATH="${REPO_ROOT}/backend" .venv/bin/python main.py > server.log 2>&1 &
    BACKEND_PID=$!
    cd ..
    
    # Cleanup on exit
    trap "echo ''; echo '🛑 Shutting down servers...'; kill $BACKEND_PID 2>/dev/null || true; exit 0" EXIT INT TERM
    
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
fi
