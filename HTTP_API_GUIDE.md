# SCB MCP HTTP Server - API Guide

Denna guide beskriver hur du använder SCB MCP Server via HTTP-endpoints.

## Översikt / Overview

HTTP-servern exponerar SCB-verktygen via enkla REST-liknande endpoints med JSON-data.

**Bas-URL:** `http://localhost:8000` (eller din server-URL)

## Endpoints

### 1. Server Information
**Endpoint:** `GET /`

Hämtar information om servern och tillgängliga endpoints.

**Exempel:**
```bash
curl http://localhost:8000/
```

**Respons:**
```json
{
  "name": "SCB MCP Server",
  "version": "1.0.0",
  "description": "Model Context Protocol server for Statistics Sweden (SCB) data access",
  "protocol": "HTTP JSON-RPC style",
  "endpoints": {
    "tools": "/tools",
    "call_tool": "/call_tool",
    "health": "/health"
  }
}
```

### 2. Health Check
**Endpoint:** `GET /health`

Kontrollera om servern är igång.

**Exempel:**
```bash
curl http://localhost:8000/health
```

**Respons:**
```json
{
  "status": "healthy",
  "service": "scb-mcp-server"
}
```

### 3. List Tools
**Endpoint:** `GET /tools`

Lista alla tillgängliga SCB-verktyg.

**Exempel:**
```bash
curl http://localhost:8000/tools
```

**Respons:**
```json
{
  "tools": [
    {
      "name": "scb_browse_metadata",
      "description": "Browse SCB metadata tree...",
      "inputSchema": {...}
    },
    ...
  ]
}
```

### 4. Call Tool
**Endpoint:** `POST /call_tool`

Anropa ett verktyg med argument.

**Request Body:**
```json
{
  "name": "tool_name",
  "arguments": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    // Tool-specific result
  }
}
```

## Verktygsanvändning / Tool Usage

### Tool 1: scb_browse_metadata

Bläddra i SCB:s metadataträd.

**Request:**
```bash
curl -X POST http://localhost:8000/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "scb_browse_metadata",
    "arguments": {
      "path": "",
      "language": "sv"
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "result": {
    "path": "root",
    "language": "sv",
    "items": [
      {
        "id": "BE",
        "text": "Befolkning",
        "type": "l"
      },
      ...
    ]
  }
}
```

### Tool 2: scb_search_tables

Sök efter tabeller.

**Request:**
```bash
curl -X POST http://localhost:8000/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "scb_search_tables",
    "arguments": {
      "query": "befolkning",
      "language": "sv"
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "result": {
    "query": "befolkning",
    "language": "sv",
    "matches": [
      {
        "id": "BE",
        "text": "Befolkning",
        "type": "l"
      }
    ]
  }
}
```

### Tool 3: scb_get_table_metadata

Hämta metadata för en tabell.

**Request:**
```bash
curl -X POST http://localhost:8000/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "scb_get_table_metadata",
    "arguments": {
      "table_id": "BE0101N1",
      "language": "sv"
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "result": {
    "table_id": "BE0101N1",
    "language": "sv",
    "variables": {
      "Region": {
        "code": "Region",
        "text": "Region",
        "values": ["00", "01", ...],
        "valueTexts": ["Riket", "Stockholm", ...]
      },
      ...
    }
  }
}
```

### Tool 4: scb_fetch_data

Hämta faktisk data från en tabell.

**Request:**
```bash
curl -X POST http://localhost:8000/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "scb_fetch_data",
    "arguments": {
      "table_id": "BE0101N1",
      "query": {
        "Region": ["*"],
        "Tid": ["2023"]
      },
      "language": "sv"
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "result": {
    "table_id": "BE0101N1",
    "language": "sv",
    "query": {...},
    "data": {
      "columns": [...],
      "data": [...]
    }
  }
}
```

### Tool 5: scb_get_table_info

Hämta allmän information om en tabell.

**Request:**
```bash
curl -X POST http://localhost:8000/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "scb_get_table_info",
    "arguments": {
      "table_id": "BE0101N1",
      "language": "sv"
    }
  }'
```

**Response:**
```json
{
  "success": true,
  "result": {
    "table_id": "BE0101N1",
    "language": "sv",
    "url": "https://api.scb.se/...",
    "info": "Table found and accessible"
  }
}
```

## Python Client Exempel

```python
import requests
import json

BASE_URL = "http://localhost:8000"

# Lista alla verktyg
response = requests.get(f"{BASE_URL}/tools")
tools = response.json()['tools']
print(f"Available tools: {[t['name'] for t in tools]}")

# Bläddra i metadata
response = requests.post(
    f"{BASE_URL}/call_tool",
    json={
        "name": "scb_browse_metadata",
        "arguments": {
            "path": "",
            "language": "sv"
        }
    }
)
result = response.json()
if result['success']:
    print(f"Found {len(result['result']['items'])} categories")

# Sök efter tabeller
response = requests.post(
    f"{BASE_URL}/call_tool",
    json={
        "name": "scb_search_tables",
        "arguments": {
            "query": "befolkning",
            "language": "sv"
        }
    }
)
result = response.json()
if result['success']:
    print(f"Found {len(result['result']['matches'])} matches")
```

## JavaScript/Node.js Client Exempel

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000';

// Lista alla verktyg
async function listTools() {
  const response = await axios.get(`${BASE_URL}/tools`);
  return response.data.tools;
}

// Anropa ett verktyg
async function callTool(name, arguments) {
  const response = await axios.post(`${BASE_URL}/call_tool`, {
    name: name,
    arguments: arguments
  });
  return response.data;
}

// Exempel: Bläddra i metadata
const result = await callTool('scb_browse_metadata', {
  path: '',
  language: 'sv'
});

console.log(result);
```

## Integration med AI-assistenter

### OpenAI GPT med Functions

```python
import openai

tools = [
    {
        "type": "function",
        "function": {
            "name": "scb_browse_metadata",
            "description": "Browse SCB metadata tree",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path in tree"},
                    "language": {"type": "string", "enum": ["sv", "en"]}
                },
                "required": []
            }
        }
    }
    # ... fler verktyg
]

def call_scb_tool(name, arguments):
    response = requests.post(
        "http://localhost:8000/call_tool",
        json={"name": name, "arguments": arguments}
    )
    return response.json()['result']

# Använd med OpenAI
response = openai.chat.completions.create(
    model="gpt-4",
    messages=[{"role": "user", "content": "Visa befolkningsdata för Stockholm"}],
    tools=tools,
    tool_choice="auto"
)

# Hantera function calls
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        result = call_scb_tool(
            tool_call.function.name,
            json.loads(tool_call.function.arguments)
        )
```

## Felhantering / Error Handling

### Success Response
```json
{
  "success": true,
  "result": {...}
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message here"
}
```

### HTTP Status Codes
- `200` - Success
- `400` - Bad Request (missing parameters)
- `404` - Tool Not Found
- `500` - Internal Server Error

## Testning / Testing

Använd det medföljande testskriptet:

```bash
python test_http_server.py
```

Eller testa manuellt med curl:

```bash
# Health check
curl http://localhost:8000/health

# Lista verktyg
curl http://localhost:8000/tools

# Anropa verktyg
curl -X POST http://localhost:8000/call_tool \
  -H "Content-Type: application/json" \
  -d '{"name":"scb_browse_metadata","arguments":{"path":"","language":"sv"}}'
```

## CORS (Cross-Origin Resource Sharing)

Om du behöver anropa API:et från en webbläsare, lägg till CORS-stöd i `scb_mcp_server_http.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Eller specifika domäner
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Rate Limiting och Säkerhet

För produktion, överväg att lägga till:

1. **Rate Limiting:**
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)

@api.post("/call_tool")
@limiter.limit("10/minute")
async def call_tool(...):
    ...
```

2. **API Key Authentication:**
```python
from fastapi import Header, HTTPException

async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != "your-secret-key":
        raise HTTPException(status_code=403, detail="Invalid API key")
```

3. **HTTPS:** Använd alltid HTTPS i produktion.

---

För mer information, se `README.md` och `DEPLOYMENT_GUIDE.md`.
