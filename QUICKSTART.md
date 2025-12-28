# SpecBot Quick Start Guide

## Option 1: Automatic Startup (Recommended)

Run both servers with a single command:

```bash
./start-servers.sh
```

This will:
1. ✅ Check prerequisites (venv, node_modules)
2. 🔧 Create `.env` file if missing
3. 📡 Start backend on http://localhost:8000
4. 🎨 Start frontend on http://localhost:5173

**Stop servers:** Press `Ctrl+C`

---

## Option 2: Manual Startup

### Step 1: Start Backend Server

**Terminal 1:**
```bash
cd backend

# Activate virtual environment (if not using script)
source venv/bin/activate  # Linux/Mac
# OR: venv\Scripts\activate  # Windows

# Start server
python main.py
```

**Expected output:**
```
Starting server with uvicorn...
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
Starting SpecBot Backend API Server
Server configuration: host=0.0.0.0, port=8000
CORS allowed origins: http://localhost:5173
```

**Verify backend is running:**
Open http://localhost:8000/docs in your browser - you should see the API documentation.

### Step 2: Start Frontend Server

**Terminal 2:**
```bash
cd frontend

# Make sure .env file exists
if [ ! -f .env ]; then
  cp .env.example .env
fi

# Start dev server
npm run dev
```

**Expected output:**
```
  VITE v5.0.0  ready in 234 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### Step 3: Test the Application

1. Open http://localhost:5173 in your browser
2. Type "Hello world" in the input field
3. Click "Send"
4. You should see: "api says: Hello world"

---

## Troubleshooting

### ❌ Error: "Cannot connect to server"

**Cause:** Backend server is not running or frontend can't reach it.

**Fix:**
1. Check backend is running: `curl http://localhost:8000/health`
   - Should return: `{"status":"ok"}`
2. If not running, start backend in Terminal 1 (see above)
3. Check frontend `.env` file exists: `cat frontend/.env`
   - Should contain: `VITE_API_BASE_URL=http://localhost:8000`
4. Restart frontend dev server (Ctrl+C, then `npm run dev`)

### ❌ Error: "Address already in use" (Port 8000)

**Cause:** Another process is using port 8000.

**Fix:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use a different port
cd backend
API_PORT=8001 python main.py

# Then update frontend/.env
echo "VITE_API_BASE_URL=http://localhost:8001" > frontend/.env
```

### ❌ Backend Error: "No module named 'fastapi'"

**Cause:** Dependencies not installed or virtual environment not activated.

**Fix:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### ⚠️ Frontend shows old error after fixing backend

**Cause:** Browser cache or dev server needs restart.

**Fix:**
1. Stop frontend dev server (Ctrl+C)
2. Restart: `npm run dev`
3. Hard refresh browser: Ctrl+Shift+R (or Cmd+Shift+R on Mac)

---

## Verification Checklist

Run these commands to verify everything is working:

```bash
# 1. Check backend health
curl http://localhost:8000/health
# Expected: {"status":"ok"}

# 2. Test message endpoint
curl -X POST http://localhost:8000/api/v1/messages \
  -H "Content-Type: application/json" \
  -d '{"message":"test"}'
# Expected: {"status":"success","message":"api says: test","timestamp":"..."}

# 3. Check frontend env
cat frontend/.env
# Expected: VITE_API_BASE_URL=http://localhost:8000

# 4. Check ports in use
lsof -i :8000  # Backend should be running
lsof -i :5173  # Frontend should be running
```

---

## Environment Variables

### Backend (`backend/.env`)

Optional - defaults work for local development:
```bash
API_HOST=0.0.0.0
API_PORT=8000
FRONTEND_URL=http://localhost:5173
LOG_LEVEL=INFO
```

### Frontend (`frontend/.env`)

**Required** - must be created from `.env.example`:
```bash
VITE_API_BASE_URL=http://localhost:8000
```

**Important:** After changing `.env` files, restart the dev servers!

---

## Running Tests

### Backend Tests
```bash
cd backend
PYTHONPATH=/workspaces/python-specbot/backend venv/bin/pytest tests/ -v
# Expected: 21 passed
```

### Frontend Tests
```bash
cd frontend
npm test
# Expected: 8/11 test files passing (E2E need servers running)
```

---

## Development Workflow

1. **Start servers** (once): `./start-servers.sh`
2. **Edit code**: Both servers auto-reload on file changes
3. **Test changes**: Browser auto-refreshes (Vite HMR)
4. **Check logs**:
   - Backend: See terminal or `backend/server.log`
   - Frontend: See terminal
   - Browser: Open DevTools Console (F12)

---

## Need Help?

- **API Documentation**: http://localhost:8000/docs (when backend running)
- **Architecture**: See `architecture.md`
- **Backend Details**: See `backend/README.md`
- **Feature Specs**: See `specs/003-backend-api-loopback/`
