#!/bin/bash
# Check for unread Brief digests and open the latest one
# Called by the LaunchAgent on login/wake

BRIEFS_DIR="$HOME/Briefs"
MARKER_DIR="$BRIEFS_DIR/.opened"

mkdir -p "$MARKER_DIR"

# Find the most recent digest
LATEST=$(ls -t "$BRIEFS_DIR"/brief-*.html 2>/dev/null | head -1)

if [ -z "$LATEST" ]; then
    exit 0
fi

BASENAME=$(basename "$LATEST")
MARKER="$MARKER_DIR/$BASENAME.opened"

# Only open if not already opened
if [ ! -f "$MARKER" ]; then
    open "$LATEST"
    touch "$MARKER"
fi
