# SCB MCP Server - Deployment Guide

## Nätverkskrav / Network Requirements

SCB MCP Server behöver tillgång till SCB:s öppna API för att fungera korrekt:

The SCB MCP Server needs access to the SCB open API to function correctly:

### Krävda endpoints / Required endpoints:
- `https://api.scb.se/OV0104/v1/doris/sv/ssd/` (Swedish API)
- `https://api.scb.se/OV0104/v1/doris/en/ssd/` (English API)

### Brandväggskonfiguration / Firewall Configuration

Om servern körs bakom en företagsbrandvägg eller i en begränsad miljö, säkerställ att följande är tillåtet:

If the server runs behind a corporate firewall or in a restricted environment, ensure the following is allowed:

```
Domain: api.scb.se
Port: 443 (HTTPS)
Protocol: HTTPS/TLS 1.2+
```

## Deployment-alternativ / Deployment Options

### 1. Lokal deployment (Utveckling / Development)

**För användning med Claude Desktop:**

```bash
# Installera beroenden
pip install -r requirements.txt

# Kör servern
python scb_mcp_server.py
```

**Konfigurera Claude Desktop** (`claude_desktop_config.json`):
```json
{
  "mcpServers": {
    "scb-statistics": {
      "command": "python",
      "args": ["/path/to/PxMCPPoC/scb_mcp_server.py"]
    }
  }
}
```

### 2. Docker Deployment

**Bygg och kör med Docker Compose:**

```bash
# Bygg imagen
docker-compose build

# Starta servern
docker-compose up -d

# Kontrollera status
docker-compose ps

# Visa loggar
docker-compose logs -f scb-mcp-server

# Stoppa servern
docker-compose down
```

**Testa att servern körs:**
```bash
curl http://localhost:8000/health
```

### 3. Cloud Deployment (AWS/Azure/GCP)

#### AWS (EC2/ECS)

**EC2 Deployment:**

1. Skapa en EC2-instans (t.ex. t3.micro)
2. Installera Docker
3. Klona projektet
4. Kör med Docker Compose

```bash
# På EC2-instansen
sudo yum update -y
sudo yum install -y docker git
sudo service docker start
sudo usermod -a -G docker ec2-user

# Klona och starta
git clone <your-repo>
cd PxMCPPoC
docker-compose up -d
```

**Security Group Configuration:**
- Inbound: Port 8000 (TCP) från dina AI-assistenters IP-adresser
- Outbound: Port 443 (HTTPS) till api.scb.se

#### Azure (Container Instances)

```bash
# Bygg imagen
docker build -t scb-mcp-server .

# Pusha till Azure Container Registry
az acr login --name <your-registry>
docker tag scb-mcp-server <your-registry>.azurecr.io/scb-mcp-server
docker push <your-registry>.azurecr.io/scb-mcp-server

# Skapa Container Instance
az container create \
  --resource-group <your-rg> \
  --name scb-mcp-server \
  --image <your-registry>.azurecr.io/scb-mcp-server \
  --ports 8000 \
  --dns-name-label scb-mcp-server
```

#### GCP (Cloud Run)

```bash
# Bygg och pusha
gcloud builds submit --tag gcr.io/<project-id>/scb-mcp-server

# Deploya
gcloud run deploy scb-mcp-server \
  --image gcr.io/<project-id>/scb-mcp-server \
  --platform managed \
  --region europe-north1 \
  --allow-unauthenticated
```

### 4. Kubernetes Deployment

**deployment.yaml:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: scb-mcp-server
spec:
  replicas: 2
  selector:
    matchLabels:
      app: scb-mcp-server
  template:
    metadata:
      labels:
        app: scb-mcp-server
    spec:
      containers:
      - name: scb-mcp-server
        image: scb-mcp-server:latest
        ports:
        - containerPort: 8000
        env:
        - name: LOG_LEVEL
          value: "INFO"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
---
apiVersion: v1
kind: Service
metadata:
  name: scb-mcp-server
spec:
  selector:
    app: scb-mcp-server
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

**Applya:**
```bash
kubectl apply -f deployment.yaml
```

## Säkerhetsöverväganden / Security Considerations

### 1. API-åtkomstkontroll / API Access Control

Om du exponerar servern för extern åtkomst, överväg att lägga till autentisering:

```python
# Exempel: Basic Auth med FastAPI
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets

security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = secrets.compare_digest(credentials.username, "your-username")
    correct_password = secrets.compare_digest(credentials.password, "your-password")
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials"
        )
    return credentials.username
```

### 2. Rate Limiting

Lägg till rate limiting för att skydda mot överanvändning:

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@api.get("/sse")
@limiter.limit("10/minute")
async def handle_sse(request: Request):
    # ... din kod här
```

### 3. HTTPS/TLS

I produktion, använd alltid HTTPS. Exempel med nginx som reverse proxy:

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Monitoring och Logging

### Prometheus Metrics

Lägg till metrics för monitoring:

```python
from prometheus_client import Counter, Histogram
import time

request_count = Counter('scb_mcp_requests_total', 'Total requests')
request_duration = Histogram('scb_mcp_request_duration_seconds', 'Request duration')

@api.middleware("http")
async def add_metrics(request: Request, call_next):
    request_count.inc()
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    request_duration.observe(duration)
    return response
```

### Structured Logging

```python
import structlog

logger = structlog.get_logger()

@app.call_tool()
async def call_tool(name: str, arguments: Any):
    logger.info("tool_called", tool=name, args=arguments)
    # ... din kod här
```

## Felsökning / Troubleshooting

### Problem: SCB API är inte tillgängligt

**Symptom:** SSL-fel eller timeout när servern försöker kontakta SCB API

**Lösningar:**
1. Kontrollera internetanslutning: `curl https://api.scb.se/OV0104/v1/doris/sv/ssd/`
2. Verifiera brandväggsinställningar
3. Kontrollera DNS-upplösning: `nslookup api.scb.se`
4. Testa med olika nätverk

### Problem: Port 8000 redan används

```bash
# Hitta process som använder porten
lsof -i :8000

# Ändra port i docker-compose.yml
ports:
  - "8001:8000"  # Extern port:Intern port
```

### Problem: Docker build misslyckas

```bash
# Rensa Docker cache
docker system prune -a

# Bygg utan cache
docker-compose build --no-cache
```

## Performance Tuning

### Uvicorn Workers

För högre genomströmning, öka antalet workers:

```python
if __name__ == "__main__":
    uvicorn.run(
        api,
        host="0.0.0.0",
        port=8000,
        workers=4,  # Antal CPU-cores
        log_level="info"
    )
```

### Connection Pooling

pyscbwrapper använder requests. Överväg att använda en session med connection pooling:

```python
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(total=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('https://', adapter)
```

## Backup och Disaster Recovery

### Data Caching

Överväg att cacha SCB-data för att minska belastningen på API:et:

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=100)
def cached_get_table_metadata(table_id: str, language: str):
    # Din metadata-hämtningskod här
    pass
```

### Health Checks

Implementera omfattande health checks:

```python
@api.get("/health/detailed")
async def detailed_health():
    checks = {
        "server": "healthy",
        "scb_api": await check_scb_api_connection(),
        "memory": get_memory_usage(),
        "disk": get_disk_usage()
    }
    return checks
```

---

För ytterligare hjälp, se README.md eller öppna ett issue på GitHub.
