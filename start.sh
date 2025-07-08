#!/bin/bash
set -e

echo "=== DermAssist Startup Script ==="
echo "Running pre-startup diagnostics..."

# Run the diagnostic script
python debug_settings.py

echo ""
echo "=== Starting Application ==="
echo "Running: uvicorn backend.main:app --host 0.0.0.0 --port 8000"

# Start the application
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000 