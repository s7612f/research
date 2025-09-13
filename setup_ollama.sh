#!/bin/bash
# setup_ollama.sh - Install Ollama and Dolphin Mixtral 8x7B on RunPod
# Checks prerequisites, installs dependencies, pulls model

set -e

echo "================================"
echo "RunPod Ollama Setup"
echo "================================"

# Check GPU availability
if ! command -v nvidia-smi >/dev/null 2>&1; then
  echo "GPU not detected. Make sure you are on a GPU-enabled RunPod." >&2
  exit 1
else
  nvidia-smi
fi

# Check Python
if ! command -v python3 >/dev/null 2>&1; then
  echo "Python3 is required. Installing..."
  apt-get update && apt-get install -y python3 python3-pip
else
  python3 --version
fi

# Install basic utilities
apt-get update
apt-get install -y curl git --no-install-recommends

# Install Ollama if not present
if ! command -v ollama >/dev/null 2>&1; then
  echo "Installing Ollama..."
  curl https://ollama.ai/install.sh | sh
else
  echo "Ollama already installed"
fi

# Ensure Ollama service running
if ! pgrep -x "ollama" >/dev/null; then
  echo "Starting Ollama service..."
  ollama serve &
  sleep 5
fi

# Pull Dolphin Mixtral model
if ! ollama list | grep -q "dolphin-mixtral"; then
  echo "Pulling dolphin-mixtral:8x7b model..."
  ollama pull dolphin-mixtral:8x7b
else
  echo "Dolphin Mixtral model already present"
fi

# Install Python packages for research
pip3 install --upgrade langchain chromadb requests beautifulsoup4

echo "Setup complete!"
echo "Run: ollama run dolphin-mixtral:8x7b"
