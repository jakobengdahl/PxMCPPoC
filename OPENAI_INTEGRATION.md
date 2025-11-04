# SCB MCP Server - OpenAI Integration Guide

Guide för att integrera SCB MCP Server med OpenAI:s Agent Builder och GPT Actions.

## Alternativ 1: MCP SSE Server (Rekommenderad för OpenAI)

OpenAI:s agent builder stödjer MCP-protokollet via SSE (Server-Sent Events).

### Starta SSE-servern

```bash
# Installera dependencies
pip install -r requirements.txt

# Starta SSE-servern
python scb_mcp_server_sse.py
```

Servern startar på `http://0.0.0.0:8000` med SSE-endpoint på `/sse`.

### Konfigurera i OpenAI Agent Builder

1. **Gå till OpenAI Agent Builder** (platform.openai.com)

2. **Lägg till Action**:
   - Type: "MCP Server"
   - URL: `https://your-domain.com/sse` (din publika URL)

3. **Verifiera**:
   - OpenAI kommer testa `/sse` endpointen
   - Om det fungerar ser du listan med 5 verktyg

### Exponera lokalt till OpenAI (för utveckling)

Om du kör lokalt, använd en tunnel-tjänst:

**Med ngrok:**
```bash
# Starta servern lokalt
python scb_mcp_server_sse.py

# I annat terminal, starta ngrok
ngrok http 8000

# Använd ngrok-URL:en i OpenAI
# https://abc123.ngrok.io/sse
```

**Med Cloudflare Tunnel:**
```bash
cloudflared tunnel --url http://localhost:8000
```

## Alternativ 2: Custom GPT Actions (HTTP API)

Om MCP SSE inte fungerar, använd den vanliga HTTP API:n.

### Starta HTTP-servern

```bash
python scb_mcp_server_http.py
```

### OpenAI Action Schema

Skapa en Custom GPT eller använd Actions i Assistant API med följande schema:

```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "SCB Statistics API",
    "description": "Access Statistics Sweden (SCB) open data",
    "version": "1.0.0"
  },
  "servers": [
    {
      "url": "https://your-domain.com"
    }
  ],
  "paths": {
    "/call_tool": {
      "post": {
        "operationId": "callSCBTool",
        "summary": "Call an SCB tool",
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/ToolCall"
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Tool result",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ToolResult"
                }
              }
            }
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "ToolCall": {
        "type": "object",
        "required": ["name", "arguments"],
        "properties": {
          "name": {
            "type": "string",
            "enum": [
              "scb_browse_metadata",
              "scb_search_tables",
              "scb_get_table_metadata",
              "scb_fetch_data",
              "scb_get_table_info"
            ]
          },
          "arguments": {
            "type": "object"
          }
        }
      },
      "ToolResult": {
        "type": "object",
        "properties": {
          "success": {
            "type": "boolean"
          },
          "result": {
            "type": "object"
          }
        }
      }
    }
  }
}
```

### Skapa funktioner för varje verktyg

Alternativt, definiera separata funktioner:

**1. Browse Metadata:**
```json
{
  "name": "scb_browse_metadata",
  "description": "Browse SCB metadata tree to find available tables",
  "parameters": {
    "type": "object",
    "properties": {
      "path": {
        "type": "string",
        "description": "Path in metadata tree (empty for root)"
      },
      "language": {
        "type": "string",
        "enum": ["sv", "en"],
        "default": "sv"
      }
    }
  }
}
```

**2. Search Tables:**
```json
{
  "name": "scb_search_tables",
  "description": "Search for statistical tables",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "Search query (e.g., 'befolkning', 'population')"
      },
      "language": {
        "type": "string",
        "enum": ["sv", "en"],
        "default": "sv"
      }
    },
    "required": ["query"]
  }
}
```

**3. Get Table Metadata:**
```json
{
  "name": "scb_get_table_metadata",
  "description": "Get metadata for a specific table",
  "parameters": {
    "type": "object",
    "properties": {
      "table_id": {
        "type": "string",
        "description": "SCB table ID (e.g., 'BE0101N1')"
      },
      "language": {
        "type": "string",
        "enum": ["sv", "en"],
        "default": "sv"
      }
    },
    "required": ["table_id"]
  }
}
```

**4. Fetch Data:**
```json
{
  "name": "scb_fetch_data",
  "description": "Fetch statistical data from a table",
  "parameters": {
    "type": "object",
    "properties": {
      "table_id": {
        "type": "string",
        "description": "SCB table ID"
      },
      "query": {
        "type": "object",
        "description": "Query specification with variables and values"
      },
      "language": {
        "type": "string",
        "enum": ["sv", "en"],
        "default": "sv"
      }
    },
    "required": ["table_id", "query"]
  }
}
```

## Deployment för OpenAI

### Publicera servern

OpenAI behöver kunna nå din server via HTTPS. Alternativ:

**1. Cloud Hosting (Rekommenderat):**
- AWS, Azure, GCP
- Heroku, Railway, Render
- DigitalOcean App Platform

**2. Lokal + Tunnel (Utveckling):**
- ngrok
- Cloudflare Tunnel
- localtunnel

### Exempel: Deployment på Render.com

1. **Skapa `render.yaml`:**
```yaml
services:
  - type: web
    name: scb-mcp-server
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python scb_mcp_server_sse.py
    envVars:
      - key: PORT
        value: 8000
```

2. **Pusha till GitHub**

3. **Anslut Render till ditt repo**

4. **Använd Render URL i OpenAI**:
   - `https://scb-mcp-server.onrender.com/sse`

## Testa Integrationen

### Test 1: Verifiera SSE Endpoint

```bash
curl https://your-domain.com/sse
```

Du bör få ett SSE-svar.

### Test 2: Testa från OpenAI

När du konfigurerat actions i OpenAI, testa med:

> "Visa mig befolkningsstatistik för Sverige"

OpenAI kommer:
1. Anropa `scb_browse_metadata` eller `scb_search_tables`
2. Hitta relevanta tabeller
3. Använda `scb_get_table_metadata` för att se tillgängliga data
4. Anropa `scb_fetch_data` för att hämta datan
5. Presentera resultatet för dig

## Felsökning

### "Unable to load tools for this server"

**Möjliga orsaker:**
1. SSE-endpoint är inte tillgänglig
2. CORS-problem
3. SSL/HTTPS krävs (inte HTTP)
4. Brandvägg blockerar

**Lösningar:**
```bash
# 1. Verifiera att servern körs
curl http://localhost:8000/health

# 2. Testa SSE endpoint lokalt
curl http://localhost:8000/sse

# 3. Kontrollera HTTPS om deploy:ad
curl https://your-domain.com/sse

# 4. Kolla loggar
python scb_mcp_server_sse.py
# Se efter fel när OpenAI ansluter
```

### "Not Found" på /sse

Detta betyder att SSE-endpointen inte finns. Kontrollera:

1. **Använd rätt server:**
   ```bash
   # FÖR OPENAI: Använd SSE-servern
   python scb_mcp_server_sse.py

   # INTE http-servern (den har inte /sse)
   # python scb_mcp_server_http.py
   ```

2. **Verifiera endpoint:**
   ```bash
   curl http://localhost:8000/
   # Bör visa "sse_endpoint": "/sse"
   ```

### CORS-fel från OpenAI

Lägg till CORS i `scb_mcp_server_sse.py`:

```python
from starlette.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chat.openai.com", "https://platform.openai.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Exempel-konversation med OpenAI

**Du:** "Kan du hämta befolkningsdata för Stockholm från SCB?"

**OpenAI (tänker):**
1. Anropar `scb_search_tables` med query="befolkning"
2. Hittar tabell BE0101N1
3. Anropar `scb_get_table_metadata` för BE0101N1
4. Ser att Region och Tid finns som variabler
5. Anropar `scb_fetch_data` med:
   ```json
   {
     "table_id": "BE0101N1",
     "query": {
       "Region": ["01"],
       "Tid": ["2023"]
     }
   }
   ```

**OpenAI (svarar):** "Här är befolkningsdata för Stockholm 2023: ..."

## Tips

1. **Använd SSE-servern för OpenAI** - Den är MCP-kompatibel
2. **Kräv HTTPS** - OpenAI kräver säkra anslutningar
3. **Övervaka loggar** - Se vad OpenAI anropar
4. **Börja enkelt** - Testa lokalt med ngrok först
5. **Cache data** - Överväg att cacha SCB-svar för snabbare respons

## Ytterligare Resurser

- [MCP Specification](https://modelcontextprotocol.io)
- [OpenAI Actions Guide](https://platform.openai.com/docs/actions)
- [SCB API Documentation](https://www.scb.se/api)

---

För frågor eller problem, se `README.md` eller öppna ett GitHub issue.
