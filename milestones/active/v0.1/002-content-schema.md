# Content Schema -- **IN REFINEMENT**

## WHAT / TO WHOM / WHY

**WHAT**: A unified data schema that normalizes content from all sources — regardless of whether it's a podcast episode, blog post, news article, or engineering writeup — into a single structure that downstream processing (enrichment, ranking, digest generation) can operate on uniformly.

**TO WHOM**: Every downstream component. The schema is the contract between ingestion and everything else.

**WHY**: Without normalization, every downstream step has to understand every source format. That's fragile and doesn't scale. A single content object means the enrichment pipeline, ranker, and digest generator each have one interface to work with.

## Requirements

### Core Fields (populated at ingestion)
- **Title**: The content's headline or episode title
- **URL**: Canonical link to the original content
- **Source**: Which of the 20 sources this came from
- **Source type**: `rss`, `api`, `web_scrape`
- **Published date**: When the content was originally published
- **Fetched date**: When Brief ingested it
- **Content type**: `blog_post`, `news_article`, `podcast_episode`, `newsletter`, `engineering_blog`, `report`, `talk`
- **Raw text**: The full text content (or transcript/description for podcasts)
- **Alternate sources**: Other sources that covered the same content (from dedup)

### Enrichment Fields (populated downstream by spec 004)
- **Summary (short)**: 1-2 sentence summary
- **Summary (long)**: Paragraph-length summary with key points
- **Topics**: Hierarchical topic tags (e.g., `agents > planning`, `security > prompt-injection`)
- **Entities**: Companies, products, people, models mentioned
- **Lane affinity scores**: How relevant this item is to each lane (Builders, Security, Business), scored 0.0–1.0
- **Embedding vector**: For semantic similarity and clustering

### Ranking Fields (populated downstream by spec 005)
- **Relevance score**: Final composite score used for digest inclusion
- **Cluster ID**: Which topic cluster this belongs to
- **Novelty flag**: Whether this represents a genuinely new development vs. ongoing coverage

### Metadata
- **Processing status**: `pending_enrichment`, `enriched`, `ranked`, `published`, `archived`

## Storage

The schema is implemented in **SQLite** — a single database file that lives in the project folder. No database server to install or manage. SQLite is more than capable for a single-user daily batch pipeline. If Brief outgrows it later, migrating to Postgres is straightforward because the schema stays the same.

## Requirements (behavioral)

- Every content item from every source can be represented in this schema without loss of essential information
- Fields not available from a given source are nullable (graceful degradation — don't fail because a podcast doesn't have "raw text" the same way a blog does)
- The schema supports querying by date range, source, content type, topic, lane, and cluster
- Schema migrations are handled without data loss

## Success Criteria

- [ ] Content from all 20 sources maps cleanly to the schema
- [ ] No source-specific branching logic is needed downstream of normalization
- [ ] Nullable fields don't cause errors in enrichment, ranking, or digest generation
- [ ] Items can be queried efficiently by any combination of: date, source, type, topic, lane, cluster
