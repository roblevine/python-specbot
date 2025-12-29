"""
Contract Testing Helper Functions

Utilities for loading frontend contract snapshots and replaying them
to the backend to verify contract compatibility.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

from fastapi.testclient import TestClient


def load_snapshots() -> List[Dict[str, Any]]:
    """
    Load all contract snapshots from the shared snapshot directory.

    Returns:
        List of snapshot dictionaries, each containing:
        - metadata: {operationId, capturedAt, frontendVersion}
        - request: {method, path, headers, body}

    Raises:
        FileNotFoundError: If snapshot directory doesn't exist
        ValueError: If no snapshots found (frontend tests must run first)
    """
    # Path to shared snapshot directory
    snapshot_dir = Path(__file__).parent.parent.parent.parent / "specs" / "contract-snapshots"

    if not snapshot_dir.exists():
        raise FileNotFoundError(
            f"Snapshot directory not found: {snapshot_dir}\n"
            "Run frontend contract tests first to generate snapshots."
        )

    # Load all JSON snapshot files
    snapshots = []
    for snapshot_file in snapshot_dir.glob("*.json"):
        if snapshot_file.name == ".gitkeep":
            continue

        with open(snapshot_file, 'r') as f:
            snapshot = json.load(f)
            snapshots.append(snapshot)

    if not snapshots:
        raise ValueError(
            "No contract snapshots found in specs/contract-snapshots/\n"
            "Run frontend contract tests first: cd frontend && npm test tests/contract/"
        )

    return snapshots


def replay_snapshot(client: TestClient, snapshot: Dict[str, Any]) -> Any:
    """
    Replay a frontend snapshot request to the backend.

    Takes a snapshot captured by frontend tests and replays it to the
    backend API to verify the backend can handle the actual frontend
    request format.

    Args:
        client: FastAPI TestClient instance
        snapshot: Snapshot dictionary from load_snapshots()

    Returns:
        Response object from the backend

    Example:
        >>> snapshot = {"request": {"method": "POST", "path": "/api/v1/messages", ...}}
        >>> response = replay_snapshot(client, snapshot)
        >>> assert response.status_code == 200
    """
    request = snapshot["request"]

    # Extract request details
    method = request["method"]
    path = request["path"]
    headers = request.get("headers", {})
    body = request.get("body")

    # Replay the request to the backend
    response = client.request(
        method=method,
        url=path,
        headers=headers,
        json=body if body is not None else None
    )

    return response


def validate_response_schema(response: Any, operation_id: str) -> List[str]:
    """
    Validate backend response against OpenAPI schema.

    Args:
        response: Response object from backend
        operation_id: OpenAPI operation ID (e.g., 'sendMessage')

    Returns:
        List of validation errors (empty if valid)
    """
    errors = []

    # Basic validation - response should be JSON
    try:
        response_data = response.json()
    except Exception as e:
        errors.append(f"Response is not valid JSON: {e}")
        return errors

    # Operation-specific validation
    if operation_id == "sendMessage":
        # Validate MessageResponse structure
        if "status" not in response_data:
            errors.append("Missing required field: status")
        elif response_data["status"] != "success":
            errors.append(f"Expected status 'success', got '{response_data['status']}'")

        if "message" not in response_data:
            errors.append("Missing required field: message")
        elif not response_data["message"].startswith("api says: "):
            errors.append("Response message must start with 'api says: '")

        if "timestamp" not in response_data:
            errors.append("Missing required field: timestamp")

    elif operation_id == "healthCheck":
        # Validate health check response
        if "status" not in response_data:
            errors.append("Missing required field: status")
        elif response_data["status"] != "ok":
            errors.append(f"Expected status 'ok', got '{response_data['status']}'")

    return errors
