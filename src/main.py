"""Main pipeline orchestrator for Brief.

Runs the full daily pipeline:
  ingest → enrich → rank → generate digest → deliver
"""

import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import anthropic
import yaml
from dotenv import load_dotenv

from . import database as db
from .ingestion import ingest_sources
from .enrichment import enrich_items
from .ranking import rank_and_select
from .digest import generate_digest
from .delivery import deliver_digest, deliver_error, open_digest

# Load .env from project root
load_dotenv(Path(__file__).parent.parent / ".env")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path(__file__).parent.parent / "brief.log"),
    ]
)
logger = logging.getLogger("brief")

CONFIG_DIR = Path(__file__).parent.parent / "config"


def load_sources():
    with open(CONFIG_DIR / "sources.yaml") as f:
        config = yaml.safe_load(f)
    return config.get("sources", [])


def run_pipeline():
    """Run the full Brief pipeline end-to-end."""
    run_date = datetime.now().strftime("%Y-%m-%d")  # Local time, not UTC
    logger.info("=== Brief pipeline starting for %s ===", run_date)

    # Initialize
    conn = db.get_connection()
    db.init_db(conn)
    run_id = db.start_pipeline_run(conn, run_date)

    try:
        # Load source registry
        sources = load_sources()
        enabled = [s for s in sources if s.get("enabled")]
        logger.info("Sources: %d total, %d enabled", len(sources), len(enabled))

        if not enabled:
            logger.warning("No sources enabled — nothing to ingest")
            db.update_pipeline_run(conn, run_id, status="completed",
                                   completed_at=db.now_iso(),
                                   items_ingested=0)
            return

        # Step 1: Ingest
        logger.info("--- Step 1: Ingestion ---")
        items_ingested = ingest_sources(conn, sources, run_date)
        logger.info("Ingested %d new items", items_ingested)
        db.update_pipeline_run(conn, run_id, items_ingested=items_ingested)

        # Step 2: Enrich
        logger.info("--- Step 2: Enrichment ---")
        client = anthropic.Anthropic()
        items_enriched = enrich_items(conn, client)
        logger.info("Enriched %d items", items_enriched)
        db.update_pipeline_run(conn, run_id, items_enriched=items_enriched)

        # Step 3: Rank and select
        logger.info("--- Step 3: Ranking and selection ---")
        clusters = rank_and_select(conn, sources, run_date)
        total_selected = sum(len(c["all_items"]) for c in clusters)
        logger.info("Selected %d items across %d clusters", total_selected, len(clusters))
        db.update_pipeline_run(conn, run_id, items_selected=total_selected)

        # Step 4: Generate digest
        logger.info("--- Step 4: Digest generation ---")
        html = generate_digest(clusters, client, run_date)

        # Step 5: Deliver
        logger.info("--- Step 5: Delivery ---")
        file_path = deliver_digest(conn, html, run_date)

        if file_path:
            # Mark selected items as published
            all_item_ids = []
            for c in clusters:
                all_item_ids.extend(i["id"] for i in c["all_items"])
            if all_item_ids:
                db.mark_published(conn, all_item_ids)

            # Open in browser
            open_digest(file_path)

        # Done
        db.update_pipeline_run(conn, run_id, status="completed",
                               completed_at=db.now_iso())
        logger.info("=== Brief pipeline completed successfully ===")

    except Exception as e:
        logger.exception("Pipeline failed: %s", e)
        db.update_pipeline_run(conn, run_id, status="failed",
                               completed_at=db.now_iso(),
                               error_message=str(e))
        # Deliver error page
        error_path = deliver_error(run_date, str(e))
        if error_path:
            open_digest(error_path)

    finally:
        conn.close()


if __name__ == "__main__":
    run_pipeline()
