"""Database schema and operations for Brief (spec 002)."""

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


DB_PATH = Path(__file__).parent.parent / "brief.db"


def get_connection(db_path=None):
    conn = sqlite3.connect(str(db_path or DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS content_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            source_slug TEXT NOT NULL,
            source_name TEXT NOT NULL,
            source_type TEXT NOT NULL,
            published_date TEXT,
            fetched_date TEXT NOT NULL,
            content_type TEXT,
            raw_text TEXT,
            alternate_sources TEXT DEFAULT '[]',

            summary_short TEXT,
            summary_long TEXT,
            topics TEXT DEFAULT '[]',
            entities TEXT DEFAULT '[]',
            lane_builders REAL DEFAULT 0.0,
            lane_security REAL DEFAULT 0.0,
            lane_business REAL DEFAULT 0.0,

            relevance_score REAL,
            cluster_id INTEGER,
            novelty_flag INTEGER DEFAULT 0,

            processing_status TEXT DEFAULT 'pending_enrichment',
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS pipeline_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_date TEXT NOT NULL,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            status TEXT DEFAULT 'running',
            items_ingested INTEGER DEFAULT 0,
            items_enriched INTEGER DEFAULT 0,
            items_selected INTEGER DEFAULT 0,
            error_message TEXT
        );

        CREATE TABLE IF NOT EXISTS source_health (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_slug TEXT NOT NULL,
            run_date TEXT NOT NULL,
            status TEXT NOT NULL,
            items_fetched INTEGER DEFAULT 0,
            error_message TEXT,
            response_time_ms INTEGER
        );

        CREATE TABLE IF NOT EXISTS digest_deliveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_date TEXT NOT NULL UNIQUE,
            file_path TEXT NOT NULL,
            delivered_at TEXT NOT NULL,
            opened INTEGER DEFAULT 0
        );

        CREATE INDEX IF NOT EXISTS idx_items_status ON content_items(processing_status);
        CREATE INDEX IF NOT EXISTS idx_items_source ON content_items(source_slug);
        CREATE INDEX IF NOT EXISTS idx_items_date ON content_items(fetched_date);
        CREATE INDEX IF NOT EXISTS idx_items_cluster ON content_items(cluster_id);
    """)
    conn.commit()


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def insert_item(conn, item):
    try:
        conn.execute("""
            INSERT INTO content_items
                (title, url, source_slug, source_name, source_type,
                 published_date, fetched_date, content_type, raw_text,
                 processing_status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending_enrichment', ?)
        """, (
            item["title"], item["url"], item["source_slug"],
            item["source_name"], item["source_type"],
            item.get("published_date"), now_iso(),
            item.get("content_type"), item.get("raw_text"),
            now_iso()
        ))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # duplicate URL


def get_pending_enrichment(conn):
    rows = conn.execute(
        "SELECT * FROM content_items WHERE processing_status = 'pending_enrichment'"
    ).fetchall()
    return [dict(r) for r in rows]


def update_enrichment(conn, item_id, enrichment):
    conn.execute("""
        UPDATE content_items SET
            summary_short = ?,
            summary_long = ?,
            topics = ?,
            entities = ?,
            lane_builders = ?,
            lane_security = ?,
            lane_business = ?,
            processing_status = 'enriched'
        WHERE id = ?
    """, (
        enrichment["summary_short"],
        enrichment["summary_long"],
        json.dumps(enrichment["topics"]),
        json.dumps(enrichment["entities"]),
        enrichment["lane_builders"],
        enrichment["lane_security"],
        enrichment["lane_business"],
        item_id
    ))
    conn.commit()


def get_enriched_items(conn, run_date):
    rows = conn.execute("""
        SELECT * FROM content_items
        WHERE processing_status = 'enriched'
        AND date(fetched_date) = date(?)
    """, (run_date,)).fetchall()
    return [dict(r) for r in rows]


def get_all_enriched(conn):
    rows = conn.execute("""
        SELECT * FROM content_items
        WHERE processing_status IN ('enriched', 'ranked', 'published')
    """).fetchall()
    return [dict(r) for r in rows]


def update_ranking(conn, item_id, score, cluster_id, novelty):
    conn.execute("""
        UPDATE content_items SET
            relevance_score = ?,
            cluster_id = ?,
            novelty_flag = ?,
            processing_status = 'ranked'
        WHERE id = ?
    """, (score, cluster_id, int(novelty), item_id))
    conn.commit()


def mark_published(conn, item_ids):
    placeholders = ",".join("?" for _ in item_ids)
    conn.execute(
        f"UPDATE content_items SET processing_status = 'published' WHERE id IN ({placeholders})",
        item_ids
    )
    conn.commit()


def start_pipeline_run(conn, run_date):
    conn.execute(
        "INSERT INTO pipeline_runs (run_date, started_at) VALUES (?, ?)",
        (run_date, now_iso())
    )
    conn.commit()
    return conn.execute("SELECT last_insert_rowid()").fetchone()[0]


def update_pipeline_run(conn, run_id, **kwargs):
    sets = []
    vals = []
    for k, v in kwargs.items():
        sets.append(f"{k} = ?")
        vals.append(v)
    vals.append(run_id)
    conn.execute(
        f"UPDATE pipeline_runs SET {', '.join(sets)} WHERE id = ?", vals
    )
    conn.commit()


def log_source_health(conn, source_slug, run_date, status, items_fetched=0,
                       error_message=None, response_time_ms=None):
    conn.execute("""
        INSERT INTO source_health
            (source_slug, run_date, status, items_fetched, error_message, response_time_ms)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (source_slug, run_date, status, items_fetched, error_message, response_time_ms))
    conn.commit()


def record_delivery(conn, run_date, file_path):
    try:
        conn.execute(
            "INSERT INTO digest_deliveries (run_date, file_path, delivered_at) VALUES (?, ?, ?)",
            (run_date, str(file_path), now_iso())
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # already delivered for this date


def is_delivered_today(conn, run_date):
    row = conn.execute(
        "SELECT id FROM digest_deliveries WHERE run_date = ?", (run_date,)
    ).fetchone()
    return row is not None


def get_last_fetch_date(conn, source_slug):
    row = conn.execute("""
        SELECT MAX(fetched_date) as last_fetch
        FROM content_items WHERE source_slug = ?
    """, (source_slug,)).fetchone()
    return row["last_fetch"] if row and row["last_fetch"] else None
