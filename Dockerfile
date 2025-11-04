FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY scb_mcp_server_http.py .
COPY scb_mcp_server.py .

# Expose port
EXPOSE 8000

# Run the HTTP server
CMD ["python", "scb_mcp_server_http.py"]
