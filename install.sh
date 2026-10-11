#!/usr/bin/env bash
# Copy prompt-clarifier into ~/.claude/skills (override with CLAUDE_SKILLS_DIR).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
DEST="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"
if [ ! -f "$ROOT/skills/prompt-clarifier/SKILL.md" ]; then
  echo "missing skills/prompt-clarifier/SKILL.md" >&2
  exit 1
fi
mkdir -p "$DEST"
rm -rf "$DEST/prompt-clarifier"
cp -R "$ROOT/skills/prompt-clarifier" "$DEST/prompt-clarifier"
echo "installed prompt-clarifier -> $DEST/prompt-clarifier"
