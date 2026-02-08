#!/bin/bash
# Run the Brief pipeline
# Called by the LaunchAgent on schedule

BRIEF_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$BRIEF_DIR"

# Activate virtual environment
source "$BRIEF_DIR/venv/bin/activate"

# Prevent macOS from sleeping while the pipeline runs
# (Dark Wake can kill the process before it finishes)
caffeinate -s -w $$ &

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

# Always run the technical brief (daily)
python -m src.main --profile technical 2>&1 | tee -a "$BRIEF_DIR/brief.log"

# Run the team brief on Thursdays only (day 4)
if [ "$(date +%u)" = "4" ]; then
    python -m src.main --profile team 2>&1 | tee -a "$BRIEF_DIR/brief.log"
fi

# Put the Mac back to sleep after the pipeline finishes
# (it was woken at 4:55 AM just for this — no reason to stay on)
pmset sleepnow
