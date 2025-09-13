#!/bin/bash
# startup.sh - verify environment and launch research agent
set -e

MODEL="Mixtral-8x7B-v0.1"

echo "=== Startup: checking Ollama ==="
if ! command -v ollama >/dev/null 2>&1; then
  echo "Ollama is not installed. Please install Ollama before running."
  exit 1
fi

# ensure ollama server running
if ! pgrep -x ollama >/dev/null 2>&1; then
  echo "Starting Ollama service..."
  nohup ollama serve >/root/ollama.log 2>&1 &
  sleep 5
fi

# ensure model available
if ! ollama list | grep -q "$MODEL"; then
  echo "Pulling model $MODEL..."
  ollama pull "$MODEL"
fi

# run research agent with passed arguments
python3 'Complete Autonomous Research System' "$@"
