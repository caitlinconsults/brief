"""Ingestion pipeline for Brief (spec 004).

Fetches content from enabled sources, normalizes it, deduplicates,
and stores it in the database.
"""

import logging
import time
from datetime import datetime, timedelta, timezone

import feedparser
import requests
from bs4 import BeautifulSoup

from . import database as db
from .security import sanitize_content, verify_url

logger = logging.getLogger(__name__)

REQUEST_TIMEOUT = 30
MAX_AGE_DAYS = 7


def ingest_sources(conn, sources, run_date):
    """Ingest content from all enabled sources. Returns count of new items."""
    total_new = 0

    for source in sources:
        if not source.get("enabled", False):
            continue

        slug = source["slug"]
        method = source["fetch_method"]

        start_time = time.time()
        try:
            if method == "rss":
                items = fetch_rss(source)
            elif method == "api":
                items = fetch_api(source)
            else:
                logger.info("Skipping %s: %s fetch not implemented yet", slug, method)
                db.log_source_health(conn, slug, run_date, "skipped",
                                     error_message=f"{method} not implemented")
                continue

            elapsed_ms = int((time.time() - start_time) * 1000)

            new_count = 0
            for item in items:
                if db.insert_item(conn, item):
                    new_count += 1

            total_new += new_count
            db.log_source_health(conn, slug, run_date, "success",
                                 items_fetched=new_count, response_time_ms=elapsed_ms)
            logger.info("Ingested %d new items from %s (%dms)", new_count, slug, elapsed_ms)

        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            db.log_source_health(conn, slug, run_date, "failure",
                                 error_message=str(e), response_time_ms=elapsed_ms)
            logger.error("Failed to ingest %s: %s", slug, e)
            # Continue with other sources — no single point of failure

    return total_new


def fetch_rss(source):
    """Fetch and parse an RSS/Atom feed. Returns normalized content items."""
    slug = source["slug"]
    url = source["fetch_url"]

    logger.info("Fetching RSS: %s", url)
    feed = feedparser.parse(url)

    if feed.bozo and not feed.entries:
        raise RuntimeError(f"Failed to parse feed: {feed.bozo_exception}")

    items = []
    for entry in feed.entries:
        link = entry.get("link", "")
        if not link:
            continue

        # Verify URL matches expected source domain
        if not verify_url(link, slug):
            logger.warning("Skipping URL with domain mismatch: %s", link)
            continue

        # Extract text content
        raw_text = extract_entry_text(entry)
        # Sanitize content before storage
        raw_text, _flags = sanitize_content(raw_text, slug)

        # Parse published date
        published = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            try:
                published = datetime(*entry.published_parsed[:6],
                                     tzinfo=timezone.utc).isoformat()
            except (TypeError, ValueError):
                pass
        elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
            try:
                published = datetime(*entry.updated_parsed[:6],
                                     tzinfo=timezone.utc).isoformat()
            except (TypeError, ValueError):
                pass

        # Skip items older than MAX_AGE_DAYS
        if published:
            try:
                pub_dt = datetime.fromisoformat(published)
                cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)
                if pub_dt < cutoff:
                    continue
            except (ValueError, TypeError):
                pass

        items.append({
            "title": entry.get("title", "Untitled"),
            "url": link,
            "source_slug": slug,
            "source_name": source["name"],
            "source_type": "rss",
            "published_date": published,
            "content_type": source.get("content_type", "blog_post"),
            "raw_text": raw_text,
        })

    return items


def fetch_api(source):
    """Fetch content via API. Currently only supports Hacker News."""
    slug = source["slug"]

    if slug == "hacker-news":
        return fetch_hacker_news(source)

    logger.warning("API fetch not implemented for %s", slug)
    return []


def fetch_hacker_news(source):
    """Fetch top stories from Hacker News API."""
    base_url = source["fetch_url"]

    resp = requests.get(f"{base_url}topstories.json", timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    story_ids = resp.json()[:30]  # Top 30 stories

    items = []
    for story_id in story_ids:
        try:
            story_resp = requests.get(f"{base_url}item/{story_id}.json",
                                      timeout=REQUEST_TIMEOUT)
            story_resp.raise_for_status()
            story = story_resp.json()

            if not story or story.get("type") != "story" or not story.get("url"):
                continue

            published = datetime.fromtimestamp(
                story.get("time", 0), tz=timezone.utc
            ).isoformat() if story.get("time") else None

            # Skip items older than MAX_AGE_DAYS
            if published:
                try:
                    pub_dt = datetime.fromisoformat(published)
                    cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)
                    if pub_dt < cutoff:
                        continue
                except (ValueError, TypeError):
                    pass

            items.append({
                "title": story.get("title", "Untitled"),
                "url": story["url"],
                "source_slug": "hacker-news",
                "source_name": source["name"],
                "source_type": "api",
                "published_date": published,
                "content_type": "news_article",
                "raw_text": story.get("title", ""),  # HN stories are links, title is the content
            })
        except Exception as e:
            logger.warning("Failed to fetch HN story %s: %s", story_id, e)

    return items


def extract_entry_text(entry):
    """Extract plain text from an RSS/Atom entry."""
    # Try content first (Atom), then summary (RSS), then description
    content = ""
    if hasattr(entry, "content") and entry.content:
        content = entry.content[0].get("value", "")
    elif hasattr(entry, "summary"):
        content = entry.summary or ""
    elif hasattr(entry, "description"):
        content = entry.description or ""

    if not content:
        return ""

    # Strip HTML tags to get plain text
    soup = BeautifulSoup(content, "html.parser")
    text = soup.get_text(separator="\n", strip=True)

    # Limit length to avoid huge content
    if len(text) > 10000:
        text = text[:10000] + "\n[... truncated]"

    return text
