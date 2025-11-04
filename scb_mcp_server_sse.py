#!/usr/bin/env python3
"""
SCB MCP Server (SSE) - Simple HTTP endpoints that work with OpenAI
This version provides both standard HTTP endpoints AND basic SSE support
"""

import json
import logging
from typing import Any
from pyscbwrapper import SCB
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scb-mcp-sse-server")

# Initialize FastAPI
api = FastAPI(title="SCB MCP Server", version="1.0.0")

# Initialize SCB clients
scb_sv = SCB("sv")
scb_en = SCB("en")


def get_scb_client(lang: str = "sv") -> SCB:
    """Get SCB client for specified language"""
    return scb_en if lang.lower() == "en" else scb_sv


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


# FastAPI endpoints
@api.get("/")
async def root():
    """Root endpoint with server info"""
    return {
        "name": "SCB MCP Server",
        "version": "1.0.0",
        "protocol": "HTTP JSON-RPC + SSE",
        "endpoints": {
            "tools": "/tools",
            "call_tool": "/call_tool",
            "health": "/health",
            "sse": "/sse (basic support)"
        }
    }


@api.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "scb-mcp-sse-server"}


@api.get("/tools")
async def list_tools():
    """List available SCB data tools"""
    return {
        "tools": [
            {
                "name": "scb_browse_metadata",
                "description": (
                    "Browse SCB metadata tree to discover available statistical tables. "
                    "Supports Swedish (sv) and English (en)."
                ),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path in metadata tree",
                            "default": "",
                        },
                        "language": {
                            "type": "string",
                            "enum": ["sv", "en"],
                            "default": "sv",
                        },
                    },
                },
            },
            {
                "name": "scb_search_tables",
                "description": "Search for statistical tables in SCB database using keywords.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query",
                        },
                        "language": {
                            "type": "string",
                            "enum": ["sv", "en"],
                            "default": "sv",
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "scb_get_table_metadata",
                "description": "Get detailed metadata for a specific SCB table.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "table_id": {
                            "type": "string",
                            "description": "SCB table ID (e.g., 'BE0101N1')",
                        },
                        "language": {
                            "type": "string",
                            "enum": ["sv", "en"],
                            "default": "sv",
                        },
                    },
                    "required": ["table_id"],
                },
            },
            {
                "name": "scb_fetch_data",
                "description": "Fetch actual statistical data from an SCB table.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "table_id": {
                            "type": "string",
                            "description": "SCB table ID",
                        },
                        "query": {
                            "type": "object",
                            "description": "Query specification",
                        },
                        "language": {
                            "type": "string",
                            "enum": ["sv", "en"],
                            "default": "sv",
                        },
                    },
                    "required": ["table_id", "query"],
                },
            },
            {
                "name": "scb_get_table_info",
                "description": "Get comprehensive information about a specific table.",
                "inputSchema": {
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
            },
        ]
    }


@api.post("/call_tool")
async def call_tool(request: Request):
    """Call a tool with the given arguments"""
    try:
        body = await request.json()
        name = body.get("name")
        arguments = body.get("arguments", {})

        if not name:
            return JSONResponse(
                status_code=400,
                content={"error": "Missing 'name' field in request"}
            )

        logger.info(f"Tool called: {name} with args: {arguments}")

        # Route to the appropriate tool
        if name == "scb_browse_metadata":
            result = await browse_metadata(
                path=arguments.get("path", ""),
                language=arguments.get("language", "sv")
            )
        elif name == "scb_search_tables":
            if "query" not in arguments:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Missing required argument 'query'"}
                )
            result = await search_tables(
                query=arguments["query"],
                language=arguments.get("language", "sv")
            )
        elif name == "scb_get_table_metadata":
            if "table_id" not in arguments:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Missing required argument 'table_id'"}
                )
            result = await get_table_metadata(
                table_id=arguments["table_id"],
                language=arguments.get("language", "sv")
            )
        elif name == "scb_fetch_data":
            if "table_id" not in arguments or "query" not in arguments:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Missing required arguments"}
                )
            result = await fetch_data(
                table_id=arguments["table_id"],
                query=arguments["query"],
                language=arguments.get("language", "sv")
            )
        elif name == "scb_get_table_info":
            if "table_id" not in arguments:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Missing required argument 'table_id'"}
                )
            result = await get_table_info(
                table_id=arguments["table_id"],
                language=arguments.get("language", "sv")
            )
        else:
            return JSONResponse(
                status_code=404,
                content={"error": f"Unknown tool: {name}"}
            )

        return JSONResponse(content={
            "success": True,
            "result": result
        })

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


@api.get("/sse")
async def handle_sse(request: Request):
    """Basic SSE endpoint - sends tool list on connection"""
    logger.info("SSE connection established from OpenAI")

    async def event_generator():
        """Generate SSE events"""
        try:
            # Send initial connection message
            yield f"event: connected\n"
            yield f"data: {json.dumps({'status': 'connected', 'server': 'SCB MCP Server'})}\n\n"

            # Send tools list
            tools = await list_tools()
            yield f"event: tools\n"
            yield f"data: {json.dumps(tools)}\n\n"

            # Keep connection alive
            while True:
                await asyncio.sleep(30)
                yield f"event: ping\n"
                yield f"data: {json.dumps({'status': 'alive'})}\n\n"

        except asyncio.CancelledError:
            logger.info("SSE connection closed")
        except Exception as e:
            logger.error(f"SSE error: {e}", exc_info=True)
            yield f"event: error\n"
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting SCB MCP Server on http://0.0.0.0:8000")
    logger.info("Available endpoints:")
    logger.info("  - GET  /         - Server info")
    logger.info("  - GET  /health   - Health check")
    logger.info("  - GET  /tools    - List available tools")
    logger.info("  - POST /call_tool - Call a tool")
    logger.info("  - GET  /sse      - SSE endpoint (basic)")

    uvicorn.run(
        api,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
