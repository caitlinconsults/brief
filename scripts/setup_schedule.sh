#!/bin/bash
# Set up Brief scheduling on macOS
# Creates LaunchAgent plists for:
#   1. Running the pipeline daily at 5 AM
#   2. Checking for unread digests on login/wake

set -e

BRIEF_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"

mkdir -p "$LAUNCH_AGENTS_DIR"

# Make scripts executable
chmod +x "$BRIEF_DIR/scripts/run_brief.sh"
chmod +x "$BRIEF_DIR/scripts/check_digest.sh"

# --- 1. Daily pipeline run at 5 AM ---
cat > "$LAUNCH_AGENTS_DIR/com.brief.pipeline.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.brief.pipeline</string>
    <key>ProgramArguments</key>
    <array>
        <string>${BRIEF_DIR}/scripts/run_brief.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>5</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>${BRIEF_DIR}/brief-launchd.log</string>
    <key>StandardErrorPath</key>
    <string>${BRIEF_DIR}/brief-launchd.log</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin</string>
    </dict>
</dict>
</plist>
EOF

# --- 2. Check for unread digests on login ---
cat > "$LAUNCH_AGENTS_DIR/com.brief.check-digest.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.brief.check-digest</string>
    <key>ProgramArguments</key>
    <array>
        <string>${BRIEF_DIR}/scripts/check_digest.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>${BRIEF_DIR}/brief-launchd.log</string>
    <key>StandardErrorPath</key>
    <string>${BRIEF_DIR}/brief-launchd.log</string>
</dict>
</plist>
EOF

# --- 3. Schedule Mac to wake at 4:55 AM ---
echo "Setting Mac to wake at 4:55 AM daily..."
sudo pmset repeat wakeorpoweron MTWRFSU 04:55:00 2>/dev/null || \
    echo "NOTE: Could not set wake schedule (may need sudo). You can set this manually:"
    echo "  sudo pmset repeat wakeorpoweron MTWRFSU 04:55:00"
    echo "  Or: System Settings > Energy > Schedule"

# --- Load the agents ---
launchctl unload "$LAUNCH_AGENTS_DIR/com.brief.pipeline.plist" 2>/dev/null || true
launchctl load "$LAUNCH_AGENTS_DIR/com.brief.pipeline.plist"

launchctl unload "$LAUNCH_AGENTS_DIR/com.brief.check-digest.plist" 2>/dev/null || true
launchctl load "$LAUNCH_AGENTS_DIR/com.brief.check-digest.plist"

echo ""
echo "Brief scheduling configured:"
echo "  Pipeline runs daily at 5:00 AM"
echo "  Mac wakes at 4:55 AM (if pmset succeeded)"
echo "  Unread digest auto-opens on login"
echo ""
echo "To test the pipeline manually:"
echo "  cd $BRIEF_DIR && source venv/bin/activate && python -m src.main"
echo ""
echo "To uninstall:"
echo "  launchctl unload ~/Library/LaunchAgents/com.brief.pipeline.plist"
echo "  launchctl unload ~/Library/LaunchAgents/com.brief.check-digest.plist"
echo "  sudo pmset repeat cancel"
