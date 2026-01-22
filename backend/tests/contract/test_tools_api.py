"""
Contract tests for GET /api/v1/tools endpoint.

Feature: 023-add-search-tools Task T027
"""

import pytest
from fastapi.testclient import TestClient


class TestToolsEndpoint:
    """Contract tests for /api/v1/tools endpoint."""

    def test_get_tools_returns_200(self, client):
        """GET /api/v1/tools should return 200 OK."""
        response = client.get("/api/v1/tools")
        assert response.status_code == 200

    def test_get_tools_returns_tools_array(self, client):
        """Response should contain 'tools' array."""
        response = client.get("/api/v1/tools")
        data = response.json()

        assert "tools" in data
        assert isinstance(data["tools"], list)

    def test_tool_info_has_required_fields(self, client):
        """Each tool should have id, name, description, enabled fields."""
        response = client.get("/api/v1/tools")
        data = response.json()

        if len(data["tools"]) > 0:
            tool = data["tools"][0]
            assert "id" in tool
            assert "name" in tool
            assert "description" in tool
            assert "enabled" in tool

    def test_tool_id_format(self, client):
        """Tool id should match snake_case pattern."""
        response = client.get("/api/v1/tools")
        data = response.json()

        for tool in data["tools"]:
            assert isinstance(tool["id"], str)
            assert len(tool["id"]) >= 2
            # Check snake_case pattern (lowercase letters, digits, underscores)
            assert all(c.islower() or c.isdigit() or c == '_' for c in tool["id"])

    def test_enabled_is_boolean(self, client):
        """Tool enabled field should be boolean."""
        response = client.get("/api/v1/tools")
        data = response.json()

        for tool in data["tools"]:
            assert isinstance(tool["enabled"], bool)

    def test_default_tools_registered(self, client):
        """Web search and BBC news tools should be registered by default."""
        response = client.get("/api/v1/tools")
        data = response.json()

        tool_ids = [t["id"] for t in data["tools"]]
        assert "web_search" in tool_ids
        assert "bbc_news" in tool_ids

    def test_content_type_is_json(self, client):
        """Response content type should be application/json."""
        response = client.get("/api/v1/tools")
        assert "application/json" in response.headers["content-type"]
