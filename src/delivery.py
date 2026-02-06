"""Delivery for Brief (spec 008).

Saves the digest as an HTML file to ~/Briefs/ and handles auto-open tracking.
"""

import logging
import subprocess
from pathlib import Path

from . import database as db

logger = logging.getLogger(__name__)

DEFAULT_OUTPUT_DIR = Path.home() / "Briefs"


def deliver_digest(conn, html_content, run_date, output_dir=None):
    """Save the digest HTML to a file and return the file path."""
    output_dir = Path(output_dir) if output_dir else DEFAULT_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"brief-{run_date}.html"
    file_path = output_dir / filename

    # Idempotency: don't overwrite if already delivered
    if db.is_delivered_today(conn, run_date):
        logger.info("Digest already delivered for %s, skipping", run_date)
        return None

    file_path.write_text(html_content, encoding="utf-8")
    db.record_delivery(conn, run_date, file_path)

    logger.info("Digest saved to %s", file_path)
    return file_path


def deliver_error(run_date, error_message, output_dir=None):
    """Save an error page when the pipeline fails."""
    output_dir = Path(output_dir) if output_dir else DEFAULT_OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"brief-{run_date}-error.html"
    file_path = output_dir / filename

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Brief — Error — {run_date}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, sans-serif;
            background: #0a0a0a; color: #e0e0e0;
            padding: 2rem; max-width: 600px; margin: 0 auto;
        }}
        h1 {{ color: #ff6b6b; }}
        pre {{ background: #1a1a1a; padding: 1rem; border-radius: 6px;
               overflow-x: auto; font-size: 0.85rem; color: #ccc; }}
    </style>
</head>
<body>
    <h1>Brief couldn't generate your digest today</h1>
    <p>Something went wrong during the {run_date} pipeline run.</p>
    <pre>{error_message}</pre>
    <p style="color: #666; margin-top: 2rem;">Check the logs for more detail.</p>
</body>
</html>"""

    file_path.write_text(html, encoding="utf-8")
    logger.error("Error digest saved to %s", file_path)
    return file_path


def open_digest(file_path):
    """Open the digest in the default browser (macOS)."""
    try:
        subprocess.run(["open", str(file_path)], check=True)
        logger.info("Opened digest in browser: %s", file_path)
    except Exception as e:
        logger.warning("Failed to open digest: %s", e)
