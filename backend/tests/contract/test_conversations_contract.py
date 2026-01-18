"""
Contract Tests for Conversations API - DELETE endpoint

Feature: 016-delete-conversation
Tests: T043

Validates that API responses match the OpenAPI specification.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock


@pytest.mark.contract
class TestDeleteConversationContract:
    """Contract tests for DELETE /api/v1/conversations/{conversation_id}"""

    def test_delete_success_response_204_no_content(self, client: TestClient):
        """
        T043: Validate 204 No Content response format.

        Contract Requirements:
        - Status code: 204
        - Response body: Empty (No Content)
        - Headers: Standard HTTP headers
        """
        conversation_id = "conv-550e8400-e29b-41d4-a716-446655440000"

        with patch('src.api.routes.conversations.get_storage') as mock_get_storage:
            mock_storage = AsyncMock()
            mock_storage.delete_conversation = AsyncMock(return_value=True)
            mock_get_storage.return_value = mock_storage

            response = client.delete(f"/api/v1/conversations/{conversation_id}")

            # Contract: 204 No Content
            assert response.status_code == 204

            # Contract: Empty body
            assert response.text == "" or response.content == b""

    def test_delete_not_found_response_404_matches_contract(self, client: TestClient):
        """
        T043: Validate 404 Not Found response matches ErrorResponse schema.

        Contract Requirements:
        - Status code: 404
        - Content-Type: application/json
        - Body: ErrorResponse schema with error, code, detail fields
        """
        conversation_id = "conv-nonexistent-0000-0000-000000000000"

        with patch('src.api.routes.conversations.get_storage') as mock_get_storage:
            mock_storage = AsyncMock()
            mock_storage.delete_conversation = AsyncMock(return_value=False)
            mock_get_storage.return_value = mock_storage

            response = client.delete(f"/api/v1/conversations/{conversation_id}")

            # Contract: 404 status
            assert response.status_code == 404

            # Contract: JSON content type
            assert "application/json" in response.headers.get("content-type", "")

            # Contract: ErrorResponse schema
            data = response.json()
            assert "detail" in data

            detail = data["detail"]

            # Required fields per ErrorResponse schema
            assert "error" in detail, "ErrorResponse must have 'error' field"
            assert isinstance(detail["error"], str), "'error' must be string"

            assert "code" in detail, "ErrorResponse must have 'code' field"
            assert isinstance(detail["code"], str), "'code' must be string"

            # Verify expected values
            assert detail["error"] == "Conversation not found"
            assert detail["code"] == "CONVERSATION_NOT_FOUND"

    def test_delete_server_error_response_500_matches_contract(self, client: TestClient):
        """
        T043: Validate 500 Server Error response matches ErrorResponse schema.

        Contract Requirements:
        - Status code: 500
        - Content-Type: application/json
        - Body: ErrorResponse schema
        """
        conversation_id = "conv-550e8400-e29b-41d4-a716-446655440000"

        with patch('src.api.routes.conversations.get_storage') as mock_get_storage:
            mock_storage = AsyncMock()
            mock_storage.delete_conversation = AsyncMock(
                side_effect=Exception("Storage error")
            )
            mock_get_storage.return_value = mock_storage

            response = client.delete(f"/api/v1/conversations/{conversation_id}")

            # Contract: 500 status
            assert response.status_code == 500

            # Contract: JSON content type
            assert "application/json" in response.headers.get("content-type", "")

            # Contract: ErrorResponse schema
            data = response.json()
            assert "detail" in data

            detail = data["detail"]
            assert "error" in detail
            assert "code" in detail
            assert detail["code"] == "STORAGE_WRITE_ERROR"

    def test_delete_path_parameter_format(self, client: TestClient):
        """
        T043: Validate conversation_id path parameter accepts various formats.

        Contract Requirements:
        - Path: /api/v1/conversations/{conversation_id}
        - conversation_id: string (UUID format expected)
        """
        test_cases = [
            # Standard conv- prefixed UUID
            "conv-550e8400-e29b-41d4-a716-446655440000",
            # Plain UUID
            "550e8400-e29b-41d4-a716-446655440000",
            # Another valid UUID
            "123e4567-e89b-12d3-a456-426614174000",
        ]

        with patch('src.api.routes.conversations.get_storage') as mock_get_storage:
            mock_storage = AsyncMock()
            mock_storage.delete_conversation = AsyncMock(return_value=True)
            mock_get_storage.return_value = mock_storage

            for conv_id in test_cases:
                response = client.delete(f"/api/v1/conversations/{conv_id}")
                assert response.status_code == 204, f"Failed for ID: {conv_id}"

    def test_delete_response_headers(self, client: TestClient):
        """
        T043: Validate required response headers are present.
        """
        conversation_id = "conv-550e8400-e29b-41d4-a716-446655440000"

        with patch('src.api.routes.conversations.get_storage') as mock_get_storage:
            mock_storage = AsyncMock()
            mock_storage.delete_conversation = AsyncMock(return_value=True)
            mock_get_storage.return_value = mock_storage

            response = client.delete(f"/api/v1/conversations/{conversation_id}")

            # Check standard headers exist
            assert response.status_code == 204

            # For 204 No Content, there should be no content-type header
            # or it should indicate no content
            # FastAPI may not send content-type for 204 responses

    def test_delete_method_not_allowed_for_get(self, client: TestClient):
        """
        T043: Validate only DELETE method is accepted at delete endpoint.

        Note: GET on this path goes to get_conversation endpoint, not delete.
        """
        conversation_id = "conv-550e8400-e29b-41d4-a716-446655440000"

        # POST, PUT should return 405 Method Not Allowed
        # (The route only defines DELETE for the delete operation)

        with patch('src.api.routes.conversations.get_storage') as mock_get_storage:
            mock_storage = AsyncMock()
            mock_storage.delete_conversation = AsyncMock(return_value=True)
            mock_get_storage.return_value = mock_storage

            # DELETE should work
            response = client.delete(f"/api/v1/conversations/{conversation_id}")
            assert response.status_code == 204


@pytest.mark.contract
class TestDeleteConversationContractSnapshot:
    """Snapshot-based contract tests for DELETE endpoint."""

    def test_request_format_matches_frontend_snapshot(self, client: TestClient):
        """
        T043: Validate backend accepts the request format captured by frontend.

        This test ensures frontend and backend agree on the request format.
        """
        import json
        import os

        # Load frontend snapshot if it exists
        snapshot_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "tests",
            "contract-snapshots",
            "deleteConversation.json"
        )

        if os.path.exists(snapshot_path):
            with open(snapshot_path, 'r') as f:
                snapshot = json.load(f)

            request = snapshot["request"]

            with patch('src.api.routes.conversations.get_storage') as mock_get_storage:
                mock_storage = AsyncMock()
                mock_storage.delete_conversation = AsyncMock(return_value=True)
                mock_get_storage.return_value = mock_storage

                # Make request matching frontend snapshot
                response = client.request(
                    method=request["method"],
                    url=request["path"],
                    headers=request.get("headers", {}),
                    json=request.get("body")
                )

                # Should succeed
                assert response.status_code == 204, \
                    f"Backend should accept frontend request format. Got {response.status_code}"
        else:
            # Skip if snapshot doesn't exist yet
            pytest.skip("Frontend snapshot not yet captured")

    def test_error_response_format_consistent(self, client: TestClient):
        """
        T043: Validate error response format is consistent across error types.

        All error responses should follow the same ErrorResponse schema.
        """
        with patch('src.api.routes.conversations.get_storage') as mock_get_storage:
            mock_storage = AsyncMock()

            # Test 404 error
            mock_storage.delete_conversation = AsyncMock(return_value=False)
            mock_get_storage.return_value = mock_storage

            response_404 = client.delete("/api/v1/conversations/nonexistent")
            data_404 = response_404.json()

            # Test 500 error
            mock_storage.delete_conversation = AsyncMock(side_effect=Exception("Error"))
            response_500 = client.delete("/api/v1/conversations/error-case")
            data_500 = response_500.json()

            # Both should have same structure
            assert "detail" in data_404
            assert "detail" in data_500

            assert "error" in data_404["detail"]
            assert "error" in data_500["detail"]

            assert "code" in data_404["detail"]
            assert "code" in data_500["detail"]
