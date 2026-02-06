"""Ranking and selection engine for Brief (spec 006).

Scores enriched content items and selects the top items per cluster per lane
for inclusion in the daily digest. No LLM — purely rule-based and deterministic.
"""

import json
import logging
import math
import random
from datetime import datetime, timezone
from pathlib import Path

import yaml

from . import database as db

logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).parent.parent / "config" / "ranking_weights.yaml"


def load_weights():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def rank_and_select(conn, source_registry, run_date):
    """Score all enriched items, cluster them, and select top items for the digest.

    Returns a list of selected items grouped by cluster, ready for digest generation.
    """
    config = load_weights()
    weights = config["weights"]
    selection = config["selection"]
    recency_config = config["recency"]

    # Build a lookup of source trust weights
    trust_lookup = {}
    for source in source_registry:
        trust_lookup[source["slug"]] = source.get("trust_weight", 0.5)

    # Get all enriched items for today
    items = db.get_enriched_items(conn, run_date)
    if not items:
        logger.info("No enriched items to rank")
        return []

    # Score each item
    now = datetime.now(timezone.utc)
    for item in items:
        item["relevance_score"] = compute_score(item, weights, recency_config,
                                                 trust_lookup, now)

    # Cluster items by topic
    from .enrichment import cluster_items
    items = cluster_items(items)

    # Update database with scores and clusters
    for item in items:
        db.update_ranking(
            conn, item["id"],
            item["relevance_score"],
            item["cluster_id"],
            item.get("novelty_flag", False)
        )

    # Select top items per cluster per lane
    selected = select_for_digest(items, selection)

    return selected


def compute_score(item, weights, recency_config, trust_lookup, now):
    """Compute a composite relevance score for a single item."""
    # Recency score: exponential decay
    recency_score = 0.5  # default if no date
    if item.get("published_date"):
        try:
            pub_date = datetime.fromisoformat(item["published_date"])
            if pub_date.tzinfo is None:
                pub_date = pub_date.replace(tzinfo=timezone.utc)
            hours_ago = (now - pub_date).total_seconds() / 3600
            half_life = recency_config.get("half_life_hours", 48)
            recency_score = math.exp(-0.693 * hours_ago / half_life)
        except (ValueError, TypeError):
            pass

    # Source trust score
    trust_score = trust_lookup.get(item.get("source_slug", ""), 0.5)

    # Lane affinity score: max of the three lanes
    lane_score = max(
        item.get("lane_builders", 0.0),
        item.get("lane_security", 0.0),
        item.get("lane_business", 0.0),
    )

    # Popularity: not available for most sources in MVP, use 0.5 default
    popularity_score = 0.5

    # Novelty: for MVP, all items are "novel" (no history to compare against)
    novelty_score = 0.5

    # Composite score
    score = (
        weights["recency"] * recency_score +
        weights["source_trust"] * trust_score +
        weights["lane_affinity"] * lane_score +
        weights["popularity"] * popularity_score +
        weights["novelty"] * novelty_score
    )

    return round(score, 4)


def select_for_digest(items, selection_config):
    """Select top items per cluster per lane for the digest.

    Returns a list of clusters, each with selected items per lane.
    """
    target_size = selection_config.get("target_digest_size", 20)
    max_per_lane = selection_config.get("max_items_per_lane", 3)
    novelty_budget = selection_config.get("novelty_budget", 0.25)

    # Group items by cluster
    clusters = {}
    for item in items:
        cid = item.get("cluster_id", 0)
        if cid not in clusters:
            clusters[cid] = {
                "cluster_id": cid,
                "cluster_topic": item.get("cluster_topic", "uncategorized"),
                "items": [],
            }
        clusters[cid]["items"].append(item)

    # For each cluster, pick top items per lane
    result = []
    total_selected = 0

    for cid in sorted(clusters.keys()):
        cluster = clusters[cid]
        cluster_items = cluster["items"]

        # Sort by relevance score descending
        cluster_items.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

        selected = {
            "cluster_id": cid,
            "cluster_topic": cluster["cluster_topic"],
            "builders": [],
            "security": [],
            "business": [],
            "all_items": [],
        }

        for item in cluster_items:
            if total_selected >= target_size:
                break

            # Determine which lane(s) this item belongs to
            added = False
            if item.get("lane_builders", 0) >= 0.3 and len(selected["builders"]) < max_per_lane:
                selected["builders"].append(item)
                added = True
            if item.get("lane_security", 0) >= 0.3 and len(selected["security"]) < max_per_lane:
                selected["security"].append(item)
                added = True
            if item.get("lane_business", 0) >= 0.3 and len(selected["business"]) < max_per_lane:
                selected["business"].append(item)
                added = True

            # If no lane scored above threshold, add to the highest-scoring lane
            if not added:
                best_lane = max(
                    [("builders", item.get("lane_builders", 0)),
                     ("security", item.get("lane_security", 0)),
                     ("business", item.get("lane_business", 0))],
                    key=lambda x: x[1]
                )[0]
                if len(selected[best_lane]) < max_per_lane:
                    selected[best_lane].append(item)

            selected["all_items"].append(item)
            total_selected += 1

        # Only include clusters that have at least one item in any lane
        if selected["builders"] or selected["security"] or selected["business"]:
            result.append(selected)

    # Sort clusters by average relevance score (best clusters first)
    result.sort(
        key=lambda c: sum(i.get("relevance_score", 0) for i in c["all_items"])
                       / max(len(c["all_items"]), 1),
        reverse=True
    )

    return result
