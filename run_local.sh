#!/bin/bash

# Exit on error
set -e

echo "=== Starting HypnoForge Local Backend ==="
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Ensuring dependencies are installed..."
pip install -r backend/requirements.txt

echo "Registering static-ffmpeg..."
python -c "import static_ffmpeg; static_ffmpeg.add_paths(); print('Static FFmpeg registered successfully.')"

echo "Launching FastAPI backend..."
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
