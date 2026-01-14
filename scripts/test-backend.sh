#!/bin/bash
# Backend Test Runner
# Runs all backend tests including unit, integration, and contract tests
# Usage: ./scripts/test-backend.sh [options]
#   Options: Pass any pytest options (e.g., -v, --cov, -k test_name)

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$PROJECT_ROOT/backend"

echo "=================================="
echo "🧪 Backend Test Suite"
echo "=================================="
echo ""

# Check if backend directory exists
if [ ! -d "$BACKEND_DIR" ]; then
    echo "❌ Error: Backend directory not found at $BACKEND_DIR"
    exit 1
fi

cd "$BACKEND_DIR"

# Detect virtual environment location
VENV_DIR=""
if [ -d ".venv" ]; then
    VENV_DIR=".venv"
elif [ -d "venv" ]; then
    VENV_DIR="venv"
fi

# Create venv if it doesn't exist
if [ -z "$VENV_DIR" ]; then
    echo "⚠️  Warning: No virtual environment found. Creating one..."
    python3 -m venv .venv
    VENV_DIR=".venv"
    echo "📦 Installing backend dependencies..."
    "$VENV_DIR/bin/pip" install -r requirements.txt
    echo ""
fi

# Verify pytest is installed
if [ ! -f "$VENV_DIR/bin/pytest" ]; then
    echo "⚠️  Warning: pytest not found in virtual environment. Installing dependencies..."
    "$VENV_DIR/bin/pip" install -r requirements.txt
    echo ""
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "⚠️  Please update .env with your API keys before running tests that require external APIs"
    echo ""
fi

# Run tests using the venv's pytest directly
echo "🏃 Running backend tests..."
echo ""

if [ $# -eq 0 ]; then
    # Default: run all tests with verbose output
    "$VENV_DIR/bin/pytest" tests/ -v
else
    # Pass through any arguments (e.g., --cov, -k test_name)
    "$VENV_DIR/bin/pytest" "$@"
fi

TEST_EXIT_CODE=$?

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All backend tests passed!"
else
    echo "❌ Backend tests failed with exit code $TEST_EXIT_CODE"
fi

exit $TEST_EXIT_CODE
