#!/bin/bash
# Start both backend and frontend servers for local development
# Usage: ./scripts/start-servers.sh [options]
#
# Options:
#   --no-tmux           Disable tmux even if available (use background process mode)
#   --horizontal        Use horizontal (side-by-side) pane layout instead of default vertical
#   --backend-size N    Set backend pane size to N% (default: 66, frontend gets remainder)
#   --help              Show this help message
#
# By default, uses tmux if available with vertical layout (frontend top, backend bottom).

set -e

# Parse arguments
NO_TMUX=false
TMUX_LAYOUT="vertical"
BACKEND_SIZE=66

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-tmux)
            NO_TMUX=true
            shift
            ;;
        --horizontal)
            TMUX_LAYOUT="horizontal"
            shift
            ;;
        --backend-size)
            BACKEND_SIZE="$2"
            if ! [[ "$BACKEND_SIZE" =~ ^[0-9]+$ ]] || [ "$BACKEND_SIZE" -lt 10 ] || [ "$BACKEND_SIZE" -gt 90 ]; then
                echo "Error: --backend-size must be a number between 10 and 90"
                exit 1
            fi
            shift 2
            ;;
        --help)
            echo "Usage: ./scripts/start-servers.sh [options]"
            echo ""
            echo "Options:"
            echo "  --no-tmux          Disable tmux even if available (use background process mode)"
            echo "  --horizontal       Use horizontal (side-by-side) pane layout"
            echo "  --backend-size N   Set backend pane size to N% (default: 66, range: 10-90)"
            echo "  --help             Show this help message"
            echo ""
            echo "By default, uses tmux with vertical layout (frontend top, backend bottom ~66%)."
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Determine if we should use tmux (available and not disabled)
USE_TMUX=false
if [ "$NO_TMUX" = false ] && command -v tmux &> /dev/null; then
    USE_TMUX=true
fi

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
    echo "📺 Starting servers in tmux session ($TMUX_LAYOUT layout)..."
    echo ""
    
    SESSION_NAME="specbot"
    
    # Kill existing session if it exists
    tmux kill-session -t "$SESSION_NAME" 2>/dev/null || true
    
    # Commands for each server
    BACKEND_CMD="cd '$REPO_ROOT/backend' && echo '📡 Backend Server (port 8000)' && echo '================================' && PYTHONPATH='$REPO_ROOT/backend' .venv/bin/python main.py 2>&1 | tee server.log; echo ''; echo 'Server stopped.'; read -p 'Press Enter to exit...'"
    FRONTEND_CMD="cd '$REPO_ROOT/frontend' && echo '🎨 Frontend Server (port 5173)' && echo '================================' && npm run dev; echo ''; echo 'Server stopped.'; read -p 'Press Enter to exit...'"

    if [ "$TMUX_LAYOUT" = "vertical" ]; then
        # Vertical layout: frontend top (~33%), backend bottom (~66%)
        tmux new-session -d -s "$SESSION_NAME" -n "servers" "$FRONTEND_CMD"
        tmux split-window -v -t "$SESSION_NAME:servers" "$BACKEND_CMD"

        # Set pane titles (pane 0 = frontend/top, pane 1 = backend/bottom)
        tmux select-pane -t "$SESSION_NAME:servers.0" -T "Frontend"
        tmux select-pane -t "$SESSION_NAME:servers.1" -T "Backend"

        # Resize when window is resized (fires on attach when terminal size is applied)
        FRONTEND_SIZE=$((100 - BACKEND_SIZE))
        tmux set-hook -t "$SESSION_NAME" window-resized "resize-pane -t 0 -y ${FRONTEND_SIZE}%"

    else
        # Horizontal layout: backend left, frontend right (side-by-side)
        tmux new-session -d -s "$SESSION_NAME" -n "servers" "$BACKEND_CMD"
        tmux split-window -h -t "$SESSION_NAME:servers" "$FRONTEND_CMD"

        # Set pane titles (pane 0 = backend/left, pane 1 = frontend/right)
        tmux select-pane -t "$SESSION_NAME:servers.0" -T "Backend"
        tmux select-pane -t "$SESSION_NAME:servers.1" -T "Frontend"
    fi
    
    # Enable pane border status to show titles
    tmux set-option -t "$SESSION_NAME" pane-border-status top 2>/dev/null || true

    # Enable mouse support (scrolling, pane selection, resizing)
    tmux set-option -t "$SESSION_NAME" mouse on
    
    echo "✅ tmux session '$SESSION_NAME' created with two panes"
    echo ""
    echo "📋 tmux commands:"
    echo "   Attach:      tmux attach -t $SESSION_NAME"
    echo "   Detach:      Ctrl+b, then d"
    echo "   Kill:        tmux kill-session -t $SESSION_NAME"
    echo "   Switch pane: Ctrl+b, then arrow keys (or click with mouse)"
    echo "   Scroll:      Mouse wheel or Ctrl+b, then [ to enter copy mode"
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
