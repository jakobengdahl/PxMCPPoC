#!/usr/bin/env python3
"""
SCB MCP Server - A Model Context Protocol server for Statistics Sweden (SCB) data access
Uses pyscbwrapper to interact with SCB's open data API
"""

import json
import logging
from typing import Any, Optional
from pyscbwrapper import SCB
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scb-mcp-server")

# Initialize the MCP server
app = Server("scb-statistics")

# Initialize SCB clients for both languages
scb_sv = SCB("sv")  # Swedish
scb_en = SCB("en")  # English


def get_scb_client(lang: str = "sv") -> SCB:
    """Get SCB client for specified language"""
    return scb_en if lang.lower() == "en" else scb_sv


@app.list_tools()
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
                        "description": "Search query (e.g., 'befolkning', 'population', 'arbetslöshet', 'unemployment')",
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
                "dimensions, time periods, and value codes. This is essential before fetching data."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": "string",
                        "description": "SCB table ID (e.g., 'TAB638', 'BE0101N1')",
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
                "Requires table_id and query specification with variables and their values. "
                "Returns data in structured JSON format."
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
                        "description": (
                            "Query specification with variables and selected values. "
                            "Example: {'Region': ['*'], 'Tid': ['2023', '2024']}"
                        ),
                    },
                    "language": {
                        "type": "string",
                        "description": "Language for results: 'sv' (Swedish) or 'en' (English)",
                        "enum": ["sv", "en"],
                        "default": "sv",
                    },
                },
                "required": ["table_id", "query"],
            },
        ),
        Tool(
            name="scb_get_table_info",
            description=(
                "Get comprehensive information about a specific table including its location path, "
                "full URL, and basic metadata. Useful for understanding table context."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "table_id": {
                        "type": "string",
                        "description": "SCB table ID",
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
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    try:
        if name == "scb_browse_metadata":
            result = await browse_metadata(
                path=arguments.get("path", ""),
                language=arguments.get("language", "sv")
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]

        elif name == "scb_search_tables":
            result = await search_tables(
                query=arguments["query"],
                language=arguments.get("language", "sv")
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]

        elif name == "scb_get_table_metadata":
            result = await get_table_metadata(
                table_id=arguments["table_id"],
                language=arguments.get("language", "sv")
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]

        elif name == "scb_fetch_data":
            result = await fetch_data(
                table_id=arguments["table_id"],
                query=arguments["query"],
                language=arguments.get("language", "sv")
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]

        elif name == "scb_get_table_info":
            result = await get_table_info(
                table_id=arguments["table_id"],
                language=arguments.get("language", "sv")
            )
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]

        else:
            raise ValueError(f"Unknown tool: {name}")

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


async def browse_metadata(path: str = "", language: str = "sv") -> dict:
    """Browse SCB metadata tree"""
    scb = get_scb_client(language)

    try:
        if path:
            # Navigate to specific path
            result = scb.go_down(path)
        else:
            # Get root level
            result = scb.info()

        # Extract useful information
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
        # This is a simple implementation - pyscbwrapper might have better search capabilities
        # For now, we'll browse and filter
        root = scb.info()
        results = {
            "query": query,
            "language": language,
            "matches": []
        }

        # Simple text search in root level
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
        # Set the table and get variables
        scb.set_table(table_id)
        variables = scb.get_variables()

        metadata = {
            "table_id": table_id,
            "language": language,
            "variables": variables
        }

        return metadata

    except Exception as e:
        return {"error": str(e), "table_id": table_id, "language": language}


async def fetch_data(table_id: str, query: dict, language: str = "sv") -> dict:
    """Fetch data from a table"""
    scb = get_scb_client(language)

    try:
        # Set the table
        scb.set_table(table_id)

        # Build query
        scb_query = scb.get_query()

        # Apply query filters
        for var_name, values in query.items():
            if "*" in values:
                # Select all values for this variable
                scb_query[var_name] = scb_query[var_name]["values"]
            else:
                # Select specific values
                scb_query[var_name] = values

        # Fetch data
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


async def main():
    """Run the MCP server using stdio transport"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
