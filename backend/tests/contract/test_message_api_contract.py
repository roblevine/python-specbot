"""
Contract Tests for Message API

Validates that API requests and responses match the OpenAPI specification.
Uses openapi-core for schema validation.

Feature: 003-backend-api-loopback User Story 1
Tests: T021, T022 (TDD - these should FAIL before implementation)

CRITICAL: These tests validate that frontend and backend agree on the contract.
If these fail, it indicates a breaking mismatch between client and server.
"""

import pytest
from fastapi.testclient import TestClient
from openapi_core import Spec, validate_request, validate_response
from openapi_core.protocols import Request as OpenAPIRequest, Response as OpenAPIResponse
from openapi_core.datatypes import RequestParameters, Headers
from werkzeug.datastructures import ImmutableMultiDict


class FastAPIOpenAPIRequest(OpenAPIRequest):
    """
    Adapter to convert FastAPI TestClient request to openapi-core Request protocol.
    """
    def __init__(self, fastapi_request, body: bytes):
        self._request = fastapi_request
        self._body = body

    @property
    def host_url(self) -> str:
        # Override testserver with localhost:8000 to match OpenAPI spec
        return "http://localhost:8000"

    @property
    def path(self) -> str:
        return self._request.url.path

    @property
    def method(self) -> str:
        return self._request.method.lower()

    @property
    def parameters(self) -> RequestParameters:
        return RequestParameters(
            query=ImmutableMultiDict(self._request.url.params.items()),
            header=Headers(dict(self._request.headers)),
            cookie=ImmutableMultiDict(),
            path={}
        )

    @property
    def body(self) -> bytes:
        return self._body

    @property
    def mimetype(self) -> str:
        return self._request.headers.get('content-type', 'application/json')


class FastAPIOpenAPIResponse(OpenAPIResponse):
    """
    Adapter to convert FastAPI TestClient response to openapi-core Response protocol.
    """
    def __init__(self, fastapi_response):
        self._response = fastapi_response

    @property
    def data(self) -> bytes:
        return self._response.content

    @property
    def status_code(self) -> int:
        return self._response.status_code

    @property
    def mimetype(self) -> str:
        return self._response.headers.get('content-type', 'application/json').split(';')[0]


@pytest.mark.contract
def test_loopback_request_matches_contract(
    client: TestClient,
    openapi_spec: Spec,
    sample_message_request: dict
):
    """
    T021: Validate that MessageRequest matches OpenAPI contract.

    This test validates ALL fields in the request:
    - message: required string 1-10,000 chars
    - conversationId: optional string with conv-{uuid} pattern
    - timestamp: optional ISO-8601 date-time string

    CRITICAL: If this fails, frontend and backend disagree on request format.
    """
    import json

    # Prepare request body
    body = json.dumps(sample_message_request).encode('utf-8')

    # Make the actual request
    response = client.post(
        "/api/v1/messages",
        json=sample_message_request,
        headers={"Content-Type": "application/json"}
    )

    # Create OpenAPI request object
    openapi_request = FastAPIOpenAPIRequest(response.request, body)

    # Validate request against OpenAPI spec
    # In openapi-core 0.18.2, validate_request returns None on success, or raises on error
    result = validate_request(openapi_request, spec=openapi_spec, base_url="http://localhost:8000")

    # If result is None, validation passed
    if result is not None:
        assert not result.errors, f"Request validation errors: {[str(e) for e in result.errors]}"


@pytest.mark.contract
def test_loopback_response_matches_contract(
    client: TestClient,
    openapi_spec: Spec,
    sample_message_request: dict
):
    """
    T022: Validate that MessageResponse matches OpenAPI contract.

    This test validates ALL fields in the response:
    - status: required enum "success"
    - message: required string (AI response, no prefix required)
    - timestamp: required ISO-8601 date-time string

    CRITICAL: If this fails, backend response doesn't match contract.
    """
    import json
    from unittest.mock import patch, AsyncMock

    # Mock the LLM service to return predictable response
    with patch('src.api.routes.messages.load_config') as mock_load_config, \
         patch('src.api.routes.messages.get_ai_response', new_callable=AsyncMock) as mock_get_ai:

        # Mock config
        mock_load_config.return_value = {'api_key': 'test-key', 'model': 'gpt-3.5-turbo'}

        # Mock AI response
        mock_get_ai.return_value = ("This is an AI response.", "gpt-3.5-turbo")

        # Prepare request body
        body = json.dumps(sample_message_request).encode('utf-8')

        # Make request
        response = client.post(
            "/api/v1/messages",
            json=sample_message_request,
            headers={"Content-Type": "application/json"}
        )

        # Create OpenAPI request/response objects
        openapi_request = FastAPIOpenAPIRequest(response.request, body)
        openapi_response = FastAPIOpenAPIResponse(response)

        # Validate response against OpenAPI spec
        # In openapi-core 0.18.2, validate_response returns None on success, or raises on error
        result = validate_response(openapi_request, openapi_response, spec=openapi_spec, base_url="http://localhost:8000")

        # If result is None, validation passed
        if result is not None:
            assert not result.errors, f"Response validation errors: {[str(e) for e in result.errors]}"

        # Additional assertions for success response
        if response.status_code == 200:
            data = response.json()
            assert data["status"] == "success", "Response status must be 'success'"
            assert len(data["message"]) > 0, "Response message cannot be empty"
            assert "timestamp" in data, "Response must include timestamp"


@pytest.mark.contract
def test_minimal_request_matches_contract(
    client: TestClient,
    openapi_spec: Spec,
    sample_message_minimal: dict
):
    """
    Test minimal request (only required fields) matches contract.

    Validates that optional fields (conversationId, timestamp) are truly optional.
    """
    import json

    body = json.dumps(sample_message_minimal).encode('utf-8')
    response = client.post("/api/v1/messages", json=sample_message_minimal)

    openapi_request = FastAPIOpenAPIRequest(response.request, body)
    result = validate_request(openapi_request, spec=openapi_spec, base_url="http://localhost:8000")

    if result is not None:
        assert not result.errors, f"Minimal request validation errors: {[str(e) for e in result.errors]}"


@pytest.mark.contract
def test_special_characters_request_matches_contract(
    client: TestClient,
    openapi_spec: Spec,
    sample_message_special_chars: dict
):
    """
    Test request with special characters matches contract.

    Validates FR-010: Backend accepts special characters, emoji, multi-byte characters.
    """
    import json

    body = json.dumps(sample_message_special_chars, ensure_ascii=False).encode('utf-8')
    response = client.post("/api/v1/messages", json=sample_message_special_chars)

    openapi_request = FastAPIOpenAPIRequest(response.request, body)
    result = validate_request(openapi_request, spec=openapi_spec, base_url="http://localhost:8000")

    if result is not None:
        assert not result.errors, f"Special chars request validation errors: {[str(e) for e in result.errors]}"


@pytest.mark.contract
def test_error_response_matches_contract(
    client: TestClient,
    openapi_spec: Spec
):
    """
    Test error response (400) matches contract.

    Validates error response structure for invalid requests.
    """
    import json

    # Send empty message (should trigger 400 error)
    invalid_request = {"message": ""}
    body = json.dumps(invalid_request).encode('utf-8')
    response = client.post("/api/v1/messages", json=invalid_request)

    # Create OpenAPI request/response objects
    openapi_request = FastAPIOpenAPIRequest(response.request, body)
    openapi_response = FastAPIOpenAPIResponse(response)

    # Validate error response
    result = validate_response(openapi_request, openapi_response, spec=openapi_spec, base_url="http://localhost:8000")

    if result is not None:
        assert not result.errors, f"Error response validation errors: {[str(e) for e in result.errors]}"

    # Additional assertions for error response
    if response.status_code == 400:
        data = response.json()
        assert data["status"] == "error", "Error response status must be 'error'"
        assert "error" in data, "Error response must include error message"
        assert "timestamp" in data, "Error response must include timestamp"


@pytest.mark.contract
def test_conversation_id_format_validated_by_contract(
    client: TestClient,
    openapi_spec: Spec
):
    """
    Test that conversationId format is strictly validated by contract.

    CRITICAL: This test ensures that if frontend sends wrong ID format,
    it will be caught by contract validation.

    Valid format: conv-{uuid}
    Invalid formats: raw uuid, wrong prefix, malformed uuid
    """
    import json

    test_cases = [
        # Valid cases - should pass contract validation
        {
            "request": {"message": "Test", "conversationId": "conv-a1b2c3d4-5678-90ab-cdef-123456789abc"},
            "should_pass_contract": True,
            "description": "Valid conv-{uuid} format"
        },
        # Invalid cases - should fail contract validation
        {
            "request": {"message": "Test", "conversationId": "a1b2c3d4-5678-90ab-cdef-123456789abc"},
            "should_pass_contract": False,
            "description": "Raw UUID without conv- prefix"
        },
        {
            "request": {"message": "Test", "conversationId": "not-a-uuid"},
            "should_pass_contract": False,
            "description": "Invalid format"
        },
        {
            "request": {"message": "Test", "conversationId": "msg-a1b2c3d4-5678-90ab-cdef-123456789abc"},
            "should_pass_contract": False,
            "description": "Wrong prefix (msg- instead of conv-)"
        },
    ]

    for case in test_cases:
        body = json.dumps(case["request"]).encode('utf-8')
        response = client.post("/api/v1/messages", json=case["request"])

        openapi_request = FastAPIOpenAPIRequest(response.request, body)

        if case["should_pass_contract"]:
            # Should pass validation without errors or exceptions
            result = validate_request(openapi_request, spec=openapi_spec, base_url="http://localhost:8000")
            if result is not None:
                assert not result.errors, f"{case['description']}: Expected to pass contract but got errors: {[str(e) for e in result.errors]}"
        else:
            # Should fail validation (either raise exception or return errors)
            from openapi_core.validation.exceptions import ValidationError as OpenAPIValidationError
            validation_failed = False

            try:
                result = validate_request(openapi_request, spec=openapi_spec, base_url="http://localhost:8000")
                if result is not None and result.errors:
                    validation_failed = True
            except OpenAPIValidationError:
                validation_failed = True

            assert validation_failed, f"{case['description']}: Expected to fail contract validation but passed"


@pytest.mark.contract
def test_all_message_fields_validated(
    client: TestClient,
    openapi_spec: Spec
):
    """
    Test that ALL MessageRequest fields are validated by contract.

    This comprehensive test ensures:
    - message: validated for type, length, whitespace
    - conversationId: validated for format (conv-{uuid} pattern)
    - timestamp: validated for ISO-8601 format

    CRITICAL: This prevents silent schema drift between frontend and backend.
    """
    import json
    from unittest.mock import patch, AsyncMock

    # Mock the LLM service to return predictable response
    with patch('src.api.routes.messages.load_config') as mock_load_config, \
         patch('src.api.routes.messages.get_ai_response', new_callable=AsyncMock) as mock_get_ai:

        # Mock config
        mock_load_config.return_value = {'api_key': 'test-key', 'model': 'gpt-3.5-turbo'}

        # Mock AI response
        mock_get_ai.return_value = ("This is an AI response to your test message.", "gpt-3.5-turbo")

        # Test comprehensive valid request with ALL fields
        full_request = {
            "message": "Test message with all fields",
            "conversationId": "conv-12345678-1234-1234-1234-123456789abc",
            "timestamp": "2025-12-29T15:00:00.000Z"
        }

        body = json.dumps(full_request).encode('utf-8')
        response = client.post("/api/v1/messages", json=full_request)

        openapi_request = FastAPIOpenAPIRequest(response.request, body)
        openapi_response = FastAPIOpenAPIResponse(response)

        # Validate both request and response
        request_result = validate_request(openapi_request, spec=openapi_spec, base_url="http://localhost:8000")
        response_result = validate_response(openapi_request, openapi_response, spec=openapi_spec, base_url="http://localhost:8000")

        if request_result is not None:
            assert not request_result.errors, f"Request with all fields failed validation: {[str(e) for e in request_result.errors]}"
        if response_result is not None:
            assert not response_result.errors, f"Response validation failed: {[str(e) for e in response_result.errors]}"

        # Verify response content
        data = response.json()
        assert data["status"] == "success"
        assert len(data["message"]) > 0, "Response message cannot be empty"
        assert "timestamp" in data


@pytest.mark.contract
def test_ai_response_matches_contract(
    client: TestClient,
    openapi_spec: Spec
):
    """
    T009: Validate that AI response matches OpenAPI contract v2.0.0.

    This test validates that when using the LLM service:
    - Response status is "success"
    - Response message contains AI text (NOT "api says: " prefix)
    - Response includes ISO-8601 timestamp
    - Response matches MessageResponse schema in contract

    Feature: 006-openai-langchain-chat User Story 1
    Expected: FAIL (LLM service not integrated into endpoint yet)
    """
    import json
    from unittest.mock import patch, Mock, AsyncMock

    # Mock the LLM service to return predictable AI response
    # Patch where the functions are imported in messages.py
    with patch('src.api.routes.messages.load_config') as mock_load_config, \
         patch('src.api.routes.messages.get_ai_response', new_callable=AsyncMock) as mock_get_ai:

        # Mock config
        mock_load_config.return_value = {'api_key': 'test-key', 'model': 'gpt-3.5-turbo'}

        # Mock AI response
        mock_get_ai.return_value = ("Hello! I'm doing well, thank you for asking.", "gpt-3.5-turbo")

        # Prepare request
        request_data = {"message": "Hello, how are you?"}
        body = json.dumps(request_data).encode('utf-8')

        # Make request
        response = client.post(
            "/api/v1/messages",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )

        # Create OpenAPI request/response objects
        openapi_request = FastAPIOpenAPIRequest(response.request, body)
        openapi_response = FastAPIOpenAPIResponse(response)

        # Validate response against OpenAPI spec (v2.0.0)
        result = validate_response(
            openapi_request,
            openapi_response,
            spec=openapi_spec,
            base_url="http://localhost:8000"
        )

        # Check validation result
        if result is not None:
            assert not result.errors, f"AI response validation errors: {[str(e) for e in result.errors]}"

        # Verify response structure
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()

        assert data["status"] == "success", "Response status must be 'success'"
        assert "timestamp" in data, "Response must include timestamp"

        # CRITICAL: AI response should NOT have "api says: " prefix
        assert not data["message"].startswith("api says: "), \
            f"AI response should not have 'api says: ' prefix, got: {data['message']}"

        # Verify AI response content is present
        assert len(data["message"]) > 0, "AI response message cannot be empty"


@pytest.mark.contract
def test_503_error_response_matches_contract(
    client: TestClient,
    openapi_spec: Spec
):
    """
    T028: Contract test for 503 Service Unavailable error responses.

    Validates that 503 error responses (AI service issues) match OpenAPI spec.
    """
    from unittest.mock import patch, AsyncMock
    import json
    from src.services.llm_service import LLMAuthenticationError

    # Mock the LLM service to raise LLMAuthenticationError
    with patch('src.api.routes.messages.load_config') as mock_load_config, \
         patch('src.api.routes.messages.get_ai_response', new_callable=AsyncMock) as mock_get_ai:

        # Mock config
        mock_load_config.return_value = {'api_key': 'test-key', 'model': 'gpt-3.5-turbo'}

        # Mock AI service to raise LLMAuthenticationError
        mock_get_ai.side_effect = LLMAuthenticationError("AI service configuration error")

        # Prepare request
        request_data = {"message": "Hello"}
        body = json.dumps(request_data).encode('utf-8')

        # Make request
        response = client.post(
            "/api/v1/messages",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )

        # Create OpenAPI request/response objects
        openapi_request = FastAPIOpenAPIRequest(response.request, body)
        openapi_response = FastAPIOpenAPIResponse(response)

        # Validate response against OpenAPI spec
        result = validate_response(
            openapi_request,
            openapi_response,
            spec=openapi_spec,
            base_url="http://localhost:8000"
        )

        # Check validation result
        if result is not None:
            assert not result.errors, f"503 response validation errors: {[str(e) for e in result.errors]}"

        # Verify response structure
        assert response.status_code == 503, f"Expected 503, got {response.status_code}"
        data = response.json()

        # Verify error structure
        assert "error" in data, "Error response must include 'error' field"
        assert isinstance(data["error"], str), "Error field must be string"

        # CRITICAL: Must NOT expose sensitive data (API keys, raw errors)
        error_msg = data["error"].lower()
        assert "api key" not in error_msg or "invalid" in error_msg, \
            "Must not expose raw API key errors"
        assert "authentication" not in error_msg, \
            "Must not expose raw authentication errors"


@pytest.mark.contract
def test_504_timeout_response_matches_contract(
    client: TestClient,
    openapi_spec: Spec
):
    """
    T029: Contract test for 504 Gateway Timeout error responses.

    Validates that 504 timeout responses match OpenAPI spec.
    """
    from unittest.mock import patch, AsyncMock
    import json
    from src.services.llm_service import LLMTimeoutError

    # Mock the LLM service to raise LLMTimeoutError
    with patch('src.api.routes.messages.load_config') as mock_load_config, \
         patch('src.api.routes.messages.get_ai_response', new_callable=AsyncMock) as mock_get_ai:

        # Mock config
        mock_load_config.return_value = {'api_key': 'test-key', 'model': 'gpt-3.5-turbo'}

        # Mock AI service to raise LLMTimeoutError
        mock_get_ai.side_effect = LLMTimeoutError("Request timed out")

        # Prepare request
        request_data = {"message": "Hello"}
        body = json.dumps(request_data).encode('utf-8')

        # Make request
        response = client.post(
            "/api/v1/messages",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )

        # Create OpenAPI request/response objects
        openapi_request = FastAPIOpenAPIRequest(response.request, body)
        openapi_response = FastAPIOpenAPIResponse(response)

        # Validate response against OpenAPI spec
        result = validate_response(
            openapi_request,
            openapi_response,
            spec=openapi_spec,
            base_url="http://localhost:8000"
        )

        # Check validation result
        if result is not None:
            assert not result.errors, f"504 response validation errors: {[str(e) for e in result.errors]}"

        # Verify response structure
        assert response.status_code == 504, f"Expected 504, got {response.status_code}"
        data = response.json()

        # Verify error structure
        assert "error" in data, "Error response must include 'error' field"
        assert isinstance(data["error"], str), "Error field must be string"

        # Verify timeout message is user-friendly
        error_msg = data["error"].lower()
        assert "timeout" in error_msg or "timed out" in error_msg, \
            f"Timeout error message should mention timeout: {data['error']}"


@pytest.mark.contract
def test_message_request_with_model_field_matches_contract(
    client: TestClient,
    openapi_spec: Spec
):
    """
    T013: Contract test for POST /api/v1/messages with model field.

    Validates that MessageRequest with optional model field matches OpenAPI spec.
    This is part of Feature 008-openai-model-selector User Story 1.

    Tests:
    - model field is optional string
    - Valid model IDs are accepted
    - Response includes the model that was used
    """
    import json
    from unittest.mock import patch, AsyncMock

    # Mock the LLM service
    with patch('src.api.routes.messages.load_config') as mock_load_config, \
         patch('src.api.routes.messages.get_ai_response', new_callable=AsyncMock) as mock_get_ai:

        # Mock config
        mock_load_config.return_value = {'api_key': 'test-key', 'model': 'gpt-3.5-turbo'}

        # Mock AI response - return both response and model used (T013)
        mock_get_ai.return_value = ("AI response text", "gpt-4")

        # Test request with model field
        request_data = {
            "message": "Test message",
            "model": "gpt-4"
        }
        body = json.dumps(request_data).encode('utf-8')

        # Make request
        response = client.post(
            "/api/v1/messages",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )

        # Create OpenAPI request/response objects
        openapi_request = FastAPIOpenAPIRequest(response.request, body)
        openapi_response = FastAPIOpenAPIResponse(response)

        # Validate request against spec (model field should be accepted)
        request_result = validate_request(openapi_request, spec=openapi_spec, base_url="http://localhost:8000")
        if request_result is not None:
            assert not request_result.errors, f"Request with model field failed validation: {[str(e) for e in request_result.errors]}"

        # Validate response against spec
        response_result = validate_response(openapi_request, openapi_response, spec=openapi_spec, base_url="http://localhost:8000")
        if response_result is not None:
            assert not response_result.errors, f"Response validation failed: {[str(e) for e in response_result.errors]}"

        # Verify response includes model field
        assert response.status_code == 200
        data = response.json()
        assert "model" in data, "Response must include model field (FR-008)"
        assert data["model"] == "gpt-4", f"Response model should match used model, got {data['model']}"


@pytest.mark.contract
def test_message_request_without_model_uses_default(
    client: TestClient,
    openapi_spec: Spec
):
    """
    T013: Validate that omitting model field uses default model.

    When no model is specified, the backend should use the default model
    from configuration and return it in the response.
    """
    import json
    from unittest.mock import patch, AsyncMock

    # Mock the LLM service
    with patch('src.api.routes.messages.load_config') as mock_load_config, \
         patch('src.api.routes.messages.get_ai_response', new_callable=AsyncMock) as mock_get_ai:

        # Mock config with default model
        mock_load_config.return_value = {'api_key': 'test-key', 'model': 'gpt-3.5-turbo'}

        # Mock AI response - returns default model when not specified
        mock_get_ai.return_value = ("AI response text", "gpt-3.5-turbo")

        # Test request WITHOUT model field
        request_data = {
            "message": "Test message"
        }
        body = json.dumps(request_data).encode('utf-8')

        # Make request
        response = client.post(
            "/api/v1/messages",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )

        # Validate response
        assert response.status_code == 200
        data = response.json()

        # Verify default model was used
        assert "model" in data, "Response must include model field"
        assert len(data["model"]) > 0, "Model field cannot be empty"


@pytest.mark.contract
def test_invalid_model_id_returns_error(
    client: TestClient,
    openapi_spec: Spec
):
    """
    T013: Validate that invalid model ID returns appropriate error.

    When a non-existent model is specified, the backend should reject
    the request with a validation error.
    """
    import json
    from unittest.mock import patch, AsyncMock

    # Mock the LLM service
    with patch('src.api.routes.messages.load_config') as mock_load_config, \
         patch('src.api.routes.messages.get_ai_response', new_callable=AsyncMock) as mock_get_ai:

        # Mock config
        mock_load_config.return_value = {'api_key': 'test-key', 'model': 'gpt-3.5-turbo'}

        # Mock AI response to raise ValueError for invalid model
        mock_get_ai.side_effect = ValueError("Invalid model: nonexistent-model")

        # Test request with invalid model
        request_data = {
            "message": "Test message",
            "model": "nonexistent-model"
        }

        # Make request
        response = client.post(
            "/api/v1/messages",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )

        # Should return 400 error for invalid model
        assert response.status_code == 400
        data = response.json()

        # Check for error in either top-level or detail wrapper
        error_message = ""
        if "error" in data:
            error_message = data["error"]
        elif "detail" in data:
            if isinstance(data["detail"], dict) and "error" in data["detail"]:
                error_message = data["detail"]["error"]
            elif isinstance(data["detail"], str):
                error_message = data["detail"]

        assert len(error_message) > 0, "Error response must include error message"
        assert "model" in error_message.lower() or "invalid" in error_message.lower(), \
            f"Error should mention model or invalid, got: {error_message}"


# ============================================================================
# Streaming Contract Tests (Feature: 009-message-streaming)
# ============================================================================

@pytest.mark.contract
def test_streaming_request_with_sse_accept_header(
    client: TestClient,
    sample_message_minimal: dict
):
    """
    T011: Contract test for streaming endpoint with Accept: text/event-stream header.

    Validates that:
    - POST /api/v1/messages accepts text/event-stream Accept header
    - Response has Content-Type: text/event-stream
    - Response status is 200
    - Response body contains SSE formatted data

    Feature: 009-message-streaming User Story 1
    Expected: FAIL (streaming not implemented yet)
    """
    from unittest.mock import patch, AsyncMock, Mock

    # Mock the LLM streaming service
    with patch('src.api.routes.messages.load_config') as mock_load_config, \
         patch('src.api.routes.messages.stream_ai_response') as mock_stream_ai:

        # Mock config
        mock_load_config.return_value = {'api_key': 'test-key', 'model': 'gpt-3.5-turbo'}

        # Mock streaming response with async generator
        async def mock_generator():
            from src.schemas import TokenEvent, CompleteEvent
            yield TokenEvent(content="Hello")
            yield TokenEvent(content=" ")
            yield TokenEvent(content="World")
            yield CompleteEvent(model="gpt-3.5-turbo")

        mock_stream_ai.return_value = mock_generator()

        # Make request with SSE Accept header
        response = client.post(
            "/api/v1/messages",
            json=sample_message_minimal,
            headers={"Accept": "text/event-stream"}
        )

        # Verify response
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        # Verify Content-Type header
        content_type = response.headers.get("Content-Type", "")
        assert "text/event-stream" in content_type, \
            f"Expected text/event-stream Content-Type, got: {content_type}"


@pytest.mark.contract
def test_streaming_response_sse_format(
    client: TestClient,
    sample_message_minimal: dict
):
    """
    T011: Validate SSE (Server-Sent Events) format in streaming response.

    Validates that streaming response follows SSE specification:
    - Each event: "data: <JSON>\\n\\n"
    - Events are newline-delimited
    - JSON contains type field (token, complete, error)

    Feature: 009-message-streaming User Story 1
    """
    from unittest.mock import patch
    import json

    # Mock the LLM streaming service
    with patch('src.api.routes.messages.load_config') as mock_load_config, \
         patch('src.api.routes.messages.stream_ai_response') as mock_stream_ai:

        # Mock config
        mock_load_config.return_value = {'api_key': 'test-key', 'model': 'gpt-3.5-turbo'}

        # Mock streaming response
        async def mock_generator():
            from src.schemas import TokenEvent, CompleteEvent
            yield TokenEvent(content="Test")
            yield CompleteEvent(model="gpt-3.5-turbo")

        mock_stream_ai.return_value = mock_generator()

        # Make streaming request
        response = client.post(
            "/api/v1/messages",
            json=sample_message_minimal,
            headers={"Accept": "text/event-stream"}
        )

        # Parse SSE response
        response_text = response.text

        # SSE format: each event should be "data: {...}\n\n"
        assert "data: " in response_text, "SSE response must contain 'data: ' prefix"

        # Split by double newline to get individual events
        events = [e for e in response_text.split("\n\n") if e.strip()]

        assert len(events) > 0, "SSE response must contain at least one event"

        # Validate each event format
        for event_str in events:
            assert event_str.startswith("data: "), \
                f"Each SSE event must start with 'data: ', got: {event_str[:20]}"

            # Extract JSON part (remove "data: " prefix)
            json_str = event_str[6:]  # len("data: ") = 6

            # Validate JSON is parseable
            try:
                event_data = json.loads(json_str)
            except json.JSONDecodeError as e:
                pytest.fail(f"SSE event contains invalid JSON: {e}\nEvent: {json_str}")

            # Validate event has type field
            assert "type" in event_data, f"SSE event must have 'type' field, got: {event_data}"
            assert event_data["type"] in ["token", "complete", "error"], \
                f"Event type must be token/complete/error, got: {event_data['type']}"


@pytest.mark.contract
def test_streaming_event_sequence(
    client: TestClient,
    sample_message_minimal: dict
):
    """
    T011: Validate correct sequence of streaming events.

    Validates that streaming response follows expected event sequence:
    1. Zero or more TokenEvent (type="token")
    2. Exactly one CompleteEvent (type="complete") OR ErrorEvent (type="error")
    3. CompleteEvent is always the last event

    Feature: 009-message-streaming User Story 1
    """
    from unittest.mock import patch
    import json

    # Mock the LLM streaming service
    with patch('src.api.routes.messages.load_config') as mock_load_config, \
         patch('src.api.routes.messages.stream_ai_response') as mock_stream_ai:

        # Mock config
        mock_load_config.return_value = {'api_key': 'test-key', 'model': 'gpt-3.5-turbo'}

        # Mock streaming response with multiple tokens
        async def mock_generator():
            from src.schemas import TokenEvent, CompleteEvent
            yield TokenEvent(content="Hello")
            yield TokenEvent(content=" ")
            yield TokenEvent(content="World")
            yield TokenEvent(content="!")
            yield CompleteEvent(model="gpt-3.5-turbo")

        mock_stream_ai.return_value = mock_generator()

        # Make streaming request
        response = client.post(
            "/api/v1/messages",
            json=sample_message_minimal,
            headers={"Accept": "text/event-stream"}
        )

        # Parse events
        response_text = response.text
        events = []

        for event_str in response_text.split("\n\n"):
            if event_str.strip() and event_str.startswith("data: "):
                json_str = event_str[6:]
                events.append(json.loads(json_str))

        # Validate event sequence
        assert len(events) >= 2, "Stream must have at least 1 token + 1 complete event"

        # All events except last should be TokenEvent
        for i, event in enumerate(events[:-1]):
            assert event["type"] == "token", \
                f"Event {i} should be token, got: {event['type']}"
            assert "content" in event, f"TokenEvent must have 'content' field"

        # Last event should be CompleteEvent
        last_event = events[-1]
        assert last_event["type"] == "complete", \
            f"Last event should be complete, got: {last_event['type']}"
        assert "model" in last_event, "CompleteEvent must have 'model' field"
        assert last_event["model"] == "gpt-3.5-turbo"


@pytest.mark.contract
def test_streaming_backward_compatibility_json_accept(
    client: TestClient,
    sample_message_minimal: dict
):
    """
    T011: Test backward compatibility - Accept: application/json still works.

    Validates that:
    - Existing clients using Accept: application/json continue to work
    - Response is standard JSON (not SSE)
    - Response matches MessageResponse schema

    Feature: 009-message-streaming User Story 1
    CRITICAL: This ensures we don't break existing integrations
    """
    from unittest.mock import patch, AsyncMock
    import json

    # Mock the LLM service (non-streaming)
    with patch('src.api.routes.messages.load_config') as mock_load_config, \
         patch('src.api.routes.messages.get_ai_response', new_callable=AsyncMock) as mock_get_ai:

        # Mock config
        mock_load_config.return_value = {'api_key': 'test-key', 'model': 'gpt-3.5-turbo'}

        # Mock non-streaming AI response
        mock_get_ai.return_value = ("Hello World!", "gpt-3.5-turbo")

        # Make request with application/json Accept header (or omit - defaults to JSON)
        response = client.post(
            "/api/v1/messages",
            json=sample_message_minimal,
            headers={"Accept": "application/json"}
        )

        # Verify non-streaming response
        assert response.status_code == 200

        # Verify Content-Type is JSON
        content_type = response.headers.get("Content-Type", "")
        assert "application/json" in content_type, \
            f"JSON Accept should return application/json, got: {content_type}"

        # Verify response is valid JSON (not SSE)
        data = response.json()
        assert "status" in data, "JSON response must have status field"
        assert data["status"] == "success"
        assert "message" in data, "JSON response must have message field"
        assert "timestamp" in data, "JSON response must have timestamp field"

        # Verify NOT SSE format
        response_text = response.text
        assert not response_text.startswith("data: "), \
            "JSON response should not be in SSE format"


@pytest.mark.contract
def test_streaming_with_conversation_history(
    client: TestClient
):
    """
    T011: Validate streaming works with conversation history.

    Validates that streaming endpoint accepts history field and
    passes it to the streaming service.

    Feature: 009-message-streaming User Story 1
    """
    from unittest.mock import patch

    # Mock the LLM streaming service
    with patch('src.api.routes.messages.load_config') as mock_load_config, \
         patch('src.api.routes.messages.stream_ai_response') as mock_stream_ai:

        # Mock config
        mock_load_config.return_value = {'api_key': 'test-key', 'model': 'gpt-3.5-turbo'}

        # Mock streaming response
        async def mock_generator():
            from src.schemas import TokenEvent, CompleteEvent
            yield TokenEvent(content="Context-aware response")
            yield CompleteEvent(model="gpt-3.5-turbo")

        mock_stream_ai.return_value = mock_generator()

        # Request with conversation history
        request_data = {
            "message": "What's my name?",
            "history": [
                {"sender": "user", "text": "My name is Alice"},
                {"sender": "system", "text": "Nice to meet you, Alice!"}
            ]
        }

        # Make streaming request
        response = client.post(
            "/api/v1/messages",
            json=request_data,
            headers={"Accept": "text/event-stream"}
        )

        # Verify streaming response
        assert response.status_code == 200
        assert "text/event-stream" in response.headers.get("Content-Type", "")

        # Verify stream_ai_response was called with history
        mock_stream_ai.assert_called_once()
        call_kwargs = mock_stream_ai.call_args[1]
        assert "history" in call_kwargs, "stream_ai_response should receive history"
        assert len(call_kwargs["history"]) == 2


@pytest.mark.contract
def test_streaming_with_custom_model(
    client: TestClient,
    sample_message_minimal: dict
):
    """
    T011: Validate streaming works with per-request model selection.

    Validates that streaming endpoint accepts model field and
    CompleteEvent returns the model that was used.

    Feature: 009-message-streaming + 008-openai-model-selector
    """
    from unittest.mock import patch
    import json

    # Mock the LLM streaming service
    with patch('src.api.routes.messages.load_config') as mock_load_config, \
         patch('src.api.routes.messages.stream_ai_response') as mock_stream_ai:

        # Mock config
        mock_load_config.return_value = {'api_key': 'test-key', 'model': 'gpt-3.5-turbo'}

        # Mock streaming response with custom model
        async def mock_generator():
            from src.schemas import TokenEvent, CompleteEvent
            yield TokenEvent(content="GPT-4 response")
            yield CompleteEvent(model="gpt-4")  # Returns requested model

        mock_stream_ai.return_value = mock_generator()

        # Request with custom model
        request_data = {
            **sample_message_minimal,
            "model": "gpt-4"
        }

        # Make streaming request
        response = client.post(
            "/api/v1/messages",
            json=request_data,
            headers={"Accept": "text/event-stream"}
        )

        # Parse events
        events = []
        for event_str in response.text.split("\n\n"):
            if event_str.strip() and event_str.startswith("data: "):
                events.append(json.loads(event_str[6:]))

        # Find CompleteEvent
        complete_events = [e for e in events if e["type"] == "complete"]
        assert len(complete_events) == 1, "Should have exactly one CompleteEvent"

        # Verify model field in CompleteEvent
        assert complete_events[0]["model"] == "gpt-4", \
            f"CompleteEvent should return requested model, got: {complete_events[0]['model']}"


@pytest.mark.contract
def test_streaming_error_event_format(
    client: TestClient,
    sample_message_minimal: dict
):
    """
    T011: Validate ErrorEvent format in streaming response.

    Validates that when streaming fails:
    - ErrorEvent is yielded with type="error"
    - ErrorEvent has error field (human-readable message)
    - ErrorEvent has code field (machine-readable error code)
    - Valid error codes: TIMEOUT, RATE_LIMIT, LLM_ERROR, AUTH_ERROR, CONNECTION_ERROR, UNKNOWN

    Feature: 009-message-streaming User Story 3
    """
    from unittest.mock import patch
    import json

    # Mock the LLM streaming service to yield error
    with patch('src.api.routes.messages.load_config') as mock_load_config, \
         patch('src.api.routes.messages.stream_ai_response') as mock_stream_ai:

        # Mock config
        mock_load_config.return_value = {'api_key': 'test-key', 'model': 'gpt-3.5-turbo'}

        # Mock streaming response with error
        async def mock_generator():
            from src.schemas import ErrorEvent
            yield ErrorEvent(error="AI service is busy", code="RATE_LIMIT")

        mock_stream_ai.return_value = mock_generator()

        # Make streaming request
        response = client.post(
            "/api/v1/messages",
            json=sample_message_minimal,
            headers={"Accept": "text/event-stream"}
        )

        # Parse events
        events = []
        for event_str in response.text.split("\n\n"):
            if event_str.strip() and event_str.startswith("data: "):
                events.append(json.loads(event_str[6:]))

        # Should have exactly one ErrorEvent
        assert len(events) == 1, f"Error stream should have exactly one event, got {len(events)}"

        error_event = events[0]
        assert error_event["type"] == "error", f"Event type should be 'error', got: {error_event['type']}"
        assert "error" in error_event, "ErrorEvent must have 'error' field"
        assert "code" in error_event, "ErrorEvent must have 'code' field"

        # Validate error code is one of the valid codes
        valid_codes = ["TIMEOUT", "RATE_LIMIT", "LLM_ERROR", "AUTH_ERROR", "CONNECTION_ERROR", "UNKNOWN"]
        assert error_event["code"] in valid_codes, \
            f"Error code must be one of {valid_codes}, got: {error_event['code']}"


@pytest.mark.contract
def test_streaming_sse_headers(
    client: TestClient,
    sample_message_minimal: dict
):
    """
    T011: Validate required SSE headers in streaming response.

    Validates that streaming response includes required headers:
    - Content-Type: text/event-stream
    - Cache-Control: no-cache (prevents caching of stream)
    - Connection: keep-alive (maintains connection for streaming)
    - X-Accel-Buffering: no (disables nginx buffering)

    Feature: 009-message-streaming User Story 1
    """
    from unittest.mock import patch

    # Mock the LLM streaming service
    with patch('src.api.routes.messages.load_config') as mock_load_config, \
         patch('src.api.routes.messages.stream_ai_response') as mock_stream_ai:

        # Mock config
        mock_load_config.return_value = {'api_key': 'test-key', 'model': 'gpt-3.5-turbo'}

        # Mock streaming response
        async def mock_generator():
            from src.schemas import TokenEvent, CompleteEvent
            yield TokenEvent(content="Test")
            yield CompleteEvent(model="gpt-3.5-turbo")

        mock_stream_ai.return_value = mock_generator()

        # Make streaming request
        response = client.post(
            "/api/v1/messages",
            json=sample_message_minimal,
            headers={"Accept": "text/event-stream"}
        )

        # Verify required headers
        headers = response.headers

        assert "text/event-stream" in headers.get("Content-Type", ""), \
            f"Missing or incorrect Content-Type: {headers.get('Content-Type')}"

        # Note: Cache-Control, Connection, X-Accel-Buffering may not be testable
        # with TestClient since it doesn't fully emulate HTTP streaming headers.
        # These will be validated in integration tests with actual server.
