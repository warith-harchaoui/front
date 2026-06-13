#!/usr/bin/env bash
# install-alt-ai.sh — macOS and Ubuntu/Linux installer for the local
# Ollama-based alt-text generator. For Windows, use install-alt-ai.ps1.
#
# Installs (if missing): Ollama.
# Pulls: gemma4:e2b   (Apple Silicon: gemma4:e2b-mlx)
# Override with: OLLAMA_MODEL=<tag>  e.g. OLLAMA_MODEL=gemma3n:e2b
#
# After this script finishes, generate alt text with:
#   node front/scripts/alt-from-ollama.mjs path/to/image.jpg

set -euo pipefail

BASE="${OLLAMA_MODEL_BASE:-gemma4:e2b}"
OS="$(uname -s)"
ARCH="$(uname -m)"

if [ "$OS" = "Darwin" ] && { [ "$ARCH" = "arm64" ] || [ "$ARCH" = "aarch64" ]; }; then
  MODEL="${OLLAMA_MODEL:-${BASE}-mlx}"
else
  MODEL="${OLLAMA_MODEL:-$BASE}"
fi

echo "→ Platform: $OS $ARCH"
echo "→ Target model: $MODEL"

# 1. Install Ollama if missing.
if ! command -v ollama >/dev/null 2>&1; then
  case "$OS" in
    Darwin)
      if command -v brew >/dev/null 2>&1; then
        echo "→ Installing Ollama via Homebrew…"
        brew install ollama
      else
        echo "Homebrew not found. Install from https://brew.sh, then re-run this script." >&2
        echo "Or download the macOS app directly from https://ollama.com/download" >&2
        exit 1
      fi
      ;;
    Linux)
      echo "→ Installing Ollama via the official installer script…"
      curl -fsSL https://ollama.com/install.sh | sh
      ;;
    *)
      echo "Unsupported OS for this script: $OS." >&2
      echo "On Windows, run: powershell -ExecutionPolicy Bypass -File install-alt-ai.ps1" >&2
      exit 1
      ;;
  esac
fi

# 2. Make sure the daemon is up.
if ! ollama list >/dev/null 2>&1; then
  echo "→ Starting the Ollama daemon in the background…"
  ( ollama serve >/tmp/ollama.log 2>&1 & )
  for i in 1 2 3 4 5 6 7 8 9 10; do
    sleep 1
    if ollama list >/dev/null 2>&1; then break; fi
    if [ "$i" = "10" ]; then
      echo "Ollama did not start in 10 s. Check /tmp/ollama.log." >&2
      exit 1
    fi
  done
fi

# 3. Pull the model if missing.
if ollama list | awk 'NR>1 {print $1}' | grep -qx "$MODEL"; then
  echo "→ $MODEL already present."
else
  echo "→ Pulling $MODEL …"
  if ! ollama pull "$MODEL"; then
    cat <<EOF >&2

Could not pull "$MODEL".
If the tag is not yet in Ollama's registry, retry with a known-good vision tag:

    OLLAMA_MODEL=gemma3n:e2b $0
    # On Apple Silicon:
    OLLAMA_MODEL=gemma3n:e2b-mlx $0

Browse tags at https://ollama.com/library
EOF
    exit 1
  fi
fi

echo "→ Ready. Test with:"
echo "    node front/scripts/alt-from-ollama.mjs /path/to/image.jpg"
