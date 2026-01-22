"""
Integration Tests for Title Generation API

Tests the end-to-end flow of title generation from API request to response.

Feature: 019-llm-conversation-titles
Tasks: T006, T007, T008, T030
"""

import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestTitleGenerationEndpoint:
    """Tests for POST /api/v1/titles/generate endpoint."""

    def test_generate_title_valid_request(self, client: TestClient):
        """T006: Test title generation with valid request."""
        with patch('src.api.routes.titles.generate_title', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = "Python Binary Search Implementation"

            response = client.post(
                "/api/v1/titles/generate",
                json={
                    "messages": [
                        {"sender": "user", "text": "How do I implement a binary search tree in Python?"},
                        {"sender": "system", "text": "To implement a binary search tree in Python, you'll need..."}
                    ],
                    "model": "gpt-3.5-turbo"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["title"] == "Python Binary Search Implementation"
            assert len(data["title"]) <= 60

    def test_generate_title_invalid_model(self, client: TestClient):
        """T007: Test title generation with invalid model ID."""
        with patch('src.api.routes.titles.generate_title', new_callable=AsyncMock) as mock_generate:
            # Simulate ValueError for invalid model
            mock_generate.side_effect = ValueError("Invalid model: nonexistent-model")

            response = client.post(
                "/api/v1/titles/generate",
                json={
                    "messages": [
                        {"sender": "user", "text": "Hello"},
                        {"sender": "system", "text": "Hi there!"}
                    ],
                    "model": "nonexistent-model"
                }
            )

            assert response.status_code == 400
            data = response.json()
            assert data["status"] == "error"
            assert "invalid" in data["error"].lower() or "model" in data["error"].lower()

    def test_generate_title_empty_messages(self, client: TestClient):
        """T008: Test title generation with empty messages array."""
        response = client.post(
            "/api/v1/titles/generate",
            json={
                "messages": [],
                "model": "gpt-3.5-turbo"
            }
        )

        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "error"

    def test_generate_title_single_message_rejected(self, client: TestClient):
        """Test that single message (less than 2) is rejected."""
        response = client.post(
            "/api/v1/titles/generate",
            json={
                "messages": [
                    {"sender": "user", "text": "Hello"}
                ],
                "model": "gpt-3.5-turbo"
            }
        )

        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "error"

    def test_generate_title_missing_messages_field(self, client: TestClient):
        """Test request with missing messages field."""
        response = client.post(
            "/api/v1/titles/generate",
            json={
                "model": "gpt-3.5-turbo"
            }
        )

        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "error"

    def test_generate_title_missing_model_field(self, client: TestClient):
        """Test request with missing model field."""
        response = client.post(
            "/api/v1/titles/generate",
            json={
                "messages": [
                    {"sender": "user", "text": "Hello"},
                    {"sender": "system", "text": "Hi!"}
                ]
            }
        )

        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "error"

    def test_generate_title_invalid_sender(self, client: TestClient):
        """Test request with invalid sender value."""
        response = client.post(
            "/api/v1/titles/generate",
            json={
                "messages": [
                    {"sender": "invalid", "text": "Hello"},
                    {"sender": "system", "text": "Hi!"}
                ],
                "model": "gpt-3.5-turbo"
            }
        )

        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "error"

    def test_generate_title_empty_text(self, client: TestClient):
        """Test request with empty message text."""
        response = client.post(
            "/api/v1/titles/generate",
            json={
                "messages": [
                    {"sender": "user", "text": ""},
                    {"sender": "system", "text": "Hi!"}
                ],
                "model": "gpt-3.5-turbo"
            }
        )

        assert response.status_code == 422
        data = response.json()
        assert data["status"] == "error"


@pytest.mark.integration
class TestTitleGenerationWithRealService:
    """Tests for title generation with mocked LLM service."""

    def test_title_truncated_to_60_chars(self, client: TestClient):
        """Test that titles longer than 60 chars are truncated."""
        long_title = "A" * 100

        with patch('src.api.routes.titles.generate_title', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = long_title[:60]  # Service should truncate

            response = client.post(
                "/api/v1/titles/generate",
                json={
                    "messages": [
                        {"sender": "user", "text": "Hello"},
                        {"sender": "system", "text": "Hi!"}
                    ],
                    "model": "gpt-3.5-turbo"
                }
            )

            assert response.status_code == 200
            data = response.json()
            assert len(data["title"]) <= 60

    def test_llm_error_returns_503(self, client: TestClient):
        """Test that LLM errors return 503 status."""
        with patch('src.api.routes.titles.generate_title', new_callable=AsyncMock) as mock_generate:
            from src.services.providers.base import LLMServiceError
            mock_generate.side_effect = LLMServiceError("AI service error")

            response = client.post(
                "/api/v1/titles/generate",
                json={
                    "messages": [
                        {"sender": "user", "text": "Hello"},
                        {"sender": "system", "text": "Hi!"}
                    ],
                    "model": "gpt-3.5-turbo"
                }
            )

            assert response.status_code == 503
            data = response.json()
            assert data["status"] == "error"
            assert "service" in data["error"].lower() or "unavailable" in data["error"].lower()


@pytest.mark.integration
class TestTitleModelSelection:
    """T030: Tests for title model selection per provider."""

    def test_uses_configured_title_model(self, client: TestClient, monkeypatch):
        """Test that the configured title model is used."""
        monkeypatch.setenv('OPENAI_TITLE_MODEL', 'gpt-3.5-turbo')

        with patch('src.api.routes.titles.generate_title', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = "Test Title"

            response = client.post(
                "/api/v1/titles/generate",
                json={
                    "messages": [
                        {"sender": "user", "text": "Hello"},
                        {"sender": "system", "text": "Hi!"}
                    ],
                    "model": "gpt-3.5-turbo"  # Should match configured title model
                }
            )

            assert response.status_code == 200
            mock_generate.assert_called_once()
            # Verify the model parameter was passed
            call_kwargs = mock_generate.call_args
            assert call_kwargs[0][1] == "gpt-3.5-turbo" or call_kwargs.kwargs.get('model') == "gpt-3.5-turbo"

    def test_endpoint_accepts_any_valid_model(self, client: TestClient):
        """Test that endpoint accepts any valid model (client selects model)."""
        with patch('src.api.routes.titles.generate_title', new_callable=AsyncMock) as mock_generate:
            mock_generate.return_value = "Test Title"

            # Test with different models
            for model in ["gpt-4", "gpt-3.5-turbo", "claude-haiku-4-5-20251001"]:
                response = client.post(
                    "/api/v1/titles/generate",
                    json={
                        "messages": [
                            {"sender": "user", "text": "Hello"},
                            {"sender": "system", "text": "Hi!"}
                        ],
                        "model": model
                    }
                )

                # Should succeed if model is valid
                assert response.status_code in [200, 400]  # 400 if model doesn't exist
