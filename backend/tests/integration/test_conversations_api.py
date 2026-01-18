"""
Integration Tests for Conversations API - DELETE endpoint

Feature: 016-delete-conversation
Tests: T042

Tests the DELETE /api/v1/conversations/{conversation_id} endpoint
for various scenarios including success, not found, and error handling.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock


@pytest.fixture
def sample_conversation():
    """Sample conversation data for testing."""
    return {
        "id": "conv-550e8400-e29b-41d4-a716-446655440000",
        "title": "Test Conversation",
        "createdAt": "2025-12-28T10:00:00.000Z",
        "updatedAt": "2025-12-28T10:00:00.000Z",
        "messages": []
    }


@pytest.fixture
def mock_storage():
    """Mock storage service for testing."""
    storage = AsyncMock()
    storage.delete_conversation = AsyncMock(return_value=True)
    storage.get_conversation = AsyncMock(return_value=None)
    storage.conversation_exists = AsyncMock(return_value=True)
    return storage


class TestDeleteConversation:
    """Integration tests for DELETE /api/v1/conversations/{conversation_id}"""

    @pytest.mark.integration
    def test_delete_conversation_success(self, client: TestClient):
        """
        T042: DELETE /api/v1/conversations/{id} returns 204 No Content on success.

        Acceptance Criteria:
        - Valid conversation ID results in deletion
        - Response status is 204 No Content
        - Response body is empty
        """
        conversation_id = "conv-550e8400-e29b-41d4-a716-446655440000"

        with patch('src.api.routes.conversations.get_storage') as mock_get_storage:
            mock_storage = AsyncMock()
            mock_storage.delete_conversation = AsyncMock(return_value=True)
            mock_get_storage.return_value = mock_storage

            response = client.delete(f"/api/v1/conversations/{conversation_id}")

            assert response.status_code == 204, f"Expected 204, got {response.status_code}"
            assert response.text == "" or response.content == b"", "Response body should be empty"

            # Verify delete was called with correct ID
            mock_storage.delete_conversation.assert_called_once_with(conversation_id)

    @pytest.mark.integration
    def test_delete_conversation_not_found(self, client: TestClient):
        """
        T042: DELETE /api/v1/conversations/{id} returns 404 when conversation doesn't exist.

        Acceptance Criteria:
        - Non-existent conversation ID returns 404
        - Response contains error details
        - Error code is CONVERSATION_NOT_FOUND
        """
        conversation_id = "conv-nonexistent-0000-0000-000000000000"

        with patch('src.api.routes.conversations.get_storage') as mock_get_storage:
            mock_storage = AsyncMock()
            mock_storage.delete_conversation = AsyncMock(return_value=False)
            mock_get_storage.return_value = mock_storage

            response = client.delete(f"/api/v1/conversations/{conversation_id}")

            assert response.status_code == 404, f"Expected 404, got {response.status_code}"

            data = response.json()
            assert "detail" in data, "Response should contain 'detail' field"

            detail = data["detail"]
            assert detail["error"] == "Conversation not found"
            assert detail["code"] == "CONVERSATION_NOT_FOUND"

    @pytest.mark.integration
    def test_delete_conversation_storage_error(self, client: TestClient):
        """
        T042: DELETE /api/v1/conversations/{id} returns 500 on storage error.

        Acceptance Criteria:
        - Storage errors result in 500 response
        - Error message indicates failure
        """
        conversation_id = "conv-550e8400-e29b-41d4-a716-446655440000"

        with patch('src.api.routes.conversations.get_storage') as mock_get_storage:
            mock_storage = AsyncMock()
            mock_storage.delete_conversation = AsyncMock(
                side_effect=Exception("Storage unavailable")
            )
            mock_get_storage.return_value = mock_storage

            response = client.delete(f"/api/v1/conversations/{conversation_id}")

            assert response.status_code == 500, f"Expected 500, got {response.status_code}"

            data = response.json()
            assert "detail" in data
            assert data["detail"]["code"] == "STORAGE_WRITE_ERROR"

    @pytest.mark.integration
    def test_delete_conversation_idempotency(self, client: TestClient):
        """
        T042: Multiple delete requests for same conversation handle gracefully.

        When deleting an already-deleted conversation, should return 404.
        """
        conversation_id = "conv-550e8400-e29b-41d4-a716-446655440000"

        with patch('src.api.routes.conversations.get_storage') as mock_get_storage:
            mock_storage = AsyncMock()
            # First call succeeds
            mock_storage.delete_conversation = AsyncMock(
                side_effect=[True, False]  # First returns True, second returns False
            )
            mock_get_storage.return_value = mock_storage

            # First delete should succeed
            response1 = client.delete(f"/api/v1/conversations/{conversation_id}")
            assert response1.status_code == 204

            # Second delete should return 404 (already deleted)
            response2 = client.delete(f"/api/v1/conversations/{conversation_id}")
            assert response2.status_code == 404

    @pytest.mark.integration
    def test_delete_conversation_with_messages(self, client: TestClient):
        """
        T042: Delete conversation that has messages.

        Verifies that conversations with messages can be deleted.
        """
        conversation_id = "conv-550e8400-e29b-41d4-a716-446655440000"

        with patch('src.api.routes.conversations.get_storage') as mock_get_storage:
            mock_storage = AsyncMock()
            mock_storage.delete_conversation = AsyncMock(return_value=True)
            mock_get_storage.return_value = mock_storage

            response = client.delete(f"/api/v1/conversations/{conversation_id}")

            assert response.status_code == 204
            mock_storage.delete_conversation.assert_called_once_with(conversation_id)


class TestDeleteConversationValidation:
    """Validation tests for DELETE endpoint."""

    @pytest.mark.integration
    def test_delete_conversation_with_valid_uuid(self, client: TestClient):
        """Valid UUID format should be accepted."""
        # Standard UUID format with conv- prefix
        conversation_id = "conv-123e4567-e89b-12d3-a456-426614174000"

        with patch('src.api.routes.conversations.get_storage') as mock_get_storage:
            mock_storage = AsyncMock()
            mock_storage.delete_conversation = AsyncMock(return_value=True)
            mock_get_storage.return_value = mock_storage

            response = client.delete(f"/api/v1/conversations/{conversation_id}")
            assert response.status_code == 204

    @pytest.mark.integration
    def test_delete_conversation_with_plain_uuid(self, client: TestClient):
        """Plain UUID (without conv- prefix) should also work if that's the ID format."""
        conversation_id = "123e4567-e89b-12d3-a456-426614174000"

        with patch('src.api.routes.conversations.get_storage') as mock_get_storage:
            mock_storage = AsyncMock()
            mock_storage.delete_conversation = AsyncMock(return_value=True)
            mock_get_storage.return_value = mock_storage

            response = client.delete(f"/api/v1/conversations/{conversation_id}")
            assert response.status_code == 204


class TestDeleteConversationLogging:
    """Tests for logging behavior during deletion."""

    @pytest.mark.integration
    def test_delete_conversation_logs_success(self, client: TestClient, caplog):
        """Successful deletion should be logged."""
        conversation_id = "conv-550e8400-e29b-41d4-a716-446655440000"

        with patch('src.api.routes.conversations.get_storage') as mock_get_storage:
            mock_storage = AsyncMock()
            mock_storage.delete_conversation = AsyncMock(return_value=True)
            mock_get_storage.return_value = mock_storage

            import logging
            with caplog.at_level(logging.INFO):
                response = client.delete(f"/api/v1/conversations/{conversation_id}")

            assert response.status_code == 204
            assert any("Deleting conversation" in record.message for record in caplog.records)

    @pytest.mark.integration
    def test_delete_conversation_logs_not_found(self, client: TestClient, caplog):
        """Not found should be logged as warning."""
        conversation_id = "conv-nonexistent-0000-0000-000000000000"

        with patch('src.api.routes.conversations.get_storage') as mock_get_storage:
            mock_storage = AsyncMock()
            mock_storage.delete_conversation = AsyncMock(return_value=False)
            mock_get_storage.return_value = mock_storage

            import logging
            with caplog.at_level(logging.WARNING):
                response = client.delete(f"/api/v1/conversations/{conversation_id}")

            assert response.status_code == 404
            assert any("not found" in record.message.lower() for record in caplog.records)
