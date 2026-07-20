#!/usr/bin/env bash

# This script links the local skills and rules to the global config
# directories for both Gemini (AGY) and Claude Code, so the library
# is available in every project you work on regardless of agent.

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO_ROOT=$(dirname "$SCRIPT_DIR")

echo "Installing Python dependencies..."
if command -v pip3 &> /dev/null; then
  PIP_BIN=pip3
elif command -v pip &> /dev/null; then
  PIP_BIN=pip
else
  echo "Error: pip not found."
  echo "Please download and install Python and pip from https://www.python.org/downloads/ and try again."
  exit 1
fi

"$PIP_BIN" install "$REPO_ROOT"
if [ $? -ne 0 ]; then
  echo "Error: Failed to install dependencies."
  echo "Please download and install Python and pip from https://www.python.org/downloads/ and try again."
  exit 1
fi

# --- Gemini / Antigravity (AGY) integration ---
AGY_DIR="$HOME/.gemini/antigravity-cli"

mkdir -p "$AGY_DIR/skills"
mkdir -p "$AGY_DIR/rules"

echo "Linking skills to global AGY configuration"
for skill in "$REPO_ROOT/.agents/skills"/*; do
  if [ -d "$skill" ]; then
    ln -sfn "$skill" "$AGY_DIR/skills/$(basename "$skill")"
  fi
done

echo "Linking rules to global AGY configuration"
for rule in "$REPO_ROOT/.agents/rules"/*; do
  if [ -f "$rule" ]; then
    ln -sf "$rule" "$AGY_DIR/rules/"
  fi
done

# --- Claude Code integration ---
CLAUDE_DIR="$HOME/.claude"

mkdir -p "$CLAUDE_DIR/skills"

echo "Linking skills to global Claude Code configuration"
for skill in "$REPO_ROOT/.agents/skills"/*; do
  if [ -d "$skill" ]; then
    ln -sfn "$skill" "$CLAUDE_DIR/skills/$(basename "$skill")"
  fi
done

echo "Linking command skills (/work_next_item, /resume_task, /groom_backlogs) to global Claude Code configuration"
for skill in "$REPO_ROOT/.agents/skill_commands"/*; do
  if [ -d "$skill" ]; then
    ln -sfn "$skill" "$CLAUDE_DIR/skills/$(basename "$skill")"
  fi
done

echo "Registering library rulebook in global Claude memory"
CLAUDE_MEMORY="$CLAUDE_DIR/CLAUDE.md"
MARKER_START="<!-- ai_knowledge_library:start -->"
MARKER_END="<!-- ai_knowledge_library:end -->"

if [ -f "$CLAUDE_MEMORY" ] && grep -qF "$MARKER_START" "$CLAUDE_MEMORY"; then
  # Refresh the existing managed block in place
  TMP_FILE=$(mktemp)
  awk -v start="$MARKER_START" -v end="$MARKER_END" -v repo="$REPO_ROOT" '
    $0 == start {print; print "@" repo "/AGENTS.md"; skip=1; next}
    $0 == end {skip=0}
    !skip {print}
  ' "$CLAUDE_MEMORY" > "$TMP_FILE" && mv "$TMP_FILE" "$CLAUDE_MEMORY"
else
  {
    echo ""
    echo "$MARKER_START"
    echo "@$REPO_ROOT/AGENTS.md"
    echo "$MARKER_END"
  } >> "$CLAUDE_MEMORY"
fi

echo "Integration complete. Your AI Knowledge Library is now globally accessible to Gemini and Claude."
