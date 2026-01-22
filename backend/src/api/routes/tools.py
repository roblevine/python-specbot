"""
Tools API endpoint for listing available tools.

Feature: 023-add-search-tools Task T030
"""

from fastapi import APIRouter

from src.schemas import ToolInfo, ToolsResponse
from src.services.tools import registry

router = APIRouter(tags=["Tools"])


@router.get("/tools", response_model=ToolsResponse)
async def list_tools() -> ToolsResponse:
    """List all available tools.

    Returns information about all registered tools including
    their ID, name, description, and enabled status.

    Returns:
        ToolsResponse with list of ToolInfo objects
    """
    tools = [
        ToolInfo(
            id=t.id,
            name=t.name,
            description=t.description,
            enabled=t.is_enabled()
        )
        for t in registry.get_all()
    ]
    return ToolsResponse(tools=tools)
