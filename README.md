# SCB MCP Server - Statistics Sweden Data Access

En Model Context Protocol (MCP) server för att komma åt SCB:s (Statistiska Centralbyråns) öppna data API. Servern gör det möjligt för AI-assistenter att söka, bläddra och hämta statistisk data från SCB på både svenska och engelska.

An MCP (Model Context Protocol) server for accessing Statistics Sweden's (SCB) open data API. The server enables AI assistants to search, browse, and fetch statistical data from SCB in both Swedish and English.

## 🌟 Funktioner / Features

- **Flerspråkig / Multilingual**: Stödjer både svenska (sv) och engelska (en)
- **Komplett datautforskning / Complete data exploration**: Bläddra i SCB:s metadataträd
- **Sök efter tabeller / Search for tables**: Hitta relevanta statistiska tabeller
- **Datahämtning / Data fetching**: Hämta faktisk statistisk data med flexibla queries
- **Två körlägen / Two run modes**:
  - **stdio**: För lokal användning med Claude Desktop
  - **HTTP/SSE**: För fjärråtkomst från externa AI-assistenter

## 📋 Förutsättningar / Prerequisites

- Python 3.11 eller högre / or higher
- pip (Python package installer)
- Docker och Docker Compose (valfritt för containerized deployment / optional for containerized deployment)

## 🚀 Installation

### Grundläggande installation / Basic Installation

1. **Klona projektet / Clone the repository**:
```bash
cd PxMCPPoC
```

2. **Installera beroenden / Install dependencies**:
```bash
pip install -r requirements.txt
```

### Docker Installation

```bash
# Bygg och starta servern / Build and start the server
docker-compose up -d

# Kontrollera status / Check status
docker-compose ps

# Visa loggar / View logs
docker-compose logs -f
```

## 🎯 Användning / Usage

### Körläge 1: stdio (Lokal användning med Claude Desktop)

Detta läge används för att integrera med Claude Desktop eller andra lokala MCP-klienter.

**Starta servern / Start the server**:
```bash
python scb_mcp_server.py
```

**Konfigurera Claude Desktop**:

Lägg till följande i din Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` på macOS):

```json
{
  "mcpServers": {
    "scb-statistics": {
      "command": "python",
      "args": [
        "-u",
        "/absolut/sökväg/till/PxMCPPoC/scb_mcp_server.py"
      ]
    }
  }
}
```

### Körläge 2: HTTP/SSE (Fjärråtkomst)

Detta läge exponerar servern på en port för extern åtkomst från AI-assistenter.

**Starta HTTP-servern / Start the HTTP server**:
```bash
python scb_mcp_server_http.py
```

Servern startar på `http://localhost:8000`

**Endpoints**:
- `GET /` - Serverinformation
- `GET /health` - Hälsokontroll
- `GET /sse` - SSE endpoint för MCP-kommunikation
- `POST /messages` - POST-baserad MCP-kommunikation

**Konfigurera MCP-klient för HTTP-åtkomst / Configure MCP client for HTTP access**:

```json
{
  "mcpServers": {
    "scb-statistics-http": {
      "url": "http://localhost:8000/sse",
      "transport": "sse"
    }
  }
}
```

## 🛠️ Tillgängliga verktyg / Available Tools

### 1. `scb_browse_metadata`

Bläddra i SCB:s metadataträd för att hitta tillgängliga tabeller.

**Parametrar / Parameters**:
- `path` (valfri): Sökväg i metadataträdet (t.ex. "AM/AM0401")
- `language` (valfri): "sv" eller "en" (standard: "sv")

**Exempel / Example**:
```json
{
  "path": "",
  "language": "sv"
}
```

### 2. `scb_search_tables`

Sök efter statistiska tabeller med nyckelord.

**Parametrar / Parameters**:
- `query` (krävs): Sökfråga (t.ex. "befolkning", "unemployment")
- `language` (valfri): "sv" eller "en"

**Exempel / Example**:
```json
{
  "query": "befolkning",
  "language": "sv"
}
```

### 3. `scb_get_table_metadata`

Hämta detaljerad metadata för en specifik tabell.

**Parametrar / Parameters**:
- `table_id` (krävs): SCB tabell-ID (t.ex. "BE0101N1")
- `language` (valfri): "sv" eller "en"

**Exempel / Example**:
```json
{
  "table_id": "BE0101N1",
  "language": "sv"
}
```

### 4. `scb_fetch_data`

Hämta faktisk statistisk data från en tabell.

**Parametrar / Parameters**:
- `table_id` (krävs): SCB tabell-ID
- `query` (krävs): Query-specifikation med variabler och värden
- `language` (valfri): "sv" eller "en"

**Exempel / Example**:
```json
{
  "table_id": "BE0101N1",
  "query": {
    "Region": ["*"],
    "Tid": ["2023", "2024"]
  },
  "language": "sv"
}
```

### 5. `scb_get_table_info`

Hämta allmän information om en tabell.

**Parametrar / Parameters**:
- `table_id` (krävs): SCB tabell-ID
- `language` (valfri): "sv" eller "en"

## 🧪 Testning / Testing

Kör testskriptet för att verifiera installation och funktionalitet:

```bash
python test_scb_client.py
```

Detta testar:
- Anslutning till SCB API (svenska och engelska)
- Metadata-bläddring
- Tabellåtkomst
- MCP-verktygsfunktioner

## 📚 Användningsexempel / Usage Examples

### Exempel 1: Hitta befolkningsdata

```python
# 1. Sök efter befolkningstabeller
scb_search_tables(query="befolkning", language="sv")

# 2. Hämta metadata för en tabell
scb_get_table_metadata(table_id="BE0101N1", language="sv")

# 3. Hämta data
scb_fetch_data(
    table_id="BE0101N1",
    query={"Region": ["*"], "Tid": ["2023"]},
    language="sv"
)
```

### Exempel 2: Utforska arbetslöshetsstatistik

```python
# 1. Bläddra i arbetsmarknadsdata
scb_browse_metadata(path="AM", language="sv")

# 2. Sök efter arbetslöshetstabeller
scb_search_tables(query="arbetslöshet", language="sv")
```

## 🔧 Konfiguration / Configuration

### Miljövariabler / Environment Variables

Skapa en `.env`-fil baserad på `.env.example`:

```bash
cp .env.example .env
```

Redigera `.env`:
```env
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
DEFAULT_LANGUAGE=sv
```

## 📖 SCB API Information

### API-dokumentation / API Documentation

- **SCB API**: https://www.scb.se/api
- **pyscbwrapper GitHub**: https://github.com/kirajcg/pyscbwrapper
- **SCB Statistikdatabas**: https://www.statistikdatabasen.scb.se

### Vanliga tabell-ID:n / Common Table IDs

- `BE0101N1` - Befolkning efter ålder och kön
- `TAB638` - Befolkning efter kön och ålder
- `AM0401N1` - Arbetslöshet

## 🐛 Felsökning / Troubleshooting

### Vanliga problem / Common Issues

**Problem: "ModuleNotFoundError: No module named 'mcp'"**
```bash
pip install --upgrade mcp
```

**Problem: "Connection refused" vid HTTP-åtkomst**
- Kontrollera att servern körs: `curl http://localhost:8000/health`
- Kontrollera brandväggsinställningar
- Verifiera att port 8000 är tillgänglig

**Problem: SCB API timeout**
- Kontrollera internetanslutning
- SCB API kan vara tillfälligt otillgängligt
- Testa direkt i webbläsare: https://api.scb.se/OV0104/v1/doris/sv/ssd/

## 🤝 Bidrag / Contributing

Bidrag är välkomna! Vänligen:

1. Forka projektet
2. Skapa en feature branch (`git checkout -b feature/amazing-feature`)
3. Committa dina ändringar (`git commit -m 'Add amazing feature'`)
4. Pusha till branchen (`git push origin feature/amazing-feature`)
5. Öppna en Pull Request

## 📄 Licens / License

Detta projekt är open source och tillgängligt under MIT-licensen.

## 🙏 Erkännanden / Acknowledgments

- **pyscbwrapper**: https://github.com/kirajcg/pyscbwrapper
- **SCB (Statistiska Centralbyrån)**: För det öppna data-API:et
- **Model Context Protocol**: https://modelcontextprotocol.io
- **Anthropic**: För Claude och MCP-specifikationen

## 📞 Support

För frågor eller problem:
- Skapa en issue på GitHub
- Kontakta projektmaintainers

---

**Utvecklad med ❤️ för öppen data och AI-integration**