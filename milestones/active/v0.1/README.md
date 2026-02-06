# v0.1: MVP — The Daily Brief

**Status**: IN REFINEMENT

## WHAT / TO WHOM / WHY

**WHAT**: A daily content curation pipeline that ingests from 20 curated sources, organizes content into topic clusters, and produces a 3-lane digest (Builders, Security, Business) delivered to the user each morning.

**TO WHOM**: An AI-curious strategist who wants to stay on the cutting edge of AI developments — specifically around agent projects, AI security, and real-world business implementations — without manually monitoring dozens of sources.

**WHY**: Staying current across AI builders, security, and business implementation requires monitoring ~20 disparate sources daily. Manual curation is unsustainable. A daily automated digest with smart ranking ensures nothing important is missed, and the 3-lane structure provides strategist-grade output that separates "people experimenting" from "teams productizing" from "executives deciding."

## Technical Decisions

These were settled during spec refinement:

- **LLM**: Anthropic Claude (used for enrichment — summarization, topic tagging, entity extraction, lane scoring)
- **Database**: SQLite (single file, local, simple — can migrate to Postgres later if needed)
- **Hosting**: Cron job on local Mac (laptop generally stays open; a wake/keep-awake mechanism handles the schedule)
- **Delivery**: File-based — the digest is written as a formatted file to a local folder and opens automatically when you next use your Mac (no email service needed for MVP)
- **MVP start**: One source first (Simon Willison's Weblog) to prove the pipeline end-to-end, then add remaining sources incrementally

## MVP Scope

1. 20 curated sources (starting with 1 to prove the pipeline, then scaling up)
2. SQLite database + embeddings
3. One daily job: ingest → dedupe → cluster → rank → generate 3-lane digest
4. File-based delivery — digest saved locally and auto-opened
5. **Deferred to post-MVP**: feedback buttons, real-time alerts, academic papers, richer personalization

## Requirements

- Runs as a single daily batch job (not real-time), triggered by a Mac cron job
- Starts with Simon Willison's Weblog; scales to all 20 sources incrementally
- Deduplicates content across sources (matters once multiple sources are active)
- Groups content into topic clusters
- Ranks content by relevance, recency, and source trust
- Produces a digest with three parallel lanes per topic cluster:
  - **Builders**: What shipped, what broke, who's experimenting
  - **Security**: What failed, threat models, safety developments
  - **Business**: Who deployed what, ROI signals, operating models
- Includes direct links to source material for deeper reading
- Delivers the digest as a formatted file saved to a local folder, auto-opened on next login
- System degrades gracefully if a source is temporarily unavailable

## Success Criteria

- [ ] Pipeline runs end-to-end with Simon Willison's Weblog as the first source
- [ ] Content is deduplicated (same story from multiple sources appears once)
- [ ] Content is grouped into coherent topic clusters
- [ ] Each cluster produces a Builders, Security, and/or Business summary (not all clusters will have all three lanes)
- [ ] Digest includes clickable links to original content
- [ ] Digest is delivered via email at the configured time each morning
- [ ] System degrades gracefully if a source is temporarily unavailable
- [ ] Additional sources can be added by editing the source registry file

## Specs

- [ ] 001: Source registry
- [ ] 002: Content schema
- [ ] 003: Security and containment
- [ ] 004: Ingestion pipeline
- [ ] 005: Enrichment pipeline
- [ ] 006: Ranking and selection
- [ ] 007: Digest generation
- [ ] 008: Delivery
- [ ] 009: System scheduling
