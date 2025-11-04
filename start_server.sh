#!/bin/bash
# Startup script for SCB MCP Server

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}SCB MCP Server Starter${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}Python version:${NC}"
python3 --version
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${BLUE}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${BLUE}Activating virtual environment...${NC}"
source venv/bin/activate

# Install/upgrade dependencies
echo -e "${BLUE}Installing dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt

echo ""
echo -e "${GREEN}Dependencies installed successfully${NC}"
echo ""

# Ask user which mode to run
echo "Select server mode:"
echo "1) stdio mode (for Claude Desktop - local)"
echo "2) HTTP/SSE mode (for remote access)"
echo ""
read -p "Enter choice [1-2]: " choice

case $choice in
    1)
        echo ""
        echo -e "${GREEN}Starting server in stdio mode...${NC}"
        echo -e "${BLUE}Press Ctrl+C to stop${NC}"
        echo ""
        python scb_mcp_server.py
        ;;
    2)
        echo ""
        echo -e "${GREEN}Starting server in HTTP/SSE mode...${NC}"
        echo -e "${BLUE}Server will be available at: http://localhost:8000${NC}"
        echo -e "${BLUE}Press Ctrl+C to stop${NC}"
        echo ""
        python scb_mcp_server_http.py
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac
