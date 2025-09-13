#!/bin/bash
# setup.sh - Complete setup for research agent

echo "================================"
echo "Research Agent Setup"
echo "================================"

# Install system dependencies
echo "Installing dependencies..."
apt-get update
apt-get install -y python3-pip git curl cron sqlite3 --no-install-recommends

# Install Python packages
echo "Installing Python packages..."
pip3 install aiohttp beautifulsoup4 requests

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

# Setup cron for daily runs
echo "Setting up daily schedule..."
(crontab -l 2>/dev/null; echo "0 3 * * * cd $(pwd) && python3 research_agent.py --hours 3 >> logs/cron.log 2>&1") | crontab -

echo "Setup complete!"
echo "Run: python3 research_agent.py 'your topic'"
