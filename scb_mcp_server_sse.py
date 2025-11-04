#!/usr/bin/env python3
"""
SCB MCP Server (SSE) - MCP-compatible SSE server for OpenAI and other MCP clients
Uses proper MCP protocol over Server-Sent Events transport
"""

import json
import logging
import asyncio
from typing import Any
from pyscbwrapper import SCB
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent
from starlette.applications import Starlette
from starlette.routing import Route
from starlette.responses import Response
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scb-mcp-sse-server")

# Initialize the MCP server
mcp_server = Server("scb-statistics")

# Initialize SCB clients for both languages
scb_sv = SCB("sv")
scb_en = SCB("en")


def get_scb_client(lang: str = "sv") -> SCB:
    """Get SCB client for specified language"""
    return scb_en if lang.lower() == "en" else scb_sv


# MCP Tool definitions
@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List available SCB data tools"""
    return [
        Tool(
            name="scb_browse_metadata",
            description=(
                "Browse SCB metadata tree to discover available statistical tables. "
                "Start from root or navigate to specific paths. "
                "Returns metadata including table IDs, titles, and navigation options. "
                "Supports both Swedish (sv) and English (en)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path in metadata tree (e.g., 'AM/AM0401' or empty for root)",
                        "default": "",
                    },
                    "language": {
                        "type": "string",
                        "description": "Language for results: 'sv' (Swedish) or 'en' (English)",
                        "enum": ["sv", "en"],
                        "default": "sv",
                    },
                },
            },
        ),
        Tool(
            name="scb_search_tables",
            description=(
                "Search for statistical tables in SCB database using keywords. "
                "Returns matching tables with their IDs, titles, and descriptions. "
                "Supports both Swedish and English search."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'befolkning', 'population')",
                    },
                    "language": {
                        "type": "string",
                        "description": "Language for results: 'sv' (Swedish) or 'en' (English)",
                        "enum": ["sv", "en"],
                        "default": "sv",
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="scb_get_table_metadata",
            description=(
                "Get detailed metadata for a specific SCB table including available variables, "
                "dimensions, time periods, and value codes. Essential before fetching data."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": "string",
                        "description": "SCB table ID (e.g., 'BE0101N1')",
                    },
                    "language": {
                        "type": "string",
                        "description": "Language for results: 'sv' (Swedish) or 'en' (English)",
                        "enum": ["sv", "en"],
                        "default": "sv",
                    },
                },
                "required": ["table_id"],
            },
        ),
        Tool(
            name="scb_fetch_data",
            description=(
                "Fetch actual statistical data from an SCB table. "
                "Requires table_id and query specification with variables and values."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": "string",
                        "description": "SCB table ID",
                    },
                    "query": {
                        "type": "object",
                        "description": "Query specification. Example: {'Region': ['*'], 'Tid': ['2023']}",
                    },
                    "language": {
                        "type": "string",
                        "description": "Language: 'sv' or 'en'",
                        "enum": ["sv", "en"],
                        "default": "sv",
                    },
                },
                "required": ["table_id", "query"],
            },
        ),
        Tool(
            name="scb_get_table_info",
            description="Get comprehensive information about a specific table.",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": "string",
                        "description": "SCB table ID",
                    },
                    "language": {
                        "type": "string",
                        "enum": ["sv", "en"],
                        "default": "sv",
                    },
                },
                "required": ["table_id"],
            },
        ),
    ]


@mcp_server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    try:
        logger.info(f"Tool called: {name} with args: {arguments}")

        if name == "scb_browse_metadata":
            result = await browse_metadata(
                path=arguments.get("path", ""),
                language=arguments.get("language", "sv")
            )
        elif name == "scb_search_tables":
            result = await search_tables(
                query=arguments["query"],
                language=arguments.get("language", "sv")
            )
        elif name == "scb_get_table_metadata":
            result = await get_table_metadata(
                table_id=arguments["table_id"],
                language=arguments.get("language", "sv")
            )
        elif name == "scb_fetch_data":
            result = await fetch_data(
                table_id=arguments["table_id"],
                query=arguments["query"],
                language=arguments.get("language", "sv")
            )
        elif name == "scb_get_table_info":
            result = await get_table_info(
                table_id=arguments["table_id"],
                language=arguments.get("language", "sv")
            )
        else:
            raise ValueError(f"Unknown tool: {name}")

        return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]

    except Exception as e:
        logger.error(f"Error in {name}: {str(e)}", exc_info=True)
        return [TextContent(
            type="text",
            text=json.dumps({
                "error": str(e),
                "tool": name,
                "arguments": arguments
            }, indent=2, ensure_ascii=False)
        )]


# Tool implementations
async def browse_metadata(path: str = "", language: str = "sv") -> dict:
    """Browse SCB metadata tree"""
    scb = get_scb_client(language)
    try:
        if path:
            result = scb.go_down(path)
        else:
            result = scb.info()

        metadata = {
            "path": path or "root",
            "language": language,
            "items": []
        }

        if isinstance(result, list):
            for item in result:
                metadata["items"].append({
                    "id": item.get("id", ""),
                    "text": item.get("text", ""),
                    "type": item.get("type", ""),
                })

        return metadata
    except Exception as e:
        return {"error": str(e), "path": path, "language": language}


async def search_tables(query: str, language: str = "sv") -> dict:
    """Search for tables matching query"""
    scb = get_scb_client(language)
    try:
        root = scb.info()
        results = {
            "query": query,
            "language": language,
            "matches": []
        }

        query_lower = query.lower()
        for item in root:
            text = item.get("text", "").lower()
            if query_lower in text:
                results["matches"].append({
                    "id": item.get("id", ""),
                    "text": item.get("text", ""),
                    "type": item.get("type", ""),
                })

        return results
    except Exception as e:
        return {"error": str(e), "query": query, "language": language}


async def get_table_metadata(table_id: str, language: str = "sv") -> dict:
    """Get detailed metadata for a table"""
    scb = get_scb_client(language)
    try:
        scb.set_table(table_id)
        variables = scb.get_variables()

        return {
            "table_id": table_id,
            "language": language,
            "variables": variables
        }
    except Exception as e:
        return {"error": str(e), "table_id": table_id, "language": language}


async def fetch_data(table_id: str, query: dict, language: str = "sv") -> dict:
    """Fetch data from a table"""
    scb = get_scb_client(language)
    try:
        scb.set_table(table_id)
        scb_query = scb.get_query()

        for var_name, values in query.items():
            if "*" in values:
                scb_query[var_name] = scb_query[var_name]["values"]
            else:
                scb_query[var_name] = values

        data = scb.get_data(scb_query)

        return {
            "table_id": table_id,
            "language": language,
            "query": query,
            "data": data
        }
    except Exception as e:
        return {"error": str(e), "table_id": table_id, "query": query, "language": language}


async def get_table_info(table_id: str, language: str = "sv") -> dict:
    """Get general information about a table"""
    scb = get_scb_client(language)
    try:
        scb.set_table(table_id)
        return {
            "table_id": table_id,
            "language": language,
            "url": scb.get_url(),
            "info": "Table found and accessible"
        }
    except Exception as e:
        return {"error": str(e), "table_id": table_id, "language": language}


# Starlette app for SSE
async def handle_sse(request):
    """Handle SSE endpoint"""
    logger.info("SSE connection established")

    async with SseServerTransport("/messages") as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            mcp_server.create_initialization_options()
        )

    return Response()


async def handle_messages(request):
    """Handle POST messages"""
    return Response(status_code=200)


async def health(request):
    """Health check"""
    return Response(
        content=json.dumps({"status": "healthy", "service": "scb-mcp-sse-server"}),
        media_type="application/json"
    )


async def root(request):
    """Root endpoint"""
    return Response(
        content=json.dumps({
            "name": "SCB MCP Server",
            "version": "1.0.0",
            "protocol": "MCP over SSE",
            "sse_endpoint": "/sse"
        }),
        media_type="application/json"
    )


# Create Starlette app
app = Starlette(
    debug=True,
    routes=[
        Route("/", root),
        Route("/health", health),
        Route("/sse", handle_sse),
        Route("/messages", handle_messages, methods=["POST"]),
    ],
)


if __name__ == "__main__":
    logger.info("Starting SCB MCP SSE Server on http://0.0.0.0:8000")
    logger.info("SSE endpoint: http://0.0.0.0:8000/sse")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
