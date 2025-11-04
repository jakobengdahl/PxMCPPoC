# Snabbfix för OpenAI Agent Builder

## Problem

Du får "Unable to load tools for this server" och /sse returnerar "Not Found".

## Lösning: Använd HTTP API istället

OpenAI Agent Builder har för närvarande problem med MCP SSE-protokollet. Använd istället den enkla HTTP API:n.

### Steg 1: Starta rätt server

```bash
# ANVÄND DENNA:
python scb_mcp_server_http.py

# INTE SSE-versionen (den fungerar inte med OpenAI ännu)
```

### Steg 2: Konfigurera OpenAI med OpenAPI Schema

I OpenAI Agent Builder, lägg till Actions med denna OpenAPI-specifikation:

```yaml
openapi: 3.1.0
info:
  title: SCB Statistics API
  description: Access Statistics Sweden open data
  version: 1.0.0
servers:
  - url: https://user-jakobengdahl-804804-user.user.lab.sspcloud.fr
paths:
  /tools:
    get:
      operationId: listTools
      summary: List available SCB tools
      responses:
        '200':
          description: List of tools
          content:
            application/json:
              schema:
                type: object
                properties:
                  tools:
                    type: array
                    items:
                      type: object

  /call_tool:
    post:
      operationId: browseSCBMetadata
      summary: Browse SCB metadata tree
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                  const: scb_browse_metadata
                arguments:
                  type: object
                  properties:
                    path:
                      type: string
                      description: Path in tree (empty for root)
                    language:
                      type: string
                      enum: [sv, en]
              required: [name, arguments]
      responses:
        '200':
          description: Metadata result
          content:
            application/json:
              schema:
                type: object

  /call_tool_search:
    post:
      operationId: searchSCBTables
      summary: Search for SCB statistical tables
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                  const: scb_search_tables
                arguments:
                  type: object
                  properties:
                    query:
                      type: string
                      description: Search query
                    language:
                      type: string
                      enum: [sv, en]
                  required: [query]
              required: [name, arguments]
      responses:
        '200':
          description: Search results

  /call_tool_metadata:
    post:
      operationId: getSCBTableMetadata
      summary: Get metadata for a specific table
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                  const: scb_get_table_metadata
                arguments:
                  type: object
                  properties:
                    table_id:
                      type: string
                      description: SCB table ID
                    language:
                      type: string
                      enum: [sv, en]
                  required: [table_id]
              required: [name, arguments]
      responses:
        '200':
          description: Table metadata

  /call_tool_data:
    post:
      operationId: fetchSCBData
      summary: Fetch statistical data from SCB
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                  const: scb_fetch_data
                arguments:
                  type: object
                  properties:
                    table_id:
                      type: string
                    query:
                      type: object
                    language:
                      type: string
                      enum: [sv, en]
                  required: [table_id, query]
              required: [name, arguments]
      responses:
        '200':
          description: Statistical data
```

### Steg 3: Förenkla med Custom Actions

Eller skapa separata actions för varje operation:

#### Action 1: Browse Metadata

**URL:** `POST https://your-domain.com/call_tool`

**Body:**
```json
{
  "name": "scb_browse_metadata",
  "arguments": {
    "path": "{path}",
    "language": "sv"
  }
}
```

#### Action 2: Search Tables

**URL:** `POST https://your-domain.com/call_tool`

**Body:**
```json
{
  "name": "scb_search_tables",
  "arguments": {
    "query": "{query}",
    "language": "sv"
  }
}
```

#### Action 3: Get Metadata

**URL:** `POST https://your-domain.com/call_tool`

**Body:**
```json
{
  "name": "scb_get_table_metadata",
  "arguments": {
    "table_id": "{table_id}",
    "language": "sv"
  }
}
```

#### Action 4: Fetch Data

**URL:** `POST https://your-domain.com/call_tool`

**Body:**
```json
{
  "name": "scb_fetch_data",
  "arguments": {
    "table_id": "{table_id}",
    "query": {query_object},
    "language": "sv"
  }
}
```

### Steg 4: Testa manuellt först

Innan du konfigurerar OpenAI, testa att servern fungerar:

```bash
# Test 1: Health check
curl https://your-domain.com/health

# Test 2: List tools
curl https://your-domain.com/tools

# Test 3: Call a tool
curl -X POST https://your-domain.com/call_tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "scb_browse_metadata",
    "arguments": {
      "path": "",
      "language": "sv"
    }
  }'
```

### Komplett OpenAPI Schema (kopiera denna)

Spara denna som `openapi.yaml` och importera i OpenAI:

```yaml
openapi: 3.1.0
info:
  title: SCB Statistics Sweden API
  description: Access open statistical data from Statistics Sweden (Statistiska centralbyrån)
  version: 1.0.0
servers:
  - url: https://user-jakobengdahl-804804-user.user.lab.sspcloud.fr
    description: SCB MCP Server

paths:
  /call_tool:
    post:
      summary: Call an SCB tool
      operationId: callSCBTool
      description: Execute one of the available SCB tools
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - name
                - arguments
              properties:
                name:
                  type: string
                  description: Name of the tool to call
                  enum:
                    - scb_browse_metadata
                    - scb_search_tables
                    - scb_get_table_metadata
                    - scb_fetch_data
                    - scb_get_table_info
                arguments:
                  type: object
                  description: Arguments for the tool
            examples:
              browse:
                summary: Browse metadata
                value:
                  name: scb_browse_metadata
                  arguments:
                    path: ""
                    language: "sv"
              search:
                summary: Search tables
                value:
                  name: scb_search_tables
                  arguments:
                    query: "befolkning"
                    language: "sv"
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  success:
                    type: boolean
                  result:
                    type: object
        '400':
          description: Bad request
        '404':
          description: Tool not found
        '500':
          description: Server error
```

### Alternativ: Använd GPT Actions Format

För Custom GPT, använd denna kortare version:

```json
{
  "schema": {
    "name": "scb_search",
    "description": "Search for statistical tables in SCB database",
    "parameters": {
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "Search query in Swedish or English"
        }
      },
      "required": ["query"]
    }
  },
  "api": {
    "type": "http",
    "url": "https://your-domain.com/call_tool",
    "method": "POST",
    "body": {
      "name": "scb_search_tables",
      "arguments": {
        "query": "{{query}}",
        "language": "sv"
      }
    }
  }
}
```

## Felsökning

### "Unable to connect"

- Kontrollera att servern körs: `curl https://your-domain.com/health`
- Verifiera HTTPS (OpenAI kräver det)
- Kontrollera CORS om det behövs

### "Invalid response"

- Testa anropet manuellt med curl först
- Kontrollera att JSON-formatet är korrekt
- Kolla serverloggar för fel

### SCB API fel

Om du får fel från SCB API (t.ex. "Expecting value"):
- Detta är nätverksproblem till api.scb.se
- Servern fungerar, men kan inte nå SCB
- Kontrollera brandvägg/utgående anslutningar

## Sammanfattning

1. ✅ Använd `scb_mcp_server_http.py` (INTE sse-versionen)
2. ✅ Skapa Actions i OpenAI med OpenAPI-schemat ovan
3. ✅ Testa manuellt med curl först
4. ✅ Använd HTTPS-URL (inte HTTP)
5. ✅ Börja med en enkel action, lägg till fler efteråt

---

Behöver du mer hjälp? Öppna ett issue på GitHub!
