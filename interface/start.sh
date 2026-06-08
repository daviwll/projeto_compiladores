#!/bin/bash
# Minipar Compiler Web Interface Launcher
# Linux/Mac bash script to start the web interface

echo "============================================================"
echo "  Minipar Compiler - Web Interface Launcher"
echo "============================================================"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python not found!"
    echo "Please install Python 3.7 or higher"
    exit 1
fi

echo "[1/3] Checking Python installation..."
python3 --version
echo ""

# Check if Gradio is installed
if ! python3 -c "import gradio" &> /dev/null; then
    echo "[2/3] Gradio not found. Installing..."
    pip3 install gradio
    echo ""
else
    echo "[2/3] Gradio already installed"
    echo ""
fi

# Navigate to interface directory
cd "$(dirname "$0")"

echo "[3/3] Starting web interface..."
echo ""
echo "============================================================"
echo "  The interface will open in your browser"
echo "  URL: http://localhost:7860"
echo ""
echo "  Press Ctrl+C to stop the server"
echo "============================================================"
echo ""

# Start the interface
python3 app.py
