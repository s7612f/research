#!/bin/bash
set -e
MODEL="Mixtral-8x7B-v0.1"
DB_PATH="/root/research.db"

# Ensure Ollama is reachable
if ! curl -s http://localhost:11434/api/tags >/dev/null; then
  echo "Ollama is not running on localhost:11434"
  echo "Start Ollama before running this script."
  exit 1
fi

# Verify the required model is installed
if ! ollama list 2>/dev/null | grep -q "$MODEL"; then
  echo "Model $MODEL not found. Pulling..."
  ollama pull "$MODEL"
fi

# Ensure the database exists for persistence
mkdir -p "$(dirname "$DB_PATH")"
touch "$DB_PATH"

# Display the URL for the web interface
IP=$(hostname -I | awk '{print $1}')
echo "Open: http://$IP:7777"

# Launch the startup helper which configures mode and runs the web interface
exec python3 startup.py "$@"
