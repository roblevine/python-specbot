#!/bin/bash
#
# Contract Testing Workflow Script
#
# This script runs the complete contract testing workflow in the correct order:
# 1. Verifies prerequisites (dependencies, directories)
# 2. Runs frontend contract tests (generates snapshots)
# 3. Runs backend contract tests (replays snapshots)
# 4. Reports results
#
# Usage:
#   ./scripts/run-contract-tests.sh
#
# Options:
#   --skip-prereqs    Skip prerequisite checks
#   --frontend-only   Only run frontend snapshot capture
#   --backend-only    Only run backend snapshot replay
#   --verbose         Show detailed output
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
SKIP_PREREQS=false
FRONTEND_ONLY=false
BACKEND_ONLY=false
VERBOSE=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --skip-prereqs)
      SKIP_PREREQS=true
      shift
      ;;
    --frontend-only)
      FRONTEND_ONLY=true
      shift
      ;;
    --backend-only)
      BACKEND_ONLY=true
      shift
      ;;
    --verbose)
      VERBOSE=true
      shift
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      exit 1
      ;;
  esac
done

# Get repository root
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Contract Testing Workflow${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

#
# Step 1: Prerequisites Check
#
if [ "$SKIP_PREREQS" = false ]; then
  echo -e "${YELLOW}[1/4] Checking prerequisites...${NC}"

  # Check if frontend dependencies are installed
  if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}  → Installing frontend dependencies...${NC}"
    cd frontend
    npm install
    cd ..
  else
    echo -e "${GREEN}  ✓ Frontend dependencies installed${NC}"
  fi

  # Check if backend virtual environment exists
  if [ ! -d "backend/venv" ]; then
    echo -e "${RED}  ✗ Backend virtual environment not found${NC}"
    echo -e "${YELLOW}  → Creating virtual environment...${NC}"
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    deactivate
    cd ..
  else
    echo -e "${GREEN}  ✓ Backend virtual environment exists${NC}"
  fi

  # Check if OpenAPI spec exists
  if [ ! -f "specs/003-backend-api-loopback/contracts/message-api.yaml" ]; then
    echo -e "${RED}  ✗ OpenAPI specification not found${NC}"
    echo -e "     Expected: specs/003-backend-api-loopback/contracts/message-api.yaml"
    exit 1
  else
    echo -e "${GREEN}  ✓ OpenAPI specification found${NC}"
  fi

  # Check if snapshot directory exists
  if [ ! -d "specs/contract-snapshots" ]; then
    echo -e "${YELLOW}  → Creating snapshot directory...${NC}"
    mkdir -p specs/contract-snapshots
  else
    echo -e "${GREEN}  ✓ Snapshot directory exists${NC}"
  fi

  echo ""
else
  echo -e "${YELLOW}[1/4] Skipping prerequisite checks${NC}"
  echo ""
fi

#
# Step 2: Run Frontend Contract Tests (Snapshot Capture)
#
if [ "$BACKEND_ONLY" = false ]; then
  echo -e "${YELLOW}[2/4] Running frontend contract tests (snapshot capture)...${NC}"

  cd frontend

  if [ "$VERBOSE" = true ]; then
    npm test tests/contract/ -- --run
  else
    npm test tests/contract/ -- --run > /tmp/frontend-contract-tests.log 2>&1
  fi

  FRONTEND_EXIT_CODE=$?

  if [ $FRONTEND_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}  ✓ Frontend contract tests passed${NC}"

    # Count snapshots generated
    SNAPSHOT_COUNT=$(ls -1 ../specs/contract-snapshots/*.json 2>/dev/null | wc -l)
    echo -e "${GREEN}  ✓ Generated $SNAPSHOT_COUNT snapshot(s)${NC}"

    if [ "$VERBOSE" = false ]; then
      echo -e "     (Run with --verbose to see detailed output)"
    fi
  else
    echo -e "${RED}  ✗ Frontend contract tests failed${NC}"
    if [ "$VERBOSE" = false ]; then
      echo -e "${RED}     See: /tmp/frontend-contract-tests.log${NC}"
    fi
    cd ..
    exit 1
  fi

  cd ..
  echo ""
else
  echo -e "${YELLOW}[2/4] Skipping frontend tests (--backend-only)${NC}"
  echo ""
fi

#
# Step 3: Verify Snapshots Exist
#
if [ "$BACKEND_ONLY" = false ]; then
  echo -e "${YELLOW}[3/4] Verifying snapshots were generated...${NC}"

  SNAPSHOT_FILES=$(find specs/contract-snapshots -name "*.json" -not -name ".gitkeep" 2>/dev/null | wc -l)

  if [ "$SNAPSHOT_FILES" -eq 0 ]; then
    echo -e "${RED}  ✗ No snapshots found${NC}"
    echo -e "     Expected snapshots in: specs/contract-snapshots/"
    exit 1
  else
    echo -e "${GREEN}  ✓ Found $SNAPSHOT_FILES snapshot(s):${NC}"
    for snapshot in specs/contract-snapshots/*.json; do
      if [ -f "$snapshot" ] && [ "$(basename "$snapshot")" != ".gitkeep" ]; then
        OPERATION_ID=$(jq -r '.metadata.operationId' "$snapshot" 2>/dev/null || echo "unknown")
        echo -e "     - $(basename "$snapshot") (${OPERATION_ID})"
      fi
    done
  fi

  echo ""
else
  echo -e "${YELLOW}[3/4] Skipping snapshot verification${NC}"
  echo ""
fi

#
# Step 4: Run Backend Contract Tests (Snapshot Replay)
#
if [ "$FRONTEND_ONLY" = false ]; then
  echo -e "${YELLOW}[4/4] Running backend contract tests (snapshot replay)...${NC}"

  cd backend

  # Activate virtual environment and run tests
  if [ "$VERBOSE" = true ]; then
    PYTHONPATH=/workspaces/python-specbot/backend venv/bin/pytest tests/contract/test_replay.py -v
  else
    PYTHONPATH=/workspaces/python-specbot/backend venv/bin/pytest tests/contract/test_replay.py -v > /tmp/backend-contract-tests.log 2>&1
  fi

  BACKEND_EXIT_CODE=$?

  if [ $BACKEND_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}  ✓ Backend contract tests passed${NC}"
    echo -e "${GREEN}  ✓ Backend successfully handles all frontend request formats${NC}"

    if [ "$VERBOSE" = false ]; then
      echo -e "     (Run with --verbose to see detailed output)"
    fi
  else
    echo -e "${RED}  ✗ Backend contract tests failed${NC}"
    echo -e "${RED}  ✗ Backend cannot handle frontend request format!${NC}"
    if [ "$VERBOSE" = false ]; then
      echo -e "${RED}     See: /tmp/backend-contract-tests.log${NC}"
    fi
    cd ..
    exit 1
  fi

  cd ..
  echo ""
else
  echo -e "${YELLOW}[4/4] Skipping backend tests (--frontend-only)${NC}"
  echo ""
fi

#
# Summary
#
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Contract testing workflow complete!${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

if [ "$FRONTEND_ONLY" = false ] && [ "$BACKEND_ONLY" = false ]; then
  echo -e "${GREEN}✓ Frontend captured actual request formats as snapshots${NC}"
  echo -e "${GREEN}✓ Backend successfully replayed and processed all snapshots${NC}"
  echo -e "${GREEN}✓ No contract mismatches detected${NC}"
  echo ""
  echo -e "Contract testing is ${GREEN}PASSING${NC} - frontend and backend are compatible!"
fi

echo ""
