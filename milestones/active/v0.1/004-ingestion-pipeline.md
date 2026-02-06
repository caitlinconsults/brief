# Ingestion Pipeline -- **IN REFINEMENT**

## WHAT / TO WHOM / WHY

**WHAT**: A daily batch job that fetches new content from all enabled sources, extracts relevant metadata, and stores raw content items for downstream processing.

**TO WHOM**: The system — this is the engine that feeds everything else. Also the operator, who needs to know when a source fails and why.

**WHY**: Without reliable ingestion, the digest has nothing to work with. The pipeline must handle flaky sources, rate limits, and varying content formats gracefully. It should be boring and predictable — the "plumbing" that just works.

## Requirements

### Fetching
- Runs on a configurable schedule (default: once daily, early morning)
- Fetches only content published since the last successful fetch per source
- Handles three fetch types: RSS feed parsing, API calls, and web page retrieval
- Respects rate limits and retry policies per source
- Continues processing remaining sources if one source fails (no single point of failure)

### Deduplication
- Detects duplicate content across sources (same story covered by HN, a blog, and a newsletter)
- Deduplication uses URL normalization and title/content similarity
- When duplicates are found, keeps the highest-trust-weight version and links the others as alternate sources

### Storage
- Stores raw content items with source metadata, fetch timestamp, and processing status
- Marks items as "pending enrichment" for the next pipeline stage
- Retains items for a configurable period (default: 90 days) before archiving

### Observability
- Logs fetch success/failure per source per run
- Tracks items ingested per source per run
- Surfaces source health: consecutive failures, degraded response times, or empty results

## Success Criteria

- [ ] All enabled sources are fetched in a single pipeline run
- [ ] Content published since the last fetch is captured; older content is not re-fetched
- [ ] Duplicate content across sources is detected and consolidated
- [ ] A single source failure does not block ingestion from other sources
- [ ] Fetch results (success, failure, item count) are logged per source per run
- [ ] Raw content items are stored with enough metadata to trace back to the original source and URL
