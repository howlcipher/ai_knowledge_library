#!/usr/bin/env bash

# This script links the local skills and rules to the global AGY directory
# so they are available in every project you work on.

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(dirname "$SCRIPT_DIR")

echo "Installing Python dependencies..."
if command -v pip3 &> /dev/null; then
  pip3 install -r "$REPO_ROOT/requirements.txt"
  if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies."
    echo "Please download and install Python and pip from https://www.python.org/downloads/ and try again."
    exit 1
  fi
elif command -v pip &> /dev/null; then
  pip install -r "$REPO_ROOT/requirements.txt"
  if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies."
    echo "Please download and install Python and pip from https://www.python.org/downloads/ and try again."
    exit 1
  fi
else
  echo "Error: pip not found."
  echo "Please download and install Python and pip from https://www.python.org/downloads/ and try again."
  exit 1
fi

AGY_DIR="$HOME/.gemini/antigravity-cli"

mkdir -p "$AGY_DIR/skills"
mkdir -p "$AGY_DIR/rules"

echo "Linking skills to global AGY configuration"
for skill in "$REPO_ROOT/.agents/skills"/*; do
  if [ -d "$skill" ]; then
    ln -sf "$skill" "$AGY_DIR/skills/"
  fi
done

echo "Linking rules to global AGY configuration"
for rule in "$REPO_ROOT/.agents/rules"/*; do
  if [ -f "$rule" ]; then
    ln -sf "$rule" "$AGY_DIR/rules/"
  fi
done

echo "Integration complete. Your AI Knowledge Library is now globally accessible."
