"""
Contract Tests for Message API

Validates that API requests and responses match the OpenAPI specification.
Uses openapi-core for schema validation.

Feature: 003-backend-api-loopback User Story 1
Tests: T021, T022 (TDD - these should FAIL before implementation)
"""

import pytest
from fastapi.testclient import TestClient
from openapi_core import Spec
from openapi_core.validation.request import openapi_request_validator
from openapi_core.validation.response import openapi_response_validator
from openapi_core.protocols import Request, Response


@pytest.mark.contract
def test_loopback_request_matches_contract(
    client: TestClient,
    openapi_spec: Spec,
    sample_message_request: dict
):
    """
    T021: Validate that MessageRequest matches OpenAPI contract.

    Tests that the request payload structure, types, and validation
    rules match the specification in message-api.yaml.

    Expected: FAIL (endpoint not implemented yet)
    """
    # Make request
    response = client.post("/api/v1/messages", json=sample_message_request)

    # Create OpenAPI request object for validation
    openapi_request = RequestsOpenAPIRequest(response.request)

    # Validate request against schema
    validator = RequestValidator(openapi_spec)
    result = validator.validate(openapi_request)

    # Assert no validation errors
    assert result.errors == [], f"Request validation errors: {result.errors}"


@pytest.mark.contract
def test_loopback_response_matches_contract(
    client: TestClient,
    openapi_spec: Spec,
    sample_message_request: dict
):
    """
    T022: Validate that MessageResponse matches OpenAPI contract.

    Tests that the response payload structure, types, and required fields
    match the specification in message-api.yaml.

    Expected: FAIL (endpoint not implemented yet)
    """
    # Make request
    response = client.post("/api/v1/messages", json=sample_message_request)

    # Create OpenAPI request/response objects for validation
    openapi_request = RequestsOpenAPIRequest(response.request)
    openapi_response = RequestsOpenAPIResponse(response)

    # Validate response against schema
    validator = ResponseValidator(openapi_spec)
    result = validator.validate(openapi_request, openapi_response)

    # Assert no validation errors
    assert result.errors == [], f"Response validation errors: {result.errors}"

    # Additional assertions for success response
    if response.status_code == 200:
        data = response.json()
        assert data["status"] == "success"
        assert data["message"].startswith("api says: ")
        assert "timestamp" in data


@pytest.mark.contract
def test_minimal_request_matches_contract(
    client: TestClient,
    openapi_spec: Spec,
    sample_message_minimal: dict
):
    """
    Test minimal request (only required fields) matches contract.

    Expected: FAIL (endpoint not implemented yet)
    """
    response = client.post("/api/v1/messages", json=sample_message_minimal)

    openapi_request = RequestsOpenAPIRequest(response.request)
    validator = RequestValidator(openapi_spec)
    result = validator.validate(openapi_request)

    assert result.errors == [], f"Request validation errors: {result.errors}"


@pytest.mark.contract
def test_special_characters_request_matches_contract(
    client: TestClient,
    openapi_spec: Spec,
    sample_message_special_chars: dict
):
    """
    Test request with special characters matches contract.

    Validates FR-010: Backend accepts special characters, emoji, multi-byte characters.

    Expected: FAIL (endpoint not implemented yet)
    """
    response = client.post("/api/v1/messages", json=sample_message_special_chars)

    openapi_request = RequestsOpenAPIRequest(response.request)
    validator = RequestValidator(openapi_spec)
    result = validator.validate(openapi_request)

    assert result.errors == [], f"Request validation errors: {result.errors}"


@pytest.mark.contract
def test_error_response_matches_contract(
    client: TestClient,
    openapi_spec: Spec
):
    """
    Test error response (400) matches contract.

    Validates error response structure for invalid requests.

    Expected: FAIL (endpoint not implemented yet)
    """
    # Send empty message (should trigger 400 error)
    response = client.post("/api/v1/messages", json={"message": ""})

    # Create OpenAPI response object
    openapi_request = RequestsOpenAPIRequest(response.request)
    openapi_response = RequestsOpenAPIResponse(response)

    # Validate error response
    validator = ResponseValidator(openapi_spec)
    result = validator.validate(openapi_request, openapi_response)

    assert result.errors == [], f"Error response validation errors: {result.errors}"

    # Additional assertions for error response
    if response.status_code == 400:
        data = response.json()
        assert data["status"] == "error"
        assert "error" in data
        assert "timestamp" in data
