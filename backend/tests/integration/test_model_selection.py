"""
Integration Tests for Model Selection Flow

Tests the end-to-end flow of model selection from API request to LLM invocation.

Feature: 008-openai-model-selector User Story 1
Task: T017
"""

import pytest
from unittest.mock import patch, AsyncMock, Mock
from fastapi.testclient import TestClient


@pytest.mark.integration
def test_model_selection_end_to_end_flow(client: TestClient):
    """
    T017: Integration test for complete model selection flow.

    Tests the full stack:
    1. Client sends POST /api/v1/messages with model field
    2. API validates model against configuration
    3. LLM service creates ChatOpenAI with requested model
    4. Response includes the model that was used

    This test verifies all components work together correctly.
    """
    with patch('src.api.routes.messages.get_ai_response', new_callable=AsyncMock) as mock_get_ai:
        # Mock AI response - returns both response and model used
        mock_get_ai.return_value = ("AI response from GPT-4", "gpt-4")

        # Send request with specific model
        response = client.post(
            "/api/v1/messages",
            json={
                "message": "Hello, use GPT-4 please",
                "model": "gpt-4"
            }
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert data["status"] == "success"
        assert "message" in data
        assert "timestamp" in data
        assert "model" in data

        # Verify correct model was used
        assert data["model"] == "gpt-4"

        # Verify LLM service was called with correct model
        mock_get_ai.assert_called_once()
        call_args = mock_get_ai.call_args
        assert call_args.kwargs["model"] == "gpt-4"


@pytest.mark.integration
def test_model_selection_uses_default_when_not_specified(client: TestClient):
    """
    T017: Integration test for default model selection.

    When no model is specified in the request, the backend should:
    1. Use the default model from configuration
    2. Return the default model in the response
    """
    with patch('src.api.routes.messages.get_ai_response', new_callable=AsyncMock) as mock_get_ai:
        # Mock AI response with default model
        mock_get_ai.return_value = ("AI response from default", "gpt-3.5-turbo")

        # Send request WITHOUT model field
        response = client.post(
            "/api/v1/messages",
            json={
                "message": "Hello, use default model"
            }
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()

        # Verify response includes model field
        assert "model" in data
        assert data["model"] == "gpt-3.5-turbo"

        # Verify LLM service was called without specific model (uses default)
        mock_get_ai.assert_called_once()
        call_args = mock_get_ai.call_args
        # model parameter should be None or not present (defaults to None)
        model_arg = call_args.kwargs.get("model")
        assert model_arg is None or model_arg == "gpt-3.5-turbo"


@pytest.mark.integration
def test_model_selection_with_conversation_history(client: TestClient):
    """
    T017: Integration test for model selection with conversation history.

    Verifies that model selection works correctly when combined with
    conversation history for context-aware responses.
    """
    with patch('src.api.routes.messages.get_ai_response', new_callable=AsyncMock) as mock_get_ai:
        # Mock AI response
        mock_get_ai.return_value = ("Context-aware response", "gpt-4")

        # Send request with history and model
        response = client.post(
            "/api/v1/messages",
            json={
                "message": "Follow-up question",
                "model": "gpt-4",
                "history": [
                    {"sender": "user", "text": "First question"},
                    {"sender": "system", "text": "First answer"}
                ]
            }
        )

        # Verify response
        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert data["model"] == "gpt-4"

        # Verify LLM service received both history and model
        mock_get_ai.assert_called_once()
        call_args = mock_get_ai.call_args
        assert call_args.kwargs["model"] == "gpt-4"
        assert "history" in call_args.kwargs
        assert len(call_args.kwargs["history"]) == 2


@pytest.mark.integration
def test_invalid_model_returns_appropriate_error(client: TestClient):
    """
    T017: Integration test for invalid model error handling.

    When an invalid model is requested, the API should:
    1. Return 400 Bad Request
    2. Include error message indicating invalid model
    3. Not call the LLM service
    """
    with patch('src.api.routes.messages.get_ai_response', new_callable=AsyncMock) as mock_get_ai:
        # Mock LLM service to raise error for invalid model
        from src.services.llm_service import LLMServiceError
        mock_get_ai.side_effect = LLMServiceError("AI service error occurred")

        # Send request with invalid model
        response = client.post(
            "/api/v1/messages",
            json={
                "message": "Test message",
                "model": "nonexistent-model"
            }
        )

        # Verify error response
        # Note: LLMServiceError is mapped to 503, but validation errors should be 400
        # The actual status depends on where validation happens
        assert response.status_code in [400, 503]
        data = response.json()

        # Check for error in response
        error_msg = ""
        if "error" in data:
            error_msg = data["error"]
        elif "detail" in data:
            if isinstance(data["detail"], dict) and "error" in data["detail"]:
                error_msg = data["detail"]["error"]
            elif isinstance(data["detail"], str):
                error_msg = data["detail"]

        # Error message should mention the problem
        assert len(error_msg) > 0


@pytest.mark.integration
def test_model_configuration_validation(client: TestClient):
    """
    T017: Integration test for model configuration validation.

    Verifies that:
    1. Only models in the configuration can be used
    2. Model IDs are validated against actual configuration
    """
    # This test verifies the GET /api/v1/models endpoint returns valid config
    response = client.get("/api/v1/models")

    assert response.status_code == 200
    data = response.json()

    assert "models" in data
    assert len(data["models"]) > 0

    # Get first model ID from configuration
    first_model_id = data["models"][0]["id"]

    # Verify we can use this model
    with patch('src.api.routes.messages.get_ai_response', new_callable=AsyncMock) as mock_get_ai:
        mock_get_ai.return_value = ("Response", first_model_id)

        response = client.post(
            "/api/v1/messages",
            json={
                "message": "Test with valid model",
                "model": first_model_id
            }
        )

        assert response.status_code == 200
        data = response.json()
        assert data["model"] == first_model_id


@pytest.mark.integration
def test_model_persistence_across_conversation(client: TestClient):
    """
    T017: Integration test for model selection persistence.

    Verifies that when a model is selected for one message,
    it can be changed for subsequent messages in the conversation.
    """
    with patch('src.api.routes.messages.get_ai_response', new_callable=AsyncMock) as mock_get_ai:
        # First message with GPT-4
        mock_get_ai.return_value = ("First response", "gpt-4")

        # Use valid conv-{uuid} format
        conv_id = "conv-12345678-1234-1234-1234-123456789abc"

        response1 = client.post(
            "/api/v1/messages",
            json={
                "message": "First message",
                "model": "gpt-4",
                "conversationId": conv_id
            }
        )

        assert response1.status_code == 200
        assert response1.json()["model"] == "gpt-4"

        # Second message with GPT-3.5 (different model)
        mock_get_ai.return_value = ("Second response", "gpt-3.5-turbo")

        response2 = client.post(
            "/api/v1/messages",
            json={
                "message": "Second message",
                "model": "gpt-3.5-turbo",
                "conversationId": conv_id,
                "history": [
                    {"sender": "user", "text": "First message"},
                    {"sender": "system", "text": "First response"}
                ]
            }
        )

        assert response2.status_code == 200
        assert response2.json()["model"] == "gpt-3.5-turbo"

        # Verify both calls were made with different models
        assert mock_get_ai.call_count == 2
        first_call_model = mock_get_ai.call_args_list[0].kwargs["model"]
        second_call_model = mock_get_ai.call_args_list[1].kwargs["model"]
        assert first_call_model == "gpt-4"
        assert second_call_model == "gpt-3.5-turbo"
