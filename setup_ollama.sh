#!/bin/bash
# setup_ollama.sh - Install Ollama and Dolphin Mixtral 8x7B on macOS or Linux
# Checks prerequisites, installs dependencies, pulls model

set -e

echo "================================"
echo "Ollama Dolphin Mixtral Setup"
echo "================================"

OS="$(uname -s)"

# Determine package manager
if [[ "$OS" == "Darwin" ]]; then
  if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew is required on macOS. Install it from https://brew.sh" >&2
    exit 1
  fi
  PM="brew"
elif [[ "$OS" == "Linux" ]]; then
  if ! command -v apt-get >/dev/null 2>&1; then
    echo "apt-get is required on Linux" >&2
    exit 1
  fi
  PM="apt"
else
  echo "Unsupported OS: $OS" >&2
  exit 1
fi

install_pkg() {
  if [[ "$PM" == "apt" ]]; then
    sudo apt-get install -y "$@"
  else
    brew install "$@"
  fi
}

# Ensure curl, git, python3
for cmd in curl git python3; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Installing $cmd..."
    if [[ "$cmd" == "python3" && "$PM" == "apt" ]]; then
      sudo apt-get update
      install_pkg python3 python3-pip
    else
      install_pkg "$cmd"
    fi
  fi
  command -v "$cmd" >/dev/null 2>&1 && "$cmd" --version >/dev/null 2>&1 || true
done

# GPU check on Linux
if [[ "$OS" == "Linux" ]]; then
  if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi
  else
    echo "⚠ GPU not detected or nvidia-smi missing" >&2
  fi
fi

# Install Ollama if not present
if ! command -v ollama >/dev/null 2>&1; then
  echo "Installing Ollama..."
  curl -fsSL https://ollama.ai/install.sh | sh
else
  echo "Ollama already installed"
fi

# Ensure Ollama service running
if ! pgrep -x "ollama" >/dev/null 2>&1; then
  echo "Starting Ollama service..."
  ollama serve >/dev/null 2>&1 &
  sleep 5
fi

# Pull Dolphin Mixtral model
if ! ollama list | grep -q "dolphin-mixtral:8x7b"; then
  echo "Pulling dolphin-mixtral:8x7b model..."
  ollama pull dolphin-mixtral:8x7b
else
  echo "Dolphin Mixtral model already present"
fi

# Install Python packages for research
pip3 install --upgrade langchain chromadb requests beautifulsoup4

echo "Setup complete!"
echo "Run: ollama run dolphin-mixtral:8x7b"

