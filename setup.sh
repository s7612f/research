#!/bin/bash
# setup.sh - On-demand setup for research agent

echo "================================"
echo "Research Agent Setup"
echo "================================"

# Install system dependencies
echo "Installing dependencies..."
apt-get update
apt-get install -y python3-pip git curl sqlite3 --no-install-recommends

# Install Python packages
echo "Installing Python packages..."
# Pre-install newer blinker to satisfy Flask without removing distutils version
pip3 install --ignore-installed blinker==1.9.0
pip3 install aiohttp beautifulsoup4 requests youtube-transcript-api flask

# Create directories
mkdir -p logs data reports cache

# Test Ollama
echo "Testing Ollama connection..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✓ Ollama is running"
    ollama list
else
    echo "⚠ Ollama not detected - make sure it's running"
fi

echo "Setup complete!"
echo "Run: ./startup.sh"
