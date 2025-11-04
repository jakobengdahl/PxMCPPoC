# SCB MCP Server - Snabbstart / Quick Start

## Snabbinstallation / Quick Installation

### Steg 1: Installera beroenden / Install Dependencies

```bash
pip install -r requirements.txt
```

### Steg 2: Välj körläge / Choose Run Mode

#### A) Lokal användning med Claude Desktop (stdio)

1. **Kör servern:**
```bash
python scb_mcp_server.py
```

2. **Konfigurera Claude Desktop:**

Redigera din config-fil:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

Lägg till:
```json
{
  "mcpServers": {
    "scb-statistics": {
      "command": "python",
      "args": ["/full/path/to/PxMCPPoC/scb_mcp_server.py"]
    }
  }
}
```

3. **Starta om Claude Desktop**

#### B) Fjärråtkomst via HTTP/SSE

1. **Starta HTTP-servern:**
```bash
python scb_mcp_server_http.py
```

Servern startar på `http://localhost:8000`

2. **Testa servern:**
```bash
curl http://localhost:8000/health
```

Förväntat svar:
```json
{"status":"healthy","service":"scb-mcp-server"}
```

3. **Konfigurera din MCP-klient:**
```json
{
  "mcpServers": {
    "scb-statistics": {
      "url": "http://localhost:8000/sse",
      "transport": "sse"
    }
  }
}
```

## Snabbstart med Docker / Quick Start with Docker

```bash
# Starta servern
docker-compose up -d

# Kontrollera att den körs
curl http://localhost:8000/health

# Visa loggar
docker-compose logs -f

# Stoppa servern
docker-compose down
```

## Exempel: Använda verktygen / Example: Using the Tools

### 1. Bläddra i SCB:s metadata

```json
{
  "tool": "scb_browse_metadata",
  "arguments": {
    "path": "",
    "language": "sv"
  }
}
```

**Resultat:** Lista över huvudkategorier (Befolkning, Arbetsmarknad, etc.)

### 2. Sök efter befolkningsdata

```json
{
  "tool": "scb_search_tables",
  "arguments": {
    "query": "befolkning",
    "language": "sv"
  }
}
```

**Resultat:** Matchande tabeller med population-statistik

### 3. Hämta tabell-metadata

```json
{
  "tool": "scb_get_table_metadata",
  "arguments": {
    "table_id": "BE0101N1",
    "language": "sv"
  }
}
```

**Resultat:** Tillgängliga variabler, dimensioner och tidsperioder

### 4. Hämta faktisk data

```json
{
  "tool": "scb_fetch_data",
  "arguments": {
    "table_id": "BE0101N1",
    "query": {
      "Region": ["*"],
      "Tid": ["2023"]
    },
    "language": "sv"
  }
}
```

**Resultat:** Befolkningsdata för alla regioner år 2023

## Testning / Testing

Kör testerna för att verifiera installationen:

```bash
python test_scb_client.py
```

**Observera:** Om du är i en miljö utan tillgång till SCB API (t.ex. bakom strikt brandvägg), kommer testen att visa fel. Detta betyder inte att koden är felaktig - den behöver bara köras i en miljö med internetåtkomst till `api.scb.se`.

## Vanliga användningsfall / Common Use Cases

### Use Case 1: Befolkningsstatistik

**Fråga till AI-assistenten:**
> "Kan du hämta befolkningsdata för Stockholm från SCB?"

**AI-assistenten använder:**
1. `scb_search_tables` → Hittar BE0101N1
2. `scb_get_table_metadata` → Ser tillgängliga regioner
3. `scb_fetch_data` → Hämtar data för Stockholm

### Use Case 2: Arbetslöshetsstatistik

**Fråga:**
> "Visa arbetslöshet i Sverige senaste 5 åren"

**AI-assistenten använder:**
1. `scb_search_tables` med query="arbetslöshet"
2. `scb_get_table_metadata` → Hittar tillgängliga år
3. `scb_fetch_data` → Hämtar data för 2019-2024

### Use Case 3: Utforska datakategorier

**Fråga:**
> "Vilka typer av ekonomistatistik finns tillgänglig från SCB?"

**AI-assistenten använder:**
1. `scb_browse_metadata` → Visar huvudkategorier
2. `scb_browse_metadata` path="OE" → Utforskar offentlig ekonomi
3. `scb_browse_metadata` path="HA" → Utforskar hushållens ekonomi

## Felsökning / Troubleshooting

### Problem: "Connection refused"

**Lösning:**
```bash
# Kontrollera att servern körs
ps aux | grep scb_mcp_server

# Eller för HTTP-version
curl http://localhost:8000/health
```

### Problem: "Module not found"

**Lösning:**
```bash
# Installera om beroenden
pip install -r requirements.txt

# Eller med virtual environment
python -m venv venv
source venv/bin/activate  # På Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Problem: "SSL Certificate Error" eller "403 Forbidden"

**Orsak:** Nätverksmiljön blockerar åtkomst till SCB API

**Lösningar:**
1. Kontrollera brandväggsinställningar
2. Tillåt utgående trafik till `api.scb.se` på port 443
3. Kontakta din IT-avdelning för att vitlista SCB API:et
4. Testa från ett annat nätverk

### Problem: Claude Desktop ser inte servern

**Lösning:**
1. Kontrollera att sökvägen i config-filen är absolut (inte relativ)
2. Testa att köra kommandot manuellt:
   ```bash
   python /full/path/to/scb_mcp_server.py
   ```
3. Kontrollera att det inte finns syntaxfel i JSON-konfigurationen
4. Starta om Claude Desktop

## Nästa steg / Next Steps

1. **Läs fullständig dokumentation:** Se `README.md`
2. **Deployment i produktion:** Se `DEPLOYMENT_GUIDE.md`
3. **Anpassa servern:** Redigera `scb_mcp_server.py` eller `scb_mcp_server_http.py`
4. **Lägg till fler verktyg:** Utöka med fler SCB-funktioner

## Support

- **GitHub Issues**: Rapportera problem
- **Dokumentation**: Se README.md och DEPLOYMENT_GUIDE.md
- **SCB API Docs**: https://www.scb.se/api

---

**Lycka till med din SCB-dataintegration! / Good luck with your SCB data integration!** 🚀
