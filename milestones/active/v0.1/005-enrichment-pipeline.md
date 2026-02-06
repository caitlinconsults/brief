# Enrichment Pipeline -- **IN REFINEMENT**

## WHAT / TO WHOM / WHY

**WHAT**: A processing step that takes raw, normalized content items and adds intelligence — summaries, topic tags, entity extraction, lane affinity scores, embeddings, and topic clustering. This is where Brief stops being a feed reader and starts being an editor.

**TO WHOM**: The ranking engine and digest generator, which need enriched metadata to make good decisions. Also the user, who benefits from accurate topic grouping and lane assignment.

**WHY**: Raw content from 20 sources is noise. Enrichment turns it into signal. Without topic clustering, the digest is 30 unrelated links. Without lane affinity scoring, security content leaks into the builders lane. Without summaries, the user has to click every link to know if it matters.

## Requirements

### Summarization
- Generate a short summary (1-2 sentences) for every content item
- Generate a long summary (paragraph with key points) for items that score above a relevance threshold
- Summaries should capture the "so what" — not just what the content says, but why it matters

### Topic Tagging
- Assign hierarchical topic tags to each item (e.g., `agents > tool-use`, `security > data-leakage`, `business > roi-measurement`)
- Use a consistent taxonomy so topics are comparable across sources and over time
- An item can have multiple topic tags

### Entity Extraction
- Identify companies, products, people, and AI models mentioned in each item
- Normalize entity names (e.g., "OpenAI", "open ai", "Open AI" → `OpenAI`)

### Lane Affinity Scoring
- Score each item's relevance to each of the three lanes (Builders, Security, Business) on a 0.0–1.0 scale
- An item can be relevant to multiple lanes (e.g., an article about deploying agents securely scores high on both Builders and Security)
- Lane scores are influenced by but not solely determined by the source's lane affinity from the registry

### Embeddings
- Generate a vector embedding for each content item
- Embeddings are used for semantic similarity (dedup reinforcement, "more like this") and clustering

### Topic Clustering
- Group content items into topic clusters based on embedding similarity
- Clusters represent "storylines" — a set of items all talking about the same development or theme
- Clusters should be generated daily, with awareness of recent clusters (continuing storylines vs. new ones)
- Target: 5-15 clusters per daily run (not 1 mega-cluster, not 50 micro-clusters)

## Requirements (behavioral)

- Enrichment runs after ingestion completes, as part of the same daily pipeline
- Items that fail enrichment are flagged but don't block other items
- Enrichment is idempotent — running it twice on the same item produces the same result
- **Anthropic Claude** is the LLM used for summarization, topic tagging, entity extraction, and lane scoring (consistent with the rest of the project's tooling)
- Clustering and embedding generation use deterministic or near-deterministic methods

## Success Criteria

- [ ] Every ingested item receives a short summary and topic tags
- [ ] Entities are extracted and normalized across items
- [ ] Lane affinity scores accurately reflect content relevance (spot-check: security articles don't score high on Business lane)
- [ ] Items are grouped into coherent topic clusters (spot-check: items about the same development land in the same cluster)
- [ ] Cluster count per daily run stays in the 5-15 range
- [ ] A single item failing enrichment doesn't block the rest of the pipeline
