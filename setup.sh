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
if [ ! -f users.json ]; then
  echo "Create admin user"
  read -p "Username: " USERNAME
  read -s -p "Password: " PASSWORD
  echo
  cat <<'PY' | USERNAME="$USERNAME" PASSWORD="$PASSWORD" python3
import json, hashlib, os
u=os.environ['USERNAME']
p=os.environ['PASSWORD']
with open('config.json') as f:
    cfg=json.load(f)
db_dir=cfg.get('database_dir','/root/databases')
os.makedirs(db_dir, exist_ok=True)
users={u:{'password': hashlib.sha256(p.encode()).hexdigest(),
          'db_path': f"{db_dir}/{u}.db", 'email': None}}
with open('users.json','w') as f:
    json.dump(users,f)
PY
fi
echo "Run: ./startup.sh"
