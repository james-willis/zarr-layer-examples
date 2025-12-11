#!/bin/bash

set -e  # Exit on error

echo "🚀 Setting up Zarr Explorations..."

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ uv is required but not installed."
    echo "Install it with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Install dependencies with uv (will create venv automatically)
echo "📥 Installing Python dependencies with uv..."
uv sync --directory python

# Check if example256.zarr exists
ZARR_FILE="app/example_zarrs/example256.zarr"
if [ ! -d "$ZARR_FILE" ]; then
    echo "🗂️  Generating example256.zarr..."
    uv run --directory python create_example_zarr.py
else
    echo "✅ example256.zarr already exists"
fi

# Start file server
echo "🌐 Starting file server on http://localhost:8000"
echo "📂 Serving from app/ directory"
echo "Press Ctrl+C to stop the server"
echo ""

cd app
python3 -m http.server 8000
