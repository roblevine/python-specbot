"""
Contract Tests for Models API

Validates that GET /api/v1/models matches the OpenAPI specification.
Uses openapi-core for schema validation.

Feature: 008-openai-model-selector User Story 1
Task: T012 (TDD - this should FAIL before implementation is complete)

CRITICAL: This test validates that frontend and backend agree on the models contract.
If this fails, it indicates a breaking mismatch between client and server.
"""

import pytest
import json
import os
import yaml
from fastapi.testclient import TestClient
from openapi_core import Spec, validate_response
from openapi_core.protocols import Request as OpenAPIRequest, Response as OpenAPIResponse
from openapi_core.datatypes import RequestParameters, Headers
from werkzeug.datastructures import Headers as WerkzeugHeaders, ImmutableMultiDict


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

    @property
    def headers(self):
        return WerkzeugHeaders(self._response.headers.items())


@pytest.fixture(scope="session")
def models_openapi_spec() -> Spec:
    """
    Load OpenAPI specification for models endpoint contract testing.

    Returns:
        openapi_core.Spec object for validating requests/responses
    """
    # Path to models OpenAPI contract
    spec_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "..",
        "specs",
        "008-openai-model-selector",
        "contracts",
        "openapi-models.yaml"
    )

    # Load YAML spec
    with open(spec_path, 'r') as f:
        spec_dict = yaml.safe_load(f)

    # Create OpenAPI spec object
    return Spec.from_dict(spec_dict)


@pytest.mark.contract
def test_list_models_success_matches_contract(
    client: TestClient,
    models_openapi_spec: Spec
):
    """
    T012: Validate that GET /api/v1/models response matches OpenAPI contract.

    This test validates the successful 200 response:
    - Response structure matches ModelsResponse schema
    - models array contains ModelInfo objects
    - Each model has: id, name, description, default fields
    - At least one model is present
    - Exactly one model has default: true

    CRITICAL: If this fails, frontend and backend disagree on models format.
    """
    # Make request to models endpoint
    response = client.get("/api/v1/models")

    # Verify response is successful
    assert response.status_code == 200, \
        f"Expected 200, got {response.status_code}: {response.text}"

    # Parse response JSON
    response_data = response.json()

    # Validate structure exists
    assert "models" in response_data, "Response missing 'models' field"
    assert isinstance(response_data["models"], list), \
        "models field must be an array"
    assert len(response_data["models"]) >= 1, \
        "At least one model must be configured"

    # Validate each model has required fields
    for model in response_data["models"]:
        assert "id" in model, "Model missing 'id' field"
        assert "name" in model, "Model missing 'name' field"
        assert "description" in model, "Model missing 'description' field"
        assert "default" in model, "Model missing 'default' field"

        assert isinstance(model["id"], str), "Model id must be string"
        assert isinstance(model["name"], str), "Model name must be string"
        assert isinstance(model["description"], str), \
            "Model description must be string"
        assert isinstance(model["default"], bool), \
            "Model default must be boolean"

    # Validate exactly one default model
    default_count = sum(1 for m in response_data["models"] if m["default"])
    assert default_count == 1, \
        f"Exactly one model must be default, found {default_count}"

    # Validate response against OpenAPI schema using openapi-core
    # Create request adapter for GET request (no body)
    openapi_request = FastAPIOpenAPIRequest(response.request, b'')
    openapi_response = FastAPIOpenAPIResponse(response)

    # Validate response against spec
    result = validate_response(
        openapi_request,
        openapi_response,
        spec=models_openapi_spec,
        base_url="http://localhost:8000"
    )

    # If result is None, validation passed
    if result is not None:
        assert not result.errors, f"Response validation errors: {[str(e) for e in result.errors]}"


@pytest.mark.contract
def test_list_models_field_types(client: TestClient):
    """
    Additional validation: Verify field types and constraints.

    Validates:
    - Model ID is non-empty
    - Model name is non-empty (max 50 chars per data-model.md)
    - Model description is non-empty (max 200 chars per data-model.md)
    """
    response = client.get("/api/v1/models")
    assert response.status_code == 200

    models = response.json()["models"]

    for model in models:
        # ID validation
        assert len(model["id"]) > 0, "Model ID cannot be empty"

        # Name validation
        assert len(model["name"]) > 0, "Model name cannot be empty"
        assert len(model["name"]) <= 50, \
            f"Model name too long: {len(model['name'])} chars (max 50)"

        # Description validation
        assert len(model["description"]) > 0, \
            "Model description cannot be empty"
        assert len(model["description"]) <= 200, \
            f"Model description too long: {len(model['description'])} chars (max 200)"


@pytest.mark.contract
def test_list_models_no_duplicate_ids(client: TestClient):
    """
    Additional validation: Verify no duplicate model IDs.

    Per data-model.md: All model IDs must be unique.
    """
    response = client.get("/api/v1/models")
    assert response.status_code == 200

    models = response.json()["models"]
    ids = [m["id"] for m in models]

    assert len(ids) == len(set(ids)), \
        f"Duplicate model IDs found: {ids}"


@pytest.mark.contract
def test_list_models_includes_common_models(client: TestClient):
    """
    Smoke test: Verify response includes expected OpenAI models.

    This is not a strict requirement but verifies configuration is reasonable.
    """
    response = client.get("/api/v1/models")
    assert response.status_code == 200

    models = response.json()["models"]
    model_ids = [m["id"] for m in models]

    # At least verify we have some model configured
    # (Specific models depend on environment configuration)
    assert len(model_ids) > 0, "Expected at least one configured model"

    # Log configured models for debugging
    print(f"\nConfigured models: {model_ids}")
