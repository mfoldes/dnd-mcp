#!/bin/sh
set -e

# Initialize and logs directories
if [ ! -d "$CACHE_DIR" ]; then
    mkdir -p "$CACHE_DIR"
    echo "Created cache directory at $CACHE_DIR"
fi

if [ ! -d "$LOGS_DIR" ]; then
    mkdir -p "$LOGS_DIR"
    echo "Created logs directory at $LOGS_DIR"
fi

# Check connectivity to the DND5e API
echo "Checking connectivity to DND5e API at $DND5E_API_URL..."
python -c "import urllib.request; urllib.request.urlopen('https://www.dnd5eapi.co/api')" || {
    echo "Warning: Could not connect to D&D API"
}

# Start the application
echo "Starting DND MCP Server..."
exec python -m dnd_mcp.server "$@"