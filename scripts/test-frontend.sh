#!/bin/bash
# Frontend Test Runner
# Runs all frontend tests including unit, integration, and contract tests
# Usage: ./scripts/test-frontend.sh [options]
#   Options: Pass any vitest options (e.g., --watch, --coverage, --ui)

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo "=================================="
echo "🧪 Frontend Test Suite"
echo "=================================="
echo ""

# Check if frontend directory exists
if [ ! -d "$FRONTEND_DIR" ]; then
    echo "❌ Error: Frontend directory not found at $FRONTEND_DIR"
    exit 1
fi

cd "$FRONTEND_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
    echo ""
fi

# Run tests
echo "🏃 Running frontend tests..."
echo ""

if [ $# -eq 0 ]; then
    # Default: run all tests
    npm test
else
    # Pass through any arguments (e.g., --coverage, --watch)
    npm test -- "$@"
fi

TEST_EXIT_CODE=$?

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All frontend tests passed!"
else
    echo "❌ Frontend tests failed with exit code $TEST_EXIT_CODE"
fi

exit $TEST_EXIT_CODE
