"""Main pipeline orchestrator for Brief.

Runs the full daily pipeline:
  ingest → enrich → rank → generate digest → deliver

Supports multiple profiles (e.g. technical, team) via --profile flag.
"""

import argparse
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

PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
PROFILES_DIR = CONFIG_DIR / "profiles"


def load_profile(profile_name):
    """Load a profile config from config/profiles/{name}.yaml.

    If a {name}.local.yaml exists, its values are merged on top.
    This lets orgs keep private config (tool policies, etc.) out of the repo.
    """
    profile_path = PROFILES_DIR / f"{profile_name}.yaml"
    if not profile_path.exists():
        raise FileNotFoundError(f"Profile not found: {profile_path}")
    with open(profile_path) as f:
        profile = yaml.safe_load(f)

    local_path = PROFILES_DIR / f"{profile_name}.local.yaml"
    if local_path.exists():
        with open(local_path) as f:
            local = yaml.safe_load(f) or {}
        profile.update(local)
        logger.info("Merged local overrides from %s", local_path.name)

    return profile


def load_sources(profile):
    """Load sources from the profile's configured sources file."""
    sources_file = profile.get("sources_file", "sources.yaml")
    with open(CONFIG_DIR / sources_file) as f:
        config = yaml.safe_load(f)
    return config.get("sources", [])


def run_pipeline(profile_name="technical"):
    """Run the full Brief pipeline end-to-end for a given profile."""
    profile = load_profile(profile_name)
    brief_name = profile.get("name", "Brief")
    run_date = datetime.now().strftime("%Y-%m-%d")  # Local time, not UTC
    logger.info("=== %s pipeline starting for %s ===", brief_name, run_date)

    # Each profile gets its own database
    db_path = PROJECT_ROOT / profile.get("db_name", "brief.db")
    conn = db.get_connection(db_path)
    db.init_db(conn)
    run_id = db.start_pipeline_run(conn, run_date)

    try:
        # Load source registry
        sources = load_sources(profile)
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
        max_age_days = profile.get("max_age_days", 7)
        items_ingested = ingest_sources(conn, sources, run_date, max_age_days=max_age_days)
        logger.info("Ingested %d new items", items_ingested)
        db.update_pipeline_run(conn, run_id, items_ingested=items_ingested)

        # Step 2: Enrich
        logger.info("--- Step 2: Enrichment ---")
        client = anthropic.Anthropic()
        items_enriched = enrich_items(conn, client, profile)
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
        html = generate_digest(clusters, client, run_date, profile)

        # Step 5: Deliver
        logger.info("--- Step 5: Delivery ---")
        output_prefix = profile.get("output_prefix", "brief")
        file_path = deliver_digest(conn, html, run_date, output_prefix=output_prefix)

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
        logger.info("=== %s pipeline completed successfully ===", brief_name)

    except Exception as e:
        logger.exception("Pipeline failed: %s", e)
        db.update_pipeline_run(conn, run_id, status="failed",
                               completed_at=db.now_iso(),
                               error_message=str(e))
        # Deliver error page
        output_prefix = profile.get("output_prefix", "brief")
        error_path = deliver_error(run_date, str(e), output_prefix=output_prefix)
        if error_path:
            open_digest(error_path)

    finally:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="Run the Brief pipeline")
    parser.add_argument(
        "--profile",
        default="technical",
        help="Profile to run: technical, team, or all (default: technical)"
    )
    args = parser.parse_args()

    if args.profile == "all":
        for profile_name in ["technical", "team"]:
            try:
                run_pipeline(profile_name)
            except Exception as e:
                logger.error("Profile '%s' failed: %s", profile_name, e)
                # Continue with next profile — don't let one failure block the other
    else:
        run_pipeline(args.profile)


if __name__ == "__main__":
    main()
