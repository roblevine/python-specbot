"""
Contract Tests for Chat Streaming API

Validates that streaming API requests and responses match the OpenAPI specification.
Uses openapi-core for schema validation.

Feature: 005-llm-integration User Story 1
Task: T014 (TDD - should FAIL before implementation)

CRITICAL: These tests validate that frontend and backend agree on the streaming contract.
If these fail, it indicates a breaking mismatch between client and server.
"""

import json
import pytest
from fastapi.testclient import TestClient
from openapi_core import Spec, validate_request
from openapi_core.protocols import Request as OpenAPIRequest
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


@pytest.mark.contract
def test_chat_stream_request_matches_contract(
    client: TestClient,
    chat_openapi_spec: Spec,
    sample_chat_stream_request: dict
):
    """
    T014: Validate that ChatStreamRequest matches OpenAPI contract.

    This test validates ALL fields in the streaming request:
    - message: required string 1-10,000 chars
    - conversationId: required string with conv-{uuid} pattern
    - conversationHistory: optional array of HistoryMessage objects
    - model: optional enum (gpt-5, gpt-5-codex), default gpt-5

    CRITICAL: If this fails, frontend and backend disagree on request format.
    """
    # Prepare request body
    body = json.dumps(sample_chat_stream_request).encode('utf-8')

    # Make the actual request
    response = client.post(
        "/api/v1/chat/stream",
        json=sample_chat_stream_request,
        headers={"Content-Type": "application/json"}
    )

    # Create OpenAPI request object
    openapi_request = FastAPIOpenAPIRequest(response.request, body)

    # Validate request against OpenAPI spec
    result = validate_request(openapi_request, spec=chat_openapi_spec, base_url="http://localhost:8000")

    # If result is None, validation passed
    if result is not None:
        assert not result.errors, f"Request validation errors: {[str(e) for e in result.errors]}"


@pytest.mark.contract
def test_chat_stream_minimal_request_matches_contract(
    client: TestClient,
    chat_openapi_spec: Spec
):
    """
    Test minimal streaming request (only required fields) matches contract.

    Validates that optional fields (conversationHistory, model) are truly optional.
    """
    minimal_request = {
        "message": "Hello",
        "conversationId": "conv-123e4567-e89b-12d3-a456-426614174000"
    }

    body = json.dumps(minimal_request).encode('utf-8')
    response = client.post("/api/v1/chat/stream", json=minimal_request)

    openapi_request = FastAPIOpenAPIRequest(response.request, body)
    result = validate_request(openapi_request, spec=chat_openapi_spec, base_url="http://localhost:8000")

    if result is not None:
        assert not result.errors, f"Minimal request validation errors: {[str(e) for e in result.errors]}"


@pytest.mark.contract
def test_chat_stream_with_history_matches_contract(
    client: TestClient,
    chat_openapi_spec: Spec,
    sample_chat_stream_request_with_history: dict
):
    """
    Test streaming request with conversation history matches contract.

    Validates that conversationHistory array structure is correct.
    """
    body = json.dumps(sample_chat_stream_request_with_history).encode('utf-8')
    response = client.post("/api/v1/chat/stream", json=sample_chat_stream_request_with_history)

    openapi_request = FastAPIOpenAPIRequest(response.request, body)
    result = validate_request(openapi_request, spec=chat_openapi_spec, base_url="http://localhost:8000")

    if result is not None:
        assert not result.errors, f"Request with history validation errors: {[str(e) for e in result.errors]}"


@pytest.mark.contract
def test_conversation_id_format_validated_by_contract(
    client: TestClient,
    chat_openapi_spec: Spec
):
    """
    Test that conversationId format is strictly validated by contract.

    CRITICAL: This test ensures that if frontend sends wrong ID format,
    it will be caught by contract validation.

    Valid format: conv-{uuid}
    Invalid formats: raw uuid, wrong prefix, malformed uuid
    """
    from openapi_core.validation.exceptions import ValidationError as OpenAPIValidationError

    test_cases = [
        # Valid cases - should pass contract validation
        {
            "request": {
                "message": "Test",
                "conversationId": "conv-a1b2c3d4-5678-90ab-cdef-123456789abc"
            },
            "should_pass_contract": True,
            "description": "Valid conv-{uuid} format"
        },
        # Invalid cases - should fail contract validation
        {
            "request": {
                "message": "Test",
                "conversationId": "a1b2c3d4-5678-90ab-cdef-123456789abc"
            },
            "should_pass_contract": False,
            "description": "Raw UUID without conv- prefix"
        },
        {
            "request": {
                "message": "Test",
                "conversationId": "not-a-uuid"
            },
            "should_pass_contract": False,
            "description": "Invalid format"
        },
        {
            "request": {
                "message": "Test",
                "conversationId": "msg-a1b2c3d4-5678-90ab-cdef-123456789abc"
            },
            "should_pass_contract": False,
            "description": "Wrong prefix (msg- instead of conv-)"
        },
    ]

    for case in test_cases:
        body = json.dumps(case["request"]).encode('utf-8')
        response = client.post("/api/v1/chat/stream", json=case["request"])

        openapi_request = FastAPIOpenAPIRequest(response.request, body)

        if case["should_pass_contract"]:
            # Should pass validation without errors or exceptions
            result = validate_request(openapi_request, spec=chat_openapi_spec, base_url="http://localhost:8000")
            if result is not None:
                assert not result.errors, f"{case['description']}: Expected to pass contract but got errors: {[str(e) for e in result.errors]}"
        else:
            # Should fail validation (either raise exception or return errors)
            validation_failed = False

            try:
                result = validate_request(openapi_request, spec=chat_openapi_spec, base_url="http://localhost:8000")
                if result is not None and result.errors:
                    validation_failed = True
            except OpenAPIValidationError:
                validation_failed = True

            assert validation_failed, f"{case['description']}: Expected to fail contract validation but passed"


@pytest.mark.contract
def test_model_enum_validated_by_contract(
    client: TestClient,
    chat_openapi_spec: Spec
):
    """
    Test that model field is validated against enum values.

    Valid models: gpt-5, gpt-5-codex
    Invalid: any other string
    """
    from openapi_core.validation.exceptions import ValidationError as OpenAPIValidationError

    # Valid model - should pass
    valid_request = {
        "message": "Test",
        "conversationId": "conv-123e4567-e89b-12d3-a456-426614174000",
        "model": "gpt-5-codex"
    }

    body = json.dumps(valid_request).encode('utf-8')
    response = client.post("/api/v1/chat/stream", json=valid_request)
    openapi_request = FastAPIOpenAPIRequest(response.request, body)
    result = validate_request(openapi_request, spec=chat_openapi_spec, base_url="http://localhost:8000")

    if result is not None:
        assert not result.errors, f"Valid model should pass: {[str(e) for e in result.errors]}"

    # Invalid model - should fail
    invalid_request = {
        "message": "Test",
        "conversationId": "conv-123e4567-e89b-12d3-a456-426614174000",
        "model": "gpt-4"  # Invalid model
    }

    body = json.dumps(invalid_request).encode('utf-8')
    response = client.post("/api/v1/chat/stream", json=invalid_request)
    openapi_request = FastAPIOpenAPIRequest(response.request, body)

    validation_failed = False
    try:
        result = validate_request(openapi_request, spec=chat_openapi_spec, base_url="http://localhost:8000")
        if result is not None and result.errors:
            validation_failed = True
    except OpenAPIValidationError:
        validation_failed = True

    assert validation_failed, "Invalid model should fail contract validation"


@pytest.mark.contract
def test_message_length_validated_by_contract(
    client: TestClient,
    chat_openapi_spec: Spec
):
    """
    Test that message length is validated (1-10,000 characters).
    """
    from openapi_core.validation.exceptions import ValidationError as OpenAPIValidationError

    # Empty message - should fail
    empty_request = {
        "message": "",
        "conversationId": "conv-123e4567-e89b-12d3-a456-426614174000"
    }

    body = json.dumps(empty_request).encode('utf-8')
    response = client.post("/api/v1/chat/stream", json=empty_request)
    openapi_request = FastAPIOpenAPIRequest(response.request, body)

    validation_failed = False
    try:
        result = validate_request(openapi_request, spec=chat_openapi_spec, base_url="http://localhost:8000")
        if result is not None and result.errors:
            validation_failed = True
    except OpenAPIValidationError:
        validation_failed = True

    assert validation_failed, "Empty message should fail contract validation"

    # Message at max length - should pass
    max_length_request = {
        "message": "x" * 10000,
        "conversationId": "conv-123e4567-e89b-12d3-a456-426614174000"
    }

    body = json.dumps(max_length_request).encode('utf-8')
    response = client.post("/api/v1/chat/stream", json=max_length_request)
    openapi_request = FastAPIOpenAPIRequest(response.request, body)
    result = validate_request(openapi_request, spec=chat_openapi_spec, base_url="http://localhost:8000")

    if result is not None:
        assert not result.errors, f"Max length message should pass: {[str(e) for e in result.errors]}"


@pytest.mark.contract
def test_history_message_structure_validated_by_contract(
    client: TestClient,
    chat_openapi_spec: Spec
):
    """
    Test that HistoryMessage structure is validated (role enum, content string).
    """
    from openapi_core.validation.exceptions import ValidationError as OpenAPIValidationError

    # Valid history structure - should pass
    valid_request = {
        "message": "Test",
        "conversationId": "conv-123e4567-e89b-12d3-a456-426614174000",
        "conversationHistory": [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "system", "content": "System message"}
        ]
    }

    body = json.dumps(valid_request).encode('utf-8')
    response = client.post("/api/v1/chat/stream", json=valid_request)
    openapi_request = FastAPIOpenAPIRequest(response.request, body)
    result = validate_request(openapi_request, spec=chat_openapi_spec, base_url="http://localhost:8000")

    if result is not None:
        assert not result.errors, f"Valid history should pass: {[str(e) for e in result.errors]}"

    # Invalid role in history - should fail
    invalid_request = {
        "message": "Test",
        "conversationId": "conv-123e4567-e89b-12d3-a456-426614174000",
        "conversationHistory": [
            {"role": "invalid_role", "content": "Hello"}
        ]
    }

    body = json.dumps(invalid_request).encode('utf-8')
    response = client.post("/api/v1/chat/stream", json=invalid_request)
    openapi_request = FastAPIOpenAPIRequest(response.request, body)

    validation_failed = False
    try:
        result = validate_request(openapi_request, spec=chat_openapi_spec, base_url="http://localhost:8000")
        if result is not None and result.errors:
            validation_failed = True
    except OpenAPIValidationError:
        validation_failed = True

    assert validation_failed, "Invalid role in history should fail contract validation"
