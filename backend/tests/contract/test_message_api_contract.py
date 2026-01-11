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
        mock_get_ai.return_value = "This is an AI response."

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
        mock_get_ai.return_value = "This is an AI response to your test message."

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
        mock_get_ai.return_value = "Hello! I'm doing well, thank you for asking."

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
    from openai import AuthenticationError

    # Mock the LLM service to raise AuthenticationError
    with patch('src.api.routes.messages.load_config') as mock_load_config, \
         patch('src.api.routes.messages.get_ai_response', new_callable=AsyncMock) as mock_get_ai:

        # Mock config
        mock_load_config.return_value = {'api_key': 'test-key', 'model': 'gpt-3.5-turbo'}

        # Mock AI service to raise AuthenticationError
        mock_get_ai.side_effect = AuthenticationError("Invalid API key")

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
    import asyncio

    # Mock the LLM service to raise timeout
    with patch('src.api.routes.messages.load_config') as mock_load_config, \
         patch('src.api.routes.messages.get_ai_response', new_callable=AsyncMock) as mock_get_ai:

        # Mock config
        mock_load_config.return_value = {'api_key': 'test-key', 'model': 'gpt-3.5-turbo'}

        # Mock AI service to raise timeout
        mock_get_ai.side_effect = asyncio.TimeoutError("Request timed out")

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
