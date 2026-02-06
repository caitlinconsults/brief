#!/bin/bash
# Run the Brief pipeline
# Called by the LaunchAgent on schedule

BRIEF_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$BRIEF_DIR"

# Activate virtual environment
source "$BRIEF_DIR/venv/bin/activate"

# Prevent duplicate runs
LOCK_FILE="$BRIEF_DIR/.brief.lock"
if [ -f "$LOCK_FILE" ]; then
    PID=$(cat "$LOCK_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        echo "Brief pipeline already running (PID $PID), skipping"
        exit 0
    fi
fi
echo $$ > "$LOCK_FILE"
trap "rm -f $LOCK_FILE" EXIT

# Run the pipeline
python -m src.main 2>&1 | tee -a "$BRIEF_DIR/brief.log"
