#!/bin/bash
# Diagnostic script to check test environment configuration
# Run from project root: ./scripts/diagnose-test-env.sh

set +e  # Don't exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo "🔍 Test Environment Diagnostic"
echo "========================================"
echo ""

cd "$PROJECT_ROOT"

echo "1. Git Status:"
echo "   Current commit: $(git log -1 --oneline)"
echo "   Current branch: $(git branch --show-current)"
echo ""

echo "2. Checking conftest.py fixture:"
if grep -q "OPENAI_MODEL" backend/tests/conftest.py; then
    echo "   ✅ OPENAI_MODEL found in conftest.py"
    grep -n "setenv.*OPENAI_MODEL" backend/tests/conftest.py
else
    echo "   ❌ OPENAI_MODEL NOT found in conftest.py"
    echo "   This is the problem! You need to pull the latest changes."
fi
echo ""

echo "3. Current .env configuration:"
if [ -f "backend/.env" ]; then
    MODEL=$(grep "^OPENAI_MODEL=" backend/.env | cut -d'=' -f2)
    echo "   OPENAI_MODEL=$MODEL"
else
    echo "   ⚠️  No .env file found"
fi
echo ""

echo "4. Pytest cache (might need clearing):"
if [ -d "backend/.pytest_cache" ]; then
    echo "   Cache exists at: backend/.pytest_cache"
    echo "   To clear: rm -rf backend/.pytest_cache"
else
    echo "   No cache found"
fi
echo ""

echo "5. Running test with verbose logging:"
echo "   (This will show which model is actually being used)"
echo ""
cd backend
python -m pytest tests/unit/test_llm_service.py::test_stream_ai_response_yields_complete_event -v -s 2>&1 | grep -E "PASSED|FAILED|Using default model:|AssertionError"
TEST_EXIT_CODE=$?

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ Test PASSED - fixture is working correctly"
else
    echo "❌ Test FAILED - fixture is NOT overriding .env"
    echo ""
    echo "Suggested fixes:"
    echo "  1. Pull latest changes: git pull origin claude/streaming-ui-complete-F8FIU"
    echo "  2. Clear pytest cache: rm -rf backend/.pytest_cache"
    echo "  3. Verify you're on commit bcf8e45 or later"
fi
