#!/bin/bash
# Combined Test Runner
# Runs all tests: backend (unit, integration, contract) and frontend (unit, integration, contract)
# Usage: ./scripts/test-all.sh [--backend-only | --frontend-only | --coverage]

set -e  # Exit on error (will stop if any test suite fails)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Parse arguments
RUN_BACKEND=true
RUN_FRONTEND=true
COVERAGE=false

for arg in "$@"; do
    case $arg in
        --backend-only)
            RUN_FRONTEND=false
            ;;
        --frontend-only)
            RUN_BACKEND=false
            ;;
        --coverage)
            COVERAGE=true
            ;;
        *)
            echo "Unknown option: $arg"
            echo "Usage: $0 [--backend-only | --frontend-only | --coverage]"
            exit 1
            ;;
    esac
done

echo "========================================"
echo "🧪 Python Specbot - Full Test Suite"
echo "========================================"
echo ""

BACKEND_EXIT_CODE=0
FRONTEND_EXIT_CODE=0

# Run backend tests
if [ "$RUN_BACKEND" = true ]; then
    echo "📦 Running Backend Tests..."
    echo "----------------------------------------"
    if [ "$COVERAGE" = true ]; then
        "$SCRIPT_DIR/test-backend.sh" --cov=src --cov-report=html --cov-report=term
    else
        "$SCRIPT_DIR/test-backend.sh"
    fi
    BACKEND_EXIT_CODE=$?

    if [ $BACKEND_EXIT_CODE -ne 0 ]; then
        echo ""
        echo "❌ Backend tests failed!"
        echo ""
    fi
    echo ""
fi

# Run frontend tests
if [ "$RUN_FRONTEND" = true ]; then
    echo "📦 Running Frontend Tests..."
    echo "----------------------------------------"
    if [ "$COVERAGE" = true ]; then
        "$SCRIPT_DIR/test-frontend.sh" --coverage
    else
        "$SCRIPT_DIR/test-frontend.sh"
    fi
    FRONTEND_EXIT_CODE=$?

    if [ $FRONTEND_EXIT_CODE -ne 0 ]; then
        echo ""
        echo "❌ Frontend tests failed!"
        echo ""
    fi
    echo ""
fi

# Summary
echo "========================================"
echo "📊 Test Summary"
echo "========================================"

if [ "$RUN_BACKEND" = true ]; then
    if [ $BACKEND_EXIT_CODE -eq 0 ]; then
        echo "✅ Backend:  PASSED"
    else
        echo "❌ Backend:  FAILED (exit code: $BACKEND_EXIT_CODE)"
    fi
fi

if [ "$RUN_FRONTEND" = true ]; then
    if [ $FRONTEND_EXIT_CODE -eq 0 ]; then
        echo "✅ Frontend: PASSED"
    else
        echo "❌ Frontend: FAILED (exit code: $FRONTEND_EXIT_CODE)"
    fi
fi

echo ""

# Exit with failure if any test suite failed
if [ $BACKEND_EXIT_CODE -ne 0 ] || [ $FRONTEND_EXIT_CODE -ne 0 ]; then
    echo "❌ Some test suites failed"
    exit 1
else
    echo "✅ All test suites passed!"
    if [ "$COVERAGE" = true ]; then
        echo ""
        echo "📊 Coverage reports generated:"
        [ "$RUN_BACKEND" = true ] && echo "   Backend:  backend/htmlcov/index.html"
        [ "$RUN_FRONTEND" = true ] && echo "   Frontend: frontend/coverage/index.html"
    fi
    exit 0
fi
