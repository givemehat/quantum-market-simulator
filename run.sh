#!/bin/bash
set -e

echo "Starting Unified QDMS Application..."

# Activate virtual environment
source venv/bin/activate

# Run the unified FastAPI server
uvicorn classical_bridge.app:app --port 8000 --host 0.0.0.0
