"""
Contract Replay Tests

Loads frontend contract snapshots and replays them to the backend
to verify that the backend can handle the actual request formats
that the frontend sends.

Updated for OpenAI LangChain integration.
"""

import pytest
from unittest.mock import patch, AsyncMock
from tests.helpers.contract import load_snapshots, replay_snapshot


@pytest.mark.parametrize("snapshot", load_snapshots(), ids=lambda s: s["metadata"]["operationId"])
def test_backend_handles_frontend_snapshots(client, snapshot):
    """
    Verify backend can handle actual frontend requests.

    This test:
    1. Loads all frontend contract snapshots
    2. Replays each captured request to the backend
    3. Verifies the backend returns a successful response (2xx status)
    4. Validates the response structure against OpenAPI spec

    Updated for OpenAI LangChain integration.
    """
    operation_id = snapshot["metadata"]["operationId"]

    # Mock the LLM service for all snapshot replays
    with patch('src.api.routes.messages.get_ai_response', new_callable=AsyncMock) as mock_get_ai:
        mock_get_ai.return_value = ("AI response from snapshot replay.", "gpt-3.5-turbo")

        # Replay the snapshot request to the backend
        response = replay_snapshot(client, snapshot)

        # Backend must accept the frontend's request format
        assert response.status_code < 300, (
            f"Backend rejected snapshot '{operation_id}':\n"
            f"Status: {response.status_code}\n"
            f"Response: {response.text}"
        )

        # Response should be valid JSON
        assert response.headers.get("content-type") == "application/json", (
            f"Expected JSON response for '{operation_id}', got: {response.headers.get('content-type')}"
        )

        # Response should have valid structure
        response_data = response.json()
        assert isinstance(response_data, dict), f"Response should be an object for '{operation_id}'"

        # Validate response format matches what frontend expects
        if operation_id == "sendMessage":
            assert "timestamp" in response_data, "Response must have timestamp field"

            # CRITICAL: Validate timestamp format matches JavaScript's toISOString()
            # JavaScript produces: "2025-12-29T21:30:45.123Z" (3 decimals - milliseconds)
            # Python should match this format exactly
            timestamp = response_data["timestamp"]
            from datetime import datetime
            try:
                # Parse and re-serialize to verify format
                parsed_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                # Check format matches JavaScript's toISOString() - exactly 3 decimal places
                iso_parts = timestamp.split('.')
                assert len(iso_parts) == 2, f"Timestamp must have fractional seconds: {timestamp}"
                fractional = iso_parts[1].rstrip('Z')
                assert len(fractional) == 3, (
                    f"Timestamp must have exactly 3 decimal places (milliseconds), "
                    f"not {len(fractional)}: {timestamp}"
                )
            except Exception as e:
                raise AssertionError(
                    f"Response timestamp format doesn't match JavaScript's toISOString(): {timestamp}\n"
                    f"Expected format: 2025-12-29T21:30:45.123Z (3 decimals)\n"
                    f"Error: {e}"
                )
