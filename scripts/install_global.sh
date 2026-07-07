#!/usr/bin/env bash

# This script links the local skills and rules to the global AGY directory
# so they are available in every project you work on.

AGY_DIR="$HOME/.gemini/antigravity-cli"

mkdir -p "$AGY_DIR/skills"
mkdir -p "$AGY_DIR/rules"

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(dirname "$SCRIPT_DIR")

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
